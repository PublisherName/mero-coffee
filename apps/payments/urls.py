from django.urls import path

from apps.payments.views import checkout, esewa_failure, esewa_success

app_name = "payments"

urlpatterns = [
    path("checkout/<str:transaction_id>/", checkout, name="checkout"),
    path("esewa/success/", esewa_success, name="esewa_success"),
    path("esewa/failure/", esewa_failure, name="esewa_failure"),
]
