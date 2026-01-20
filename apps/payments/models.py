from django.db import models
from django.utils.translation import gettext_lazy as _


class PaymentGateway(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    brand_color = models.CharField(max_length=7, default="#000000")
    icon = models.ImageField(upload_to="payment_icons/", blank=True, null=True)

    merchant_id = models.CharField(max_length=255, blank=True)
    secret_key = models.CharField(max_length=255, blank=True)
    signature = models.CharField(max_length=255, blank=True)

    base_url = models.URLField(blank=True)
    sandbox_url = models.URLField(blank=True)
    success_url = models.URLField(blank=True)
    failure_url = models.URLField(blank=True)

    is_sandbox = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class SupportTransaction(models.Model):
    class Methods(models.TextChoices):
        ESEWA = "esewa", _("eSewa")
        KHALTI = "khalti", _("Khalti")
        STRIPE = "stripe", _("Stripe")
        PAYPAL = "paypal", _("PayPal")

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        COMPLETED = "completed", _("Completed")
        FAILED = "failed", _("Failed")

    creator = models.ForeignKey(
        "creators.CreatorProfile", on_delete=models.CASCADE, related_name="support_transactions"
    )
    supporter_name = models.CharField(max_length=255)
    amount = models.PositiveIntegerField()
    message = models.TextField(blank=True)
    payment_method = models.CharField(max_length=20, choices=Methods.choices)
    payment_status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    transaction_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.supporter_name} -> {self.creator} - Rs.{self.amount}"


class PaymentLog(models.Model):
    class Gateways(models.TextChoices):
        ESEWA = "esewa", _("eSewa")
        KHALTI = "khalti", _("Khalti")
        STRIPE = "stripe", _("Stripe")
        PAYPAL = "paypal", _("PayPal")

    class Status(models.TextChoices):
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

    transaction = models.ForeignKey(
        SupportTransaction, on_delete=models.CASCADE, related_name="payment_logs"
    )
    gateway = models.CharField(max_length=20, choices=Gateways.choices)
    request_payload = models.JSONField()
    response_payload = models.JSONField()
    status = models.CharField(max_length=50, choices=Status.choices)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.gateway} payment log for {self.transaction.transaction_id}"


class Withdrawal(models.Model):
    class Methods(models.TextChoices):
        BANK = "bank", _("Bank Transfer")
        ESEWA = "esewa", _("eSewa")
        KHALTI = "khalti", _("Khalti")
        STRIPE = "stripe", _("Stripe")
        PAYPAL = "paypal", _("PayPal")

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        PROCESSED = "processed", _("Processed")
        REJECTED = "rejected", _("Rejected")

    creator = models.ForeignKey(
        "creators.CreatorProfile", on_delete=models.CASCADE, related_name="withdrawals"
    )
    amount = models.PositiveIntegerField()
    payment_method = models.CharField(max_length=20, choices=Methods.choices, default=Methods.BANK)
    account_details = models.CharField(
        max_length=100, blank=True, help_text="Bank account number, eSewa ID, or Khalti number"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    remarks = models.TextField(blank=True, default="")
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.creator} withdrawal of {self.amount}"


class Membership(models.Model):
    class Intervals(models.TextChoices):
        MONTHLY = "monthly", _("Monthly")
        YEARLY = "yearly", _("Yearly")

    creator = models.ForeignKey(
        "creators.CreatorProfile", on_delete=models.CASCADE, related_name="memberships"
    )
    tier_name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    benefits = models.TextField()
    billing_interval = models.CharField(
        max_length=20, choices=Intervals.choices, default=Intervals.MONTHLY
    )

    def __str__(self):
        return f"{self.tier_name} ({self.creator})"


class Subscription(models.Model):
    class Status(models.TextChoices):
        Active = "active", _("Active")
        Cancelled = "cancelled", _("Cancelled")
        Expired = "expired", _("Expired")

    membership = models.ForeignKey(
        Membership, on_delete=models.CASCADE, related_name="subscriptions"
    )
    supporter_email = models.EmailField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.Active)
    start_date = models.DateField()
    next_billing_date = models.DateField()
    cancelled_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Subscription of {self.supporter_email} to {self.membership.tier_name}"
