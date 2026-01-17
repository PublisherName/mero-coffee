from django.shortcuts import get_object_or_404, render

from .models import PaymentGateway, SupportTransaction
from .services import PaymentFactory


def checkout(request, transaction_id):
    transaction = get_object_or_404(SupportTransaction, transaction_id=transaction_id)
    gateway = get_object_or_404(PaymentGateway, slug=transaction.payment_method)

    strategy = PaymentFactory.get_strategy(gateway.slug)
    payment_context = strategy.get_payment_context(transaction, request)

    context = {
        "transaction": transaction,
        "gateway": gateway,
        "payment_context": payment_context,
    }
    return render(request, "checkout.html", context)


def esewa_success(request):
    from .services import EsewaStrategy

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
    from .services import EsewaStrategy

    strategy = EsewaStrategy()
    encoded_data = request.GET.get("data")

    template, context = strategy.handle_failure(encoded_data)
    return render(request, template, context)


def stripe_success(request):
    from .services import StripeStrategy

    strategy = StripeStrategy()
    session_id = request.GET.get("session_id")

    template, context = strategy.handle_success(session_id)
    return render(request, template, context)


def stripe_cancel(request):
    from .services import StripeStrategy

    strategy = StripeStrategy()
    session_id = request.GET.get("session_id")

    template, context = strategy.handle_cancel(session_id)
    return render(request, template, context)
