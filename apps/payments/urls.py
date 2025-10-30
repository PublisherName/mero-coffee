from django.urls import path

from apps.payments.views import checkout, success

app_name = "payments"

urlpatterns = [
    path("checkout/", checkout, name="checkout"),
    path("success/", success, name="success"),
]
