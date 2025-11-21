from django.db import models


class SupportTransaction(models.Model):
    PAYMENT_METHODS = [
        ("esewa", "eSewa"),
        ("khalti", "Khalti"),
    ]

    PAYMENT_STATUS = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    creator = models.ForeignKey(
        "creators.CreatorProfile", on_delete=models.CASCADE, related_name="support_transactions"
    )
    supporter_name = models.CharField(max_length=255)
    amount = models.PositiveIntegerField()
    message = models.TextField(blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="pending")
    transaction_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.supporter_name} -> {self.creator} - Rs.{self.amount}"


class PaymentLog(models.Model):
    GATEWAYS = [
        ("esewa", "eSewa"),
        ("khalti", "Khalti"),
    ]

    transaction = models.ForeignKey(
        SupportTransaction, on_delete=models.CASCADE, related_name="payment_logs"
    )
    gateway = models.CharField(max_length=20, choices=GATEWAYS)
    request_payload = models.JSONField()
    response_payload = models.JSONField()
    status = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.gateway} payment log for {self.transaction.transaction_id}"


class Withdrawal(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processed", "Processed"),
        ("rejected", "Rejected"),
    ]

    creator = models.ForeignKey(
        "creators.CreatorProfile", on_delete=models.CASCADE, related_name="withdrawals"
    )
    amount = models.PositiveIntegerField()
    bank_account = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.creator} withdrawal Rs.{self.amount} ({self.status})"


class Membership(models.Model):
    BILLING_INTERVALS = [
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
    ]

    creator = models.ForeignKey(
        "creators.CreatorProfile", on_delete=models.CASCADE, related_name="memberships"
    )
    tier_name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    benefits = models.TextField()
    billing_interval = models.CharField(
        max_length=20, choices=BILLING_INTERVALS, default="monthly"
    )

    def __str__(self):
        return f"{self.tier_name} ({self.creator})"


class Subscription(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("cancelled", "Cancelled"),
        ("expired", "Expired"),
    ]

    membership = models.ForeignKey(
        Membership, on_delete=models.CASCADE, related_name="subscriptions"
    )
    supporter_email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    start_date = models.DateField()
    next_billing_date = models.DateField()
    cancelled_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Subscription of {self.supporter_email} to {self.membership.tier_name}"
