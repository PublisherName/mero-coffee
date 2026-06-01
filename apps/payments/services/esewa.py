import base64
import hashlib
import hmac
import json
import logging
import uuid
from typing import Any

import requests
from django.conf import settings
from django.urls import reverse

from apps.emails.models import EmailTemplate
from apps.emails.services import EmailService
from apps.payments.enums import PaymentLogStatus, PaymentMethods, SupportTransactionStatus
from apps.payments.models import PaymentGateway, PaymentLog, SupportTransaction
from apps.payments.services.strategy import PaymentStrategy

logger = logging.getLogger(__name__)


class EsewaStrategy(PaymentStrategy):
    GATEWAY_SLUG = PaymentMethods.ESEWA
    REQUEST_TIMEOUT = 10

    STATUS_COMPLETE = "COMPLETE"
    STATUS_PENDING = "PENDING"
    STATUS_ERROR = "ERROR"
    STATUS_AMBIGUOUS = "AMBIGUOUS"
    STATUS_NOT_FOUND = "NOT_FOUND"
    STATUS_CANCELED = "CANCELED"
    STATUS_FULL_REFUND = "FULL_REFUND"
    STATUS_PARTIAL_REFUND = "PARTIAL_REFUND"

    SIGNED_FIELDS = "total_amount,transaction_uuid,product_code"

    @staticmethod
    def _get_gateway() -> PaymentGateway | None:
        try:
            return PaymentGateway.objects.get(slug=EsewaStrategy.GATEWAY_SLUG)
        except PaymentGateway.DoesNotExist:
            logger.error("eSewa payment gateway not configured")
            return None

    @staticmethod
    def _generate_signature(secret: str, message: str) -> str:
        hmac_sha256 = hmac.new(secret.encode(), message.encode(), hashlib.sha256)
        digest = hmac_sha256.digest()
        return base64.b64encode(digest).decode("utf-8")

    @staticmethod
    def _create_payment_log(
        transaction: SupportTransaction,
        request_payload: dict,
        response_payload: dict,
        status: str,
    ) -> PaymentLog:
        return PaymentLog.objects.create(
            transaction=transaction,
            payment_method=EsewaStrategy.GATEWAY_SLUG,
            request_payload=request_payload,
            response_payload=response_payload,
            status=status,
        )

    @staticmethod
    def _mark_transaction_failed(
        transaction: SupportTransaction,
        response_data: dict,
        log_status: str,
    ) -> None:
        if transaction.payment_status != SupportTransactionStatus.FAILED:
            transaction.payment_status = SupportTransactionStatus.FAILED
            transaction.save(update_fields=["payment_status"])

        EsewaStrategy._create_payment_log(
            transaction=transaction,
            request_payload={},
            response_payload=response_data,
            status=log_status,
        )

    @staticmethod
    def _mark_transaction_completed(
        transaction: SupportTransaction,
        response_data: dict,
    ) -> None:
        if transaction.payment_status == SupportTransactionStatus.COMPLETED:
            return

        transaction.payment_status = SupportTransactionStatus.COMPLETED
        transaction.save(update_fields=["payment_status"])

        EsewaStrategy._create_payment_log(
            transaction=transaction,
            request_payload={},
            response_payload=response_data,
            status=PaymentLogStatus.SUCCESS,
        )

        EsewaStrategy._send_success_email(transaction)

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
            logger.exception("Failed to send success email")

    def verify_signature(
        self,
        data: dict,
        gateway: PaymentGateway,
        transaction: SupportTransaction,
    ) -> bool:
        signed_field_names = data.get("signed_field_names", "")
        signature = data.get("signature")

        if not signature or not signed_field_names:
            logger.warning(
                f"Missing signature fields for transaction {transaction.transaction_id}"
            )
            self._mark_transaction_failed(
                transaction=transaction,
                response_data=data,
                log_status=PaymentLogStatus.SIGNATURE_MISMATCH,
            )
            return False

        message_parts = []
        for field in signed_field_names.split(","):
            field_value = data.get(field, "")
            message_parts.append(f"{field}={field_value}")
        message = ",".join(message_parts)

        expected_signature = self._generate_signature(gateway.secret_key, message)

        if signature != expected_signature:
            logger.warning(
                f"Signature mismatch for transaction {transaction.transaction_id}: "
                f"expected={expected_signature[:10]}..., got={signature[:10]}..."
            )
            self._mark_transaction_failed(
                transaction=transaction,
                response_data=data,
                log_status=PaymentLogStatus.SIGNATURE_MISMATCH,
            )
            return False

        return True

    @staticmethod
    def verify_payment(
        transaction: SupportTransaction,
    ) -> tuple[dict | None, str | None]:
        gateway = EsewaStrategy._get_gateway()
        if not gateway:
            return None, "Payment gateway not configured"

        base_url = gateway.sandbox_url if gateway.is_sandbox else gateway.base_url
        status_url = f"{base_url}/transaction/status/"

        params = {
            "product_code": gateway.merchant_id.strip(),
            "total_amount": float(transaction.amount),
            "transaction_uuid": transaction.transaction_id,
        }

        try:
            response = requests.get(
                status_url,
                params=params,
                timeout=EsewaStrategy.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            api_response = response.json()
            api_status = api_response.get("status")

            status_map = {
                EsewaStrategy.STATUS_COMPLETE: PaymentLogStatus.API_COMPLETE,
                EsewaStrategy.STATUS_PENDING: PaymentLogStatus.API_PENDING,
                EsewaStrategy.STATUS_ERROR: PaymentLogStatus.API_ERROR,
            }
            log_status = status_map.get(api_status, PaymentLogStatus.API_UNKNOWN)

            EsewaStrategy._create_payment_log(
                transaction=transaction,
                request_payload={"action": "double_verification", "params": params},
                response_payload=api_response,
                status=log_status,
            )

            if api_status != EsewaStrategy.STATUS_COMPLETE:
                return None, f"Payment verification failed (Status: {api_status})"

            return api_response, None

        except requests.Timeout:
            logger.error(f"Timeout verifying payment for {transaction.transaction_id}")
            error_msg = "Payment verification timed out"
            error_detail = error_msg
        except requests.RequestException as e:
            logger.exception(
                f"Request error verifying payment for {transaction.transaction_id}",
            )
            error_msg = "Payment verification failed"
            error_detail = str(e)
        except Exception as e:
            logger.exception(
                f"Unexpected error verifying payment for {transaction.transaction_id}",
            )
            error_msg = "An unexpected error occurred"
            error_detail = str(e)

        EsewaStrategy._create_payment_log(
            transaction=transaction,
            request_payload={"action": "double_verification_failed"},
            response_payload={"error": error_detail},
            status=PaymentLogStatus.API_ERROR,
        )

        return None, f"{error_msg}. Please contact support."

    @staticmethod
    def handle_status(
        transaction: SupportTransaction,
        gateway: PaymentGateway,
        data: dict,
        ref_id: str | None,
    ) -> tuple[str, dict]:
        status = data.get("status")
        transaction_code = data.get("transaction_code")

        if status == EsewaStrategy.STATUS_COMPLETE:
            EsewaStrategy._mark_transaction_completed(transaction, data)

            context = {
                "transaction": transaction,
                "gateway": gateway,
                "payment_data": data,
                "transaction_code": transaction_code,
                "ref_id": ref_id,
            }
            return "payment_success.html", context

        if status == EsewaStrategy.STATUS_PENDING:
            EsewaStrategy._create_payment_log(
                transaction=transaction,
                request_payload={},
                response_payload=data,
                status=PaymentLogStatus.PENDING,
            )
            return "payment_failed.html", {
                "error": "Payment is still pending. Please wait for confirmation.",
                "transaction": transaction,
            }

        if status in [EsewaStrategy.STATUS_FULL_REFUND, EsewaStrategy.STATUS_PARTIAL_REFUND]:
            refund_status_map = {
                EsewaStrategy.STATUS_FULL_REFUND: PaymentLogStatus.FULL_REFUND,
                EsewaStrategy.STATUS_PARTIAL_REFUND: PaymentLogStatus.PARTIAL_REFUND,
            }
            log_status = refund_status_map[status]

            EsewaStrategy._mark_transaction_failed(transaction, data, log_status)

            return "payment_failed.html", {
                "error": f"Payment was refunded ({status.replace('_', ' ').title()})",
                "transaction": transaction,
            }

        if status == EsewaStrategy.STATUS_AMBIGUOUS:
            EsewaStrategy._create_payment_log(
                transaction=transaction,
                request_payload={},
                response_payload=data,
                status=PaymentLogStatus.AMBIGUOUS,
            )
            return "payment_failed.html", {
                "error": "Payment status is unclear. Please contact support.",
                "transaction": transaction,
            }

        if status in [EsewaStrategy.STATUS_NOT_FOUND, EsewaStrategy.STATUS_CANCELED]:
            failure_status_map = {
                EsewaStrategy.STATUS_NOT_FOUND: PaymentLogStatus.NOT_FOUND,
                EsewaStrategy.STATUS_CANCELED: PaymentLogStatus.CANCELED,
            }
            log_status = failure_status_map[status]

            EsewaStrategy._mark_transaction_failed(transaction, data, log_status)

            error_msg = (
                "Payment session expired"
                if status == EsewaStrategy.STATUS_NOT_FOUND
                else "Payment was cancelled"
            )
            return "payment_failed.html", {
                "error": error_msg,
                "transaction": transaction,
            }

        logger.warning(
            f"Unknown eSewa status '{status}' for transaction {transaction.transaction_id}"
        )
        EsewaStrategy._create_payment_log(
            transaction=transaction,
            request_payload={},
            response_payload=data,
            status=PaymentLogStatus.UNKNOWN_STATUS,
        )
        return "payment_failed.html", {
            "error": f"Unknown payment status: {status}",
            "transaction": transaction,
        }

    def get_payment_context(
        self,
        transaction: SupportTransaction,
        request=None,
    ) -> dict[str, Any]:
        gateway = self._get_gateway()
        if not gateway:
            return {
                "error": "Payment gateway not configured",
                "transaction": transaction,
            }

        if not transaction.transaction_id:
            transaction.transaction_id = uuid.uuid4().hex
            transaction.save(update_fields=["transaction_id"])

        amount = f"{transaction.amount:.2f}"
        tax_amount = "0.00"
        total_amount = f"{transaction.amount:.2f}"
        transaction_uuid = transaction.transaction_id
        product_code = gateway.merchant_id.strip()

        message = (
            f"total_amount={total_amount},"
            f"transaction_uuid={transaction_uuid},"
            f"product_code={product_code}"
        )
        signature = self._generate_signature(gateway.secret_key.strip(), message)

        if request:
            success_url = request.build_absolute_uri(reverse("payments:esewa_success"))
            failure_url = request.build_absolute_uri(reverse("payments:esewa_failure"))
        else:
            success_url = gateway.success_url
            failure_url = gateway.failure_url

        params = {
            "amount": amount,
            "tax_amount": tax_amount,
            "total_amount": total_amount,
            "transaction_uuid": transaction_uuid,
            "product_code": product_code,
            "product_service_charge": "0",
            "product_delivery_charge": "0",
            "success_url": success_url,
            "failure_url": failure_url,
            "signed_field_names": self.SIGNED_FIELDS,
            "signature": signature,
        }

        payment_base_url = gateway.sandbox_url if gateway.is_sandbox else gateway.base_url
        payment_url = f"{payment_base_url}/main/v2/form"

        return {
            "payment_url": payment_url,
            "payment_params": params,
            "method": "POST",
        }

    @staticmethod
    def handle_failure(encoded_data: str | None) -> tuple[str, dict]:
        if not encoded_data:
            return "payment_failed.html", {
                "error": "Payment verification failed. Please contact support.",
            }

        try:
            decoded_bytes = base64.b64decode(encoded_data)
            decoded_str = decoded_bytes.decode("utf-8")
            data = json.loads(decoded_str)
        except (base64.binascii.Error, json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning(f"Failed to decode eSewa failure data: {e}")
            return "payment_failed.html", {
                "error": "Payment verification failed. Please contact support.",
            }

        transaction_uuid = data.get("transaction_uuid")

        if not transaction_uuid:
            return "payment_failed.html", {
                "error": "Payment verification failed. Please contact support.",
            }

        try:
            transaction = SupportTransaction.objects.get(transaction_id=transaction_uuid)
        except SupportTransaction.DoesNotExist:
            logger.warning(f"Transaction not found for UUID: {transaction_uuid}")
            return "payment_failed.html", {
                "error": "Transaction not found",
            }

        EsewaStrategy._mark_transaction_failed(
            transaction=transaction,
            response_data=data,
            log_status=PaymentLogStatus.FAILED,
        )

        return "payment_failed.html", {
            "transaction": transaction,
            "error": "Payment verification failed. Please contact support.",
        }
