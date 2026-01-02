from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import BooleanField, Case, Count, Q, Sum, Value, When
from django.utils import timezone

User = get_user_model()


class CreatorProfileQuerySet(models.QuerySet):
    @classmethod
    def _monthly_start(cls):
        return timezone.now() - timedelta(days=30)

    def _creator_stats(self):
        start = self._monthly_start()
        return {
            "supporter_count": Count(
                "support_transactions__supporter_name",
                filter=Q(support_transactions__payment_status="completed"),
                distinct=True,
            ),
            "monthly_income": Sum(
                "support_transactions__amount",
                filter=Q(
                    support_transactions__payment_status="completed",
                    support_transactions__created_at__gte=start,
                ),
            ),
            "can_receive_payment": Case(
                When(user__verified=True, user__kyc__status="approved", then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
        }

    def is_creators(self):
        return self.filter(
            user__is_active=True,
            user__is_staff=False,
            user__role=User.Roles.CREATOR,
        )

    def active_creators(self):
        return self.is_creators().filter(
            user__verified=True,
            user__kyc__status="approved",
        )

    def active_creators_with_stats(self):
        return self.active_creators().annotate(**self._creator_stats())

    def by_username(self, username):
        return (
            self.is_creators()
            .filter(user__username=username)
            .select_related("user__kyc")
            .only(
                "id",
                "display_name",
                "bio",
                "avatar_url",
                "coffee_price",
                "is_active",
                "user__username",
                "user__role",
                "user__verified",
                "user__kyc__status",
            )
            .annotate(**self._creator_stats())
        )

    def by_username_active(self, username):
        return (
            self.active_creators()
            .filter(user__username=username)
            .annotate(**self._creator_stats())
            .select_related("user")
        )

    def search(self, text):
        if not text:
            return self.active_creators()
        return self.active_creators().filter(
            Q(display_name__icontains=text)
            | Q(user__username__icontains=text)
            | Q(bio__icontains=text)
        )

    def sort_supporters(self):
        return (
            self.active_creators()
            .annotate(
                supporter_count=Count(
                    "support_transactions__supporter_name",
                    filter=Q(support_transactions__payment_status="completed"),
                    distinct=True,
                )
            )
            .order_by("-supporter_count")
        )

    def sort_recent(self):
        return self.active_creators().order_by("-user__date_joined")

    def sort_monthly(self):
        start = self._monthly_start()
        return self.annotate(
            monthly_income=Sum(
                "support_transactions__amount",
                filter=Q(
                    support_transactions__payment_status="completed",
                    support_transactions__created_at__gte=start,
                ),
            )
        ).order_by("-monthly_income")

    def sort_display(self):
        return self.active_creators().order_by("display_name")

    def apply_sort(self, key):
        if key == "supporters":
            return self.sort_supporters()
        if key == "recent":
            return self.sort_recent()
        if key == "monthly":
            return self.sort_monthly()
        if key == "alphabetic":
            return self.sort_display()
        return self.sort_supporters()
