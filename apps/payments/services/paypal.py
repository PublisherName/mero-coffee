import logging
import uuid
from typing import Any

import django.db.transaction as db_tx
from django.conf import settings
from django.urls import reverse
from paypalserversdk.configuration import Environment
from paypalserversdk.http.auth.o_auth_2 import ClientCredentialsAuthCredentials
from paypalserversdk.logging.configuration.api_logging_configuration import (
    LoggingConfiguration,
    RequestLoggingConfiguration,
    ResponseLoggingConfiguration,
)
from paypalserversdk.models.amount_with_breakdown import AmountWithBreakdown
from paypalserversdk.models.checkout_payment_intent import CheckoutPaymentIntent
from paypalserversdk.models.order_application_context import OrderApplicationContext
from paypalserversdk.models.order_application_context_user_action import (
    OrderApplicationContextUserAction,
)
from paypalserversdk.models.order_request import OrderRequest
from paypalserversdk.models.purchase_unit_request import PurchaseUnitRequest
from paypalserversdk.paypal_serversdk_client import PaypalServersdkClient

from apps.emails.models import EmailTemplate
from apps.emails.services import EmailService
from apps.payments.enums import PaymentLogStatus, PaymentMethods, SupportTransactionStatus
from apps.payments.models import PaymentGateway, PaymentLog, SupportTransaction
from apps.payments.services.exceptions import (
    PayPalCaptureError,
    PayPalOrderCreationError,
    PayPalOrderFetchError,
    PayPalTransactionNotFoundError,
)
from apps.payments.services.strategy import PaymentStrategy

logger = logging.getLogger(__name__)


