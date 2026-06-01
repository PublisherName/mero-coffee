from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Sum

from apps.payments.enums import SupportTransactionStatus, WithdrawalStatus
from apps.payments.models import SupportTransaction, Withdrawal

from .managers import CreatorProfileManager


class CreatorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="creator_profile"
    )
    display_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    avatar_url = models.URLField(blank=True)
    coffee_price = models.PositiveIntegerField(default=100)
    is_active = models.BooleanField(default=True)

    objects = CreatorProfileManager()

    def __str__(self):
        return self.display_name or self.user.username

    @property
    def avatar_color(self):
        """Generate a consistent color based on username hash"""
        colors = [
            "#ef4444",  # red
            "#f97316",  # orange
            "#f59e0b",  # amber
            "#84cc16",  # lime
            "#10b981",  # emerald
            "#14b8a6",  # teal
            "#06b6d4",  # cyan
            "#3b82f6",  # blue
            "#6366f1",  # indigo
            "#8b5cf6",  # violet
            "#a855f7",  # purple
            "#ec4899",  # pink
        ]
        # Use hash of username to consistently pick a color
        username_hash = hash(self.user.username)
        return colors[username_hash % len(colors)]

    @property
    def total_earnings(self):
        completed = SupportTransaction.objects.filter(
            creator=self, payment_status=SupportTransactionStatus.COMPLETED
        )
        return completed.aggregate(total=Sum("amount"))["total"] or Decimal(0)

    @property
    def pending_balance(self):
        pending_balance = Withdrawal.objects.filter(creator=self, status=WithdrawalStatus.PENDING)
        return pending_balance.aggregate(total=models.Sum("amount"))["total"] or Decimal(0)

    @property
    def withdrawn_balance(self):
        withdrawn_balance = Withdrawal.objects.filter(
            creator=self, status=WithdrawalStatus.PROCESSED
        )
        return withdrawn_balance.aggregate(total=models.Sum("amount"))["total"] or Decimal(0)

    @property
    def available_balance(self):
        return self.total_earnings - (self.pending_balance + self.withdrawn_balance)
