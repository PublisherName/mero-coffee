from django.shortcuts import get_object_or_404, render

from .models import SupportTransaction


def checkout(request, transaction_id):
    transaction = get_object_or_404(SupportTransaction, transaction_id=transaction_id)
    return render(request, "payments/checkout.html", {"transaction": transaction})


def success(request):
    return render(request, "payments/success.html", {})
