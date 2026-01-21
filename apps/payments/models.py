from django.db import models

from .enums import (
    MembershipIntervals,
    PaymentLogStatus,
    PaymentMethods,
    SubscriptionStatus,
    SupportTransactionStatus,
    WithdrawalStatus,
)


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
    creator = models.ForeignKey(
        "creators.CreatorProfile", on_delete=models.CASCADE, related_name="support_transactions"
    )
    supporter_name = models.CharField(max_length=255)
    amount = models.PositiveIntegerField()
    message = models.TextField(blank=True)
    payment_method = models.CharField(max_length=20, choices=PaymentMethods.choices)
    payment_status = models.CharField(
        max_length=20,
        choices=SupportTransactionStatus.choices,
        default=SupportTransactionStatus.PENDING,
    )
    transaction_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.supporter_name} -> {self.creator} - Rs.{self.amount}"

    class Meta:
        indexes = [
            models.Index(fields=["payment_status", "created_at"]),
            models.Index(fields=["payment_status", "supporter_name"]),
            models.Index(fields=["creator", "payment_status"]),
        ]


class PaymentLog(models.Model):
    transaction = models.ForeignKey(
        SupportTransaction, on_delete=models.CASCADE, related_name="payment_logs"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethods.choices,
        default=PaymentMethods.BANK,
    )
    request_payload = models.JSONField()
    response_payload = models.JSONField()
    status = models.CharField(max_length=50, choices=PaymentLogStatus.choices)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.payment_method} payment log for {self.transaction.transaction_id}"


class Withdrawal(models.Model):
    creator = models.ForeignKey(
        "creators.CreatorProfile", on_delete=models.CASCADE, related_name="withdrawals"
    )
    amount = models.PositiveIntegerField()
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethods.choices,
        default=PaymentMethods.BANK,
    )
    account_details = models.CharField(
        max_length=100, blank=True, help_text="Bank account number, eSewa ID, or Khalti number"
    )
    status = models.CharField(
        max_length=20,
        choices=WithdrawalStatus.choices,
        default=WithdrawalStatus.PENDING,
    )
    remarks = models.TextField(blank=True, default="")
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.creator} withdrawal of {self.amount}"


class Membership(models.Model):
    creator = models.ForeignKey(
        "creators.CreatorProfile", on_delete=models.CASCADE, related_name="memberships"
    )
    tier_name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    benefits = models.TextField()
    billing_interval = models.CharField(
        max_length=20,
        choices=MembershipIntervals.choices,
        default=MembershipIntervals.MONTHLY,
    )

    def __str__(self):
        return f"{self.tier_name} ({self.creator})"


class Subscription(models.Model):
    membership = models.ForeignKey(
        Membership, on_delete=models.CASCADE, related_name="subscriptions"
    )
    supporter_email = models.EmailField()
    status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.ACTIVE,
    )
    start_date = models.DateField()
    next_billing_date = models.DateField()
    cancelled_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Subscription of {self.supporter_email} to {self.membership.tier_name}"
