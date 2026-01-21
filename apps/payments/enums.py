from django.db import models
from django.utils.translation import gettext_lazy as _


class PaymentMethods(models.TextChoices):
    BANK = "bank", _("Bank Transfer")
    ESEWA = "esewa", _("eSewa")
    KHALTI = "khalti", _("Khalti")
    STRIPE = "stripe", _("Stripe")
    PAYPAL = "paypal", _("PayPal")


class SupportTransactionStatus(models.TextChoices):
    PENDING = "pending", _("Pending")
    COMPLETED = "completed", _("Completed")
    FAILED = "failed", _("Failed")


class WithdrawalStatus(models.TextChoices):
    PENDING = "pending", _("Pending")
    PROCESSED = "processed", _("Processed")
    REJECTED = "rejected", _("Rejected")


class MembershipIntervals(models.TextChoices):
    MONTHLY = "monthly", _("Monthly")
    YEARLY = "yearly", _("Yearly")


class SubscriptionStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    CANCELLED = "cancelled", _("Cancelled")
    EXPIRED = "expired", _("Expired")


class PaymentLogStatus(models.TextChoices):
    # eSewa statuses
    SUCCESS = "success", _("Success")
    PENDING = "pending", _("Pending")
    FAILED = "failed", _("Failed")
    AMBIGUOUS = "ambiguous", _("Ambiguous")
    NOT_FOUND = "not_found", _("Not Found")
    CANCELED = "canceled", _("Canceled")
    FULL_REFUND = "full_refund", _("Full Refund")
    PARTIAL_REFUND = "partial_refund", _("Partial Refund")
    SIGNATURE_MISMATCH = "signature_mismatch", _("Signature Mismatch")
    API_COMPLETE = "api_complete", _("API Complete")
    API_PENDING = "api_pending", _("API Pending")
    API_ERROR = "api_error", _("API Error")
    API_UNKNOWN = "api_unknown", _("API Unknown")
    UNKNOWN_STATUS = "unknown_status", _("Unknown Status")

    # Stripe statuses
    SESSION_CREATED = "session_created", _("Session Created")
    SESSION_CREATION_FAILED = "session_creation_failed", _("Session Creation Failed")
    COMPLETED = "completed", _("Completed")
    PAYMENT_NOT_COMPLETED = "payment_not_completed", _("Payment Not Completed")
    CANCELLED = "cancelled", _("Cancelled")

    # PayPal statuses
    PAYPAL_ORDER_CREATED = "paypal_order_created", _("PayPal Order Created")
    PAYPAL_ORDER_CREATION_FAILED = (
        "paypal_order_creation_failed",
        _("PayPal Order Creation Failed"),
    )
    PAYPAL_PAYMENT_CAPTURED = "paypal_payment_captured", _("PayPal Payment Captured")
    PAYPAL_PAYMENT_NOT_CAPTURED = (
        "paypal_payment_not_captured",
        _("PayPal Payment Not Captured"),
    )
