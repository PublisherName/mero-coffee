from datetime import timedelta

from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.utils import timezone

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
    def supporters(self):
        """Count of unique supporters"""
        from apps.payments.models import SupportTransaction

        return (
            SupportTransaction.objects.filter(creator=self, payment_status="completed")
            .values("supporter_name")
            .distinct()
            .count()
        )

    @property
    def monthly(self):
        """Calculate monthly income from last 30 days"""
        from apps.payments.models import SupportTransaction

        thirty_days_ago = timezone.now() - timedelta(days=30)
        total = (
            SupportTransaction.objects.filter(
                creator=self, payment_status="completed", created_at__gte=thirty_days_ago
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )
        return int(total)
