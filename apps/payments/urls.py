from django.urls import path

from apps.payments.views import (
    checkout,
    esewa_failure,
    esewa_success,
    paypal_cancel,
    paypal_success,
    stripe_cancel,
    stripe_success,
)

app_name = "payments"

urlpatterns = [
    path("checkout/<str:transaction_id>/", checkout, name="checkout"),
    path("esewa/success/", esewa_success, name="esewa_success"),
    path("esewa/failure/", esewa_failure, name="esewa_failure"),
    path("stripe/success/", stripe_success, name="stripe_success"),
    path("stripe/cancel/", stripe_cancel, name="stripe_cancel"),
    path("paypal/success/", paypal_success, name="paypal_success"),
    path("paypal/cancel/", paypal_cancel, name="paypal_cancel"),
]
