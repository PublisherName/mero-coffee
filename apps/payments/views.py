import logging

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from apps.payments.services.factory import PaymentFactory

from .models import PaymentGateway, SupportTransaction

logger = logging.getLogger(__name__)


def checkout(request, transaction_id):
    transaction = get_object_or_404(SupportTransaction, transaction_id=transaction_id)
    gateway = get_object_or_404(PaymentGateway, slug=transaction.payment_method)

    if not gateway.is_active:
        messages.error(
            request, f"{gateway.name} is currently unavailable. Please try another payment method."
        )
        return redirect("core:homepage")

    if transaction.payment_status == SupportTransaction.Status.COMPLETED:
        messages.success(request, "This payment has already been completed.")
        return redirect("core:homepage")

    if transaction.payment_status == SupportTransaction.Status.FAILED:
        messages.warning(request, "This payment failed. Please try again with a new transaction.")
        return redirect("core:homepage")

    try:
        strategy = PaymentFactory.get_strategy(gateway.slug)
        payment_context = strategy.get_payment_context(transaction, request)

        if "error" in payment_context:
            messages.error(request, payment_context["error"])
            return render(
                request,
                "payment_failed.html",
                {
                    "error": payment_context["error"],
                    "transaction": transaction,
                },
            )

        context = {
            "transaction": transaction,
            "gateway": gateway,
            "payment_context": payment_context,
        }
        return render(request, "checkout.html", context)

    except Exception as e:
        logger.error(
            f"Checkout error for transaction {transaction_id}: {str(e)}",
            exc_info=True,
            extra={"transaction_id": transaction_id, "gateway": gateway.slug},
        )
        messages.error(request, "An error occurred while setting up payment. Please try again.")
        return render(
            request,
            "payment_failed.html",
            {
                "error": "Payment setup failed. Please try again or contact support.",
                "transaction": transaction,
            },
        )


def esewa_success(request):
    from apps.payments.services.esewa import EsewaStrategy

    strategy = EsewaStrategy()

    encoded_data = request.GET.get("data")
    data, error = strategy.base64_decode(encoded_data)
    if error:
        return render(request, "payment_failed.html", {"error": error})

    if "error_message" in data:
        return render(
            request, "payment_failed.html", {"error": f"eSewa Error: {data.get('error_message')}"}
        )

    transaction, gateway, tx_error = strategy.get_transaction_and_gateway(data, gateway="esewa")
    if tx_error:
        return render(request, "payment_failed.html", {"error": tx_error})

    if not strategy.verify_signature(data, gateway, transaction):
        return render(
            request,
            "payment_failed.html",
            {
                "error": "Payment verification failed - signature mismatch",
                "transaction": transaction,
            },
        )

    api_response, api_error = strategy.verify_payment(transaction)
    if api_error:
        return render(
            request, "payment_failed.html", {"error": api_error, "transaction": transaction}
        )

    ref_id = (
        api_response.get("ref_id")
        if api_response and "ref_id" in api_response
        else data.get("ref_id")
    )

    template_name, context = strategy.handle_status(transaction, gateway, data, ref_id)
    return render(request, template_name, context)


def esewa_failure(request):
    from apps.payments.services.esewa import EsewaStrategy

    strategy = EsewaStrategy()
    encoded_data = request.GET.get("data")

    template, context = strategy.handle_failure(encoded_data)
    return render(request, template, context)


def stripe_success(request):
    from apps.payments.services.stripe import StripeStrategy

    strategy = StripeStrategy()
    session_id = request.GET.get("session_id")

    template, context = strategy.handle_success(session_id)
    return render(request, template, context)


def stripe_cancel(request):
    from apps.payments.services.stripe import StripeStrategy

    strategy = StripeStrategy()
    session_id = request.GET.get("session_id")

    template, context = strategy.handle_cancel(session_id)
    return render(request, template, context)


def paypal_success(request):
    from apps.payments.services.paypal import PayPalStrategy

    strategy = PayPalStrategy()
    token = request.GET.get("token")

    if not token:
        return render(
            request,
            "payment_failed.html",
            {"error": "Missing payment token. Please contact support if you were charged."},
        )

    try:
        template, context = strategy.handle_success(token)
        return render(request, template, context)
    except Exception as e:
        logger.error(
            f"Unexpected error in paypal_success for token {token}: {str(e)}",
            exc_info=True,
            extra={"token": token},
        )
        return render(
            request,
            "payment_failed.html",
            {"error": "Payment verification failed. Please contact support if you were charged."},
        )


def paypal_cancel(request):
    from apps.payments.services.paypal import PayPalStrategy

    strategy = PayPalStrategy()
    token = request.GET.get("token")

    if not token:
        return render(
            request,
            "payment_failed.html",
            {"error": "Missing payment token. Please contact support if you were charged."},
        )

    try:
        template, context = strategy.handle_cancel(token)
        return render(request, template, context)
    except Exception as e:
        logger.error(
            f"Unexpected error in paypal_cancle for token {token}: {str(e)}",
            exc_info=True,
            extra={"token": token},
        )
        return render(
            request,
            "payment_failed.html",
            {"error": "Payment verification cancelled. Please contact support."},
        )
