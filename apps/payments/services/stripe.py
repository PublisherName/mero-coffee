import logging
import uuid
from typing import Any

import django.db.transaction as db_tx
import stripe
from django.conf import settings
from django.urls import reverse

from apps.emails.models import EmailTemplate
from apps.emails.services import EmailService
from apps.payments.enums import PaymentLogStatus, PaymentMethods, SupportTransactionStatus
from apps.payments.models import PaymentGateway, PaymentLog, SupportTransaction
from apps.payments.services.strategy import PaymentStrategy

logger = logging.getLogger(__name__)


class StripeStrategy(PaymentStrategy):
    """All Stripe payment logic encapsulated here"""

    @classmethod
    def get_payment_context(self, transaction: SupportTransaction, request=None) -> dict[str, Any]:
        gateway = PaymentGateway.objects.get(slug="stripe")
        stripe.api_key = gateway.secret_key

        if not transaction.transaction_id:
            transaction.transaction_id = uuid.uuid4().hex
            transaction.save()

        if request:
            success_url = request.build_absolute_uri(reverse("payments:stripe_success"))
            cancel_url = request.build_absolute_uri(reverse("payments:stripe_cancel"))
        else:
            success_url = gateway.success_url
            cancel_url = gateway.failure_url

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "npr",
                            "product_data": {
                                "name": f"Support for {transaction.creator}",
                                "description": transaction.message
                                or "Thank you for your support!",
                            },
                            "unit_amount": transaction.amount * 100,
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{cancel_url}?session_id={{CHECKOUT_SESSION_ID}}",
                metadata={
                    "transaction_id": transaction.transaction_id,
                },
            )

            PaymentLog.objects.create(
                transaction=transaction,
                payment_method=PaymentMethods.STRIPE,
                request_payload={
                    "amount": transaction.amount,
                    "currency": "npr",
                    "transaction_id": transaction.transaction_id,
                },
                response_payload={"session_id": session.id},
                status=PaymentLogStatus.SESSION_CREATED,
            )

            return {
                "payment_url": session.url,
                "method": "GET",
            }
        except stripe.error.StripeError as e:
            logger.exception(
                f"Stripe session creation error tx id {transaction.transaction_id}",
            )

            PaymentLog.objects.create(
                transaction=transaction,
                payment_method=PaymentMethods.STRIPE,
                request_payload={
                    "amount": transaction.amount,
                    "transaction_id": transaction.transaction_id,
                },
                response_payload={"error": str(e)},
                status=PaymentLogStatus.SESSION_CREATION_FAILED,
            )

            return {
                "error": "Payment setup failed. Please try again or contact support.",
                "transaction": transaction,
            }

    @staticmethod
    def handle_success(session_id: str):
        gateway = PaymentGateway.objects.get(slug="stripe")
        stripe.api_key = gateway.secret_key

        try:
            with db_tx.atomic():
                session = stripe.checkout.Session.retrieve(session_id)
                transaction_id = session.metadata.get("transaction_id")
                transaction = (
                    SupportTransaction.objects.select_for_update()
                    .filter(
                        transaction_id=transaction_id,
                    )
                    .first()
                )

                if not transaction:
                    return "payment_failed.html", {"error": "No pending transaction found."}

                if (
                    session.payment_status == "paid"
                    and session.payment_intent
                    and stripe.PaymentIntent.retrieve(session.payment_intent).status == "succeeded"
                ):
                    if transaction.payment_status == SupportTransactionStatus.COMPLETED:
                        pass
                    else:
                        # TODO: Update this to webhooks (after access to stripe dashboard)

                        transaction.payment_status = SupportTransactionStatus.COMPLETED
                        transaction.save()

                        safe_payload = {
                            "session_id": session.id,
                            "payment_status": session.payment_status,
                            "amount_total": session.amount_total,
                        }

                        PaymentLog.objects.create(
                            transaction=transaction,
                            payment_method=PaymentMethods.STRIPE,
                            request_payload={"session_id": session_id},
                            response_payload=safe_payload,
                            status=PaymentLogStatus.COMPLETED,
                        )

                        # Send email to creator
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

                        # Send email to supporter if email is available
                        supporter_email = getattr(session.customer_details, "email", None)
                        if supporter_email:
                            EmailService.send_template_email(
                                template_name=EmailTemplate.Type.PAYMENT_SUCCESS_SUPPORTER,
                                recipient=supporter_email,
                                context={
                                    "creator_name": transaction.creator.display_name
                                    or transaction.creator.user.username,
                                    "amount": transaction.amount,
                                    "message": transaction.message,
                                },
                            )

                    return "payment_success.html", {
                        "transaction": transaction,
                        "gateway": gateway,
                        "payment_data": {"session_id": session_id},
                    }
                else:
                    if transaction.payment_status != SupportTransactionStatus.FAILED:
                        transaction.payment_status = SupportTransactionStatus.FAILED
                        transaction.save()

                        safe_payload = {
                            "session_id": session.id,
                            "payment_status": session.payment_status,
                            "amount_total": session.amount_total,
                        }

                        PaymentLog.objects.create(
                            transaction=transaction,
                            payment_method=PaymentMethods.STRIPE,
                            request_payload={"session_id": session_id},
                            response_payload=safe_payload,
                            status=PaymentLogStatus.PAYMENT_NOT_COMPLETED,
                        )

                    return "payment_failed.html", {
                        "error": "Payment was not completed",
                        "transaction": transaction,
                    }
        except stripe.error.StripeError:
            logger.exception(f"Stripe error for session {session_id}")

            return "payment_failed.html", {
                "error": "Payment verification failed. Please contact support."
            }

        except Exception:
            logger.exception(
                f"Unexpected error in handle_success {session_id}",
            )

            return "payment_failed.html", {
                "error": "Payment verification failed. Please contact support."
            }

    @staticmethod
    def handle_cancel(session_id: str):
        gateway = PaymentGateway.objects.get(slug="stripe")
        stripe.api_key = gateway.secret_key

        context = {"error": "Payment was cancelled"}

        try:
            with db_tx.atomic():
                session = stripe.checkout.Session.retrieve(session_id)
                transaction_id = session.metadata.get("transaction_id")

                if transaction_id:
                    transaction = (
                        SupportTransaction.objects.select_for_update()
                        .filter(transaction_id=transaction_id)
                        .first()
                    )

                    if (
                        transaction
                        and transaction.payment_status != SupportTransactionStatus.FAILED
                    ):
                        transaction.payment_status = SupportTransactionStatus.FAILED
                        transaction.save()

                        safe_payload = {
                            "status": "cancelled",
                            "payment_status": session.payment_status,
                            "amount_total": getattr(session, "amount_total", None),
                        }

                        PaymentLog.objects.create(
                            transaction=transaction,
                            payment_method=PaymentMethods.STRIPE,
                            request_payload={"session_id": session_id},
                            response_payload=safe_payload,
                            status=PaymentLogStatus.CANCELLED,
                        )

                        context["transaction"] = transaction

        except stripe.error.StripeError:
            logger.exception(f"Stripe error in cancel {session_id}")

        except Exception:
            logger.exception(f"Error in handle_cancel {session_id}")

        return "payment_failed.html", context
