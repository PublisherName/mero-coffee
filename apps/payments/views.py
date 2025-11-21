from django.shortcuts import get_object_or_404, render

from .models import PaymentGateway, SupportTransaction


def checkout(request, transaction_id):
    transaction = get_object_or_404(SupportTransaction, transaction_id=transaction_id)
    gateway = get_object_or_404(PaymentGateway, slug=transaction.payment_method)
    return render(request, "checkout.html", {"transaction": transaction, "gateway": gateway})


def success(request):
    return render(request, "success.html", {})