class PayPalStrategy(PaymentStrategy):
    """PayPal payment logic using paypal-server-sdk 2.1.0"""

    # TODO: Implement live exchange rate in production
    NPR_TO_USD_RATE = 135

    @staticmethod
    def _get_client(gateway: PaymentGateway) -> PaypalServersdkClient:
        environment = Environment.SANDBOX if gateway.is_sandbox else Environment.PRODUCTION

        client = PaypalServersdkClient(
            client_credentials_auth_credentials=ClientCredentialsAuthCredentials(
                o_auth_client_id=gateway.merchant_id,
                o_auth_client_secret=gateway.secret_key,
            ),
            environment=environment,
            logging_configuration=LoggingConfiguration(
                log_level=logging.ERROR if settings.IS_SERVER_SECURE else logging.DEBUG,
                request_logging_config=RequestLoggingConfiguration(
                    log_body=not settings.IS_SERVER_SECURE
                ),
                response_logging_config=ResponseLoggingConfiguration(
                    log_headers=not settings.IS_SERVER_SECURE
                ),
            ),
        )
        return client

    @staticmethod
    def _fetch_paypal_order(client: PaypalServersdkClient, token: str):
        try:
            get_order_response = client.orders.get_order({"id": token})

            if get_order_response.is_error():
                error_msg = (
                    str(get_order_response.body)
                    if hasattr(get_order_response, "body")
                    else "Unknown error"
                )
                logger.error(
                    f"Failed to fetch PayPal order {token}: {error_msg}",
                    extra={"token": token, "error": error_msg},
                )
                raise PayPalOrderFetchError(f"Failed to retrieve order details: {error_msg}")

            return get_order_response.body

        except PayPalOrderFetchError:
            raise
        except Exception as e:
            logger.exception(
                f"Unexpected error fetching PayPal order {token}",
                extra={"token": token},
            )
            raise PayPalOrderFetchError(f"Order retrieval error: {e!s}") from e

    @staticmethod
    def _extract_transaction_id(order) -> str | None:
        if (
            hasattr(order, "purchase_units")
            and order.purchase_units
            and len(order.purchase_units) > 0
        ):
            unit = order.purchase_units[0]
            if hasattr(unit, "reference_id"):
                return unit.reference_id
        return None

    @staticmethod
    def _get_transaction_from_order(order) -> SupportTransaction:
        transaction_id = PayPalStrategy._extract_transaction_id(order)

        if not transaction_id:
            order_id = getattr(order, "id", "unknown")
            logger.error(
                f"No transaction ID in PayPal order {order_id}", extra={"order_id": order_id}
            )
            raise PayPalTransactionNotFoundError("No transaction ID found in PayPal order")

        transaction = (
            SupportTransaction.objects.select_for_update()
            .filter(transaction_id=transaction_id)
            .first()
        )

        if not transaction:
            logger.error(
                f"No transaction found for ID: {transaction_id}",
                extra={"transaction_id": transaction_id},
            )
            raise PayPalTransactionNotFoundError(
                f"No pending transaction found for ID: {transaction_id}"
            )

        return transaction

    @staticmethod
    def _extract_capture_details(capture_result) -> tuple[str | None, str | None]:
        capture_id = None
        captured_amount = None

        if (
            hasattr(capture_result, "purchase_units")
            and capture_result.purchase_units
            and len(capture_result.purchase_units) > 0
        ):
            unit = capture_result.purchase_units[0]
            if (
                hasattr(unit, "payments")
                and unit.payments
                and hasattr(unit.payments, "captures")
                and unit.payments.captures
            ):
                capture = unit.payments.captures[0]
                capture_id = capture.id if hasattr(capture, "id") else None
                if hasattr(capture, "amount") and hasattr(capture.amount, "value"):
                    captured_amount = capture.amount.value

        return capture_id, captured_amount

    @staticmethod
    def _create_payment_log(
        transaction: SupportTransaction,
        status: str,
        request_payload: dict[str, Any],
        response_payload: dict[str, Any],
    ) -> PaymentLog:
        return PaymentLog.objects.create(
            transaction=transaction,
            payment_method=PaymentMethods.PAYPAL,
            request_payload=request_payload,
            response_payload=response_payload,
            status=status,
        )

    @staticmethod
    def _send_success_email(transaction: SupportTransaction) -> None:
        try:
            EmailService.send_template_email(
                template_name=EmailTemplate.Type.PAYMENT_SUCCESS_CREATOR,
                recipient=transaction.creator.user.email,
                context={
                    "creator_name": transaction.creator.display_name
                    or transaction.creator.user.username,
                    "supporter_name": transaction.supporter_name,
                    "amount": transaction.amount,
                    "message": transaction.message,
                    "creator_dashboard_url": settings.SITE_BASE_URL.rstrip("/")
                    + reverse("dashboard:dashboard"),
                },
            )
        except Exception:
            logger.exception(
                f"Failed to send success email for transaction {transaction.transaction_id}",
                extra={"transaction_id": transaction.transaction_id},
            )

    @staticmethod
    def _mark_transaction_completed(
        transaction: SupportTransaction, token: str, order, capture_result
    ) -> None:
        if transaction.payment_status == SupportTransactionStatus.COMPLETED:
            logger.info(
                f"Transaction {transaction.transaction_id} already completed",
                extra={"transaction_id": transaction.transaction_id},
            )
            return

        transaction.payment_status = SupportTransactionStatus.COMPLETED
        transaction.save(update_fields=["payment_status"])

        capture_id, captured_amount = PayPalStrategy._extract_capture_details(capture_result)

        safe_payload = {
            "order_id": order.id if hasattr(order, "id") else None,
            "capture_id": capture_id,
            "status": capture_result.status if hasattr(capture_result, "status") else None,
            "amount": captured_amount,
        }

        existing_log = PaymentLog.objects.filter(
            transaction=transaction, status=PaymentLogStatus.PAYPAL_PAYMENT_CAPTURED
        ).exists()

        if not existing_log:
            PayPalStrategy._create_payment_log(
                transaction=transaction,
                status=PaymentLogStatus.PAYPAL_PAYMENT_CAPTURED,
                request_payload={"token": token},
                response_payload=safe_payload,
            )
            PayPalStrategy._send_success_email(transaction)
        else:
            logger.info(
                f"Payment log already exists for transaction {transaction.transaction_id}",
                extra={"transaction_id": transaction.transaction_id},
            )

    @staticmethod
    def _mark_transaction_failed(
        transaction: SupportTransaction,
        token: str,
        order,
        error_response,
        reason: str = "capture_failed",
    ) -> None:
        if transaction.payment_status == SupportTransactionStatus.FAILED:
            logger.info(
                f"Transaction {transaction.transaction_id} already marked as failed",
                extra={"transaction_id": transaction.transaction_id},
            )
            return

        transaction.payment_status = SupportTransactionStatus.FAILED
        transaction.save(update_fields=["payment_status"])

        safe_payload = {
            "order_id": order.id if hasattr(order, "id") else None,
            "status": order.status if hasattr(order, "status") else None,
            "error": str(error_response.body)
            if hasattr(error_response, "body")
            else str(error_response),
            "reason": reason,
        }

        status = (
            PaymentLogStatus.PAYPAL_PAYMENT_NOT_CAPTURED
            if reason == "capture_failed"
            else PaymentLogStatus.CANCELLED
        )

        PayPalStrategy._create_payment_log(
            transaction=transaction,
            status=status,
            request_payload={"token": token},
            response_payload=safe_payload,
        )

    @staticmethod
    def _capture_payment(
        client: PaypalServersdkClient,
        token: str,
        order,
        transaction: SupportTransaction,
        gateway: PaymentGateway,
    ) -> tuple[str, dict[str, Any]]:
        if transaction.payment_status == SupportTransactionStatus.COMPLETED:
            logger.info(
                f"Transaction {transaction.transaction_id} already completed, skipping capture",
                extra={"transaction_id": transaction.transaction_id, "token": token},
            )
            return "payment_success.html", {
                "transaction": transaction,
                "gateway": gateway,
                "payment_data": {"order_id": order.id if hasattr(order, "id") else None},
            }

        order_status = order.status if hasattr(order, "status") else None

        if order_status == SupportTransactionStatus.COMPLETED.upper():
            logger.info(
                f"PayPal order {token} already captured, updating transaction status",
                extra={"token": token, "transaction_id": transaction.transaction_id},
            )
            PayPalStrategy._mark_transaction_completed(transaction, token, order, order)

            return "payment_success.html", {
                "transaction": transaction,
                "gateway": gateway,
                "payment_data": {"order_id": order.id if hasattr(order, "id") else None},
            }

        try:
            capture_response = client.orders.capture_order({"id": token})

            if capture_response.status_code == 201 and capture_response.body:
                PayPalStrategy._mark_transaction_completed(
                    transaction, token, order, capture_response.body
                )

                return "payment_success.html", {
                    "transaction": transaction,
                    "gateway": gateway,
                    "payment_data": {"order_id": order.id if hasattr(order, "id") else None},
                }
            else:
                PayPalStrategy._mark_transaction_failed(
                    transaction, token, order, capture_response, reason="capture_failed"
                )
                raise PayPalCaptureError("Payment capture failed")

        except PayPalCaptureError:
            raise
        except Exception as e:
            error_msg = str(e).lower()
            if "already" in error_msg and "captured" in error_msg:
                logger.info(
                    f"Order {token} already captured (from error), fetching updated order",
                    extra={"token": token},
                )

                updated_order = PayPalStrategy._fetch_paypal_order(client, token)

                if (
                    hasattr(updated_order, "status")
                    and updated_order.status == SupportTransactionStatus.COMPLETED.upper()
                ):
                    PayPalStrategy._mark_transaction_completed(
                        transaction, token, updated_order, updated_order
                    )

                    return "payment_success.html", {
                        "transaction": transaction,
                        "gateway": gateway,
                        "payment_data": {
                            "order_id": updated_order.id if hasattr(updated_order, "id") else None
                        },
                    }

            logger.exception(
                f"Unexpected error during payment capture for token {token}",
                extra={"token": token, "transaction_id": transaction.transaction_id},
            )
            raise PayPalCaptureError(f"Capture error: {e!s}") from e

    @classmethod
    def get_payment_context(cls, transaction: SupportTransaction, request=None) -> dict[str, Any]:
        try:
            gateway = PaymentGateway.objects.get(slug=PaymentMethods.PAYPAL)
        except PaymentGateway.DoesNotExist:
            logger.error("PayPal gateway not configured")
            return {
                "error": "Payment gateway not configured. Please contact support.",
                "transaction": transaction,
            }

        if not transaction.transaction_id:
            transaction.transaction_id = uuid.uuid4().hex
            transaction.save(update_fields=["transaction_id"])

        if request:
            success_url = request.build_absolute_uri(reverse("payments:paypal_success"))
            cancel_url = request.build_absolute_uri(reverse("payments:paypal_cancel"))
        else:
            success_url = gateway.success_url
            cancel_url = gateway.failure_url

        try:
            client = cls._get_client(gateway)
            amount_usd = transaction.amount / cls.NPR_TO_USD_RATE

            response = client.orders.create_order(
                {
                    "body": OrderRequest(
                        intent=CheckoutPaymentIntent.CAPTURE,
                        purchase_units=[
                            PurchaseUnitRequest(
                                reference_id=transaction.transaction_id,
                                amount=AmountWithBreakdown(
                                    currency_code="USD",
                                    value=f"{amount_usd:.2f}",
                                ),
                                description=f"Support for {
                                    transaction.creator.display_name
                                    or transaction.creator.user.username
                                }",
                            )
                        ],
                        application_context=OrderApplicationContext(
                            return_url=success_url,
                            cancel_url=cancel_url,
                            user_action=OrderApplicationContextUserAction.PAY_NOW,
                        ),
                    ),
                    "prefer": "return=minimal",
                }
            )

            if response.is_success():
                order = response.body
                approval_url = next(
                    (link.href for link in order.links if link.rel == "approve"), None
                )

                if not approval_url:
                    logger.error(
                        f"No approval URL in PayPal order {order.id}",
                        extra={"order_id": order.id, "transaction_id": transaction.transaction_id},
                    )
                    raise PayPalOrderCreationError("No approval URL found in order response")

                cls._create_payment_log(
                    transaction=transaction,
                    status=PaymentLogStatus.PAYPAL_ORDER_CREATED,
                    request_payload={
                        "amount": transaction.amount,
                        "currency": "USD",
                        "transaction_id": transaction.transaction_id,
                    },
                    response_payload={"order_id": order.id, "status": order.status},
                )

                return {
                    "payment_url": approval_url,
                    "payment_params": {"token": order.id},
                    "method": "GET",
                }
            else:
                error_msg = str(response.body) if hasattr(response, "body") else str(response)
                logger.error(
                    f"PayPal order creation failed: {response.status_code} - {error_msg}",
                    extra={
                        "status_code": response.status_code,
                        "transaction_id": transaction.transaction_id,
                    },
                )

                cls._create_payment_log(
                    transaction=transaction,
                    status=PaymentLogStatus.PAYPAL_ORDER_CREATION_FAILED,
                    request_payload={
                        "amount": transaction.amount,
                        "transaction_id": transaction.transaction_id,
                    },
                    response_payload={"error": error_msg, "status_code": response.status_code},
                )

                raise PayPalOrderCreationError(f"Order creation failed: {error_msg}")

        except PayPalOrderCreationError:
            return {
                "error": "Payment setup failed. Please try again or contact support.",
                "transaction": transaction,
            }
        except Exception as e:
            logger.exception(
                f"Unexpected error creating PayPal order for tx {transaction.transaction_id}",
                extra={"transaction_id": transaction.transaction_id},
            )

            cls._create_payment_log(
                transaction=transaction,
                status=PaymentLogStatus.PAYPAL_ORDER_CREATION_FAILED,
                request_payload={
                    "amount": transaction.amount,
                    "transaction_id": transaction.transaction_id,
                },
                response_payload={"error": str(e)},
            )

            return {
                "error": "Payment setup failed. Please try again or contact support.",
                "transaction": transaction,
            }

    @staticmethod
    def handle_success(token: str) -> tuple[str, dict[str, Any]]:
        try:
            gateway = PaymentGateway.objects.get(slug=PaymentMethods.PAYPAL)
        except PaymentGateway.DoesNotExist:
            logger.error("PayPal gateway not configured")
            return "payment_failed.html", {
                "error": "Payment gateway configuration error. Please contact support."
            }

        try:
            with db_tx.atomic():
                client = PayPalStrategy._get_client(gateway)
                order = PayPalStrategy._fetch_paypal_order(client, token)
                transaction = PayPalStrategy._get_transaction_from_order(order)
                return PayPalStrategy._capture_payment(client, token, order, transaction, gateway)

        except PayPalOrderFetchError as e:
            logger.error(f"Order fetch error for token {token}: {e!s}", extra={"token": token})
            return "payment_failed.html", {"error": "Failed to retrieve order details"}

        except PayPalTransactionNotFoundError as e:
            logger.error(f"Transaction not found for token {token}: {e!s}", extra={"token": token})
            return "payment_failed.html", {"error": "No pending transaction found"}

        except PayPalCaptureError as e:
            logger.error(f"Capture error for token {token}: {e!s}", extra={"token": token})
            return "payment_failed.html", {"error": "Payment capture failed"}

        except Exception:
            logger.exception(
                f"Unexpected error in handle_success for token {token}",
                extra={"token": token},
            )
            return "payment_failed.html", {
                "error": "Payment verification failed. Please contact support."
            }

    @staticmethod
    def handle_cancel(token: str) -> tuple[str, dict[str, Any]]:
        context = {"error": "Payment was cancelled"}

        try:
            gateway = PaymentGateway.objects.get(slug=PaymentMethods.PAYPAL)
        except PaymentGateway.DoesNotExist:
            logger.error("PayPal gateway not configured")
            return "payment_failed.html", context

        try:
            with db_tx.atomic():
                client = PayPalStrategy._get_client(gateway)
                order = PayPalStrategy._fetch_paypal_order(client, token)
                transaction = PayPalStrategy._get_transaction_from_order(order)

                PayPalStrategy._mark_transaction_failed(
                    transaction, token, order, order, reason="cancelled"
                )

                context["transaction"] = transaction

        except (PayPalOrderFetchError, PayPalTransactionNotFoundError) as e:
            logger.warning(
                f"Error in handle_cancel for token {token}: {e!s}", extra={"token": token}
            )

        except Exception:
            logger.exception(
                f"Unexpected error in handle_cancel for token {token}",
                extra={"token": token},
            )

        return "payment_failed.html", context
