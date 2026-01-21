from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import BooleanField, Case, Count, Q, Sum, Value, When
from django.utils import timezone

User = get_user_model()


class CreatorProfileQuerySet(models.QuerySet):
    @property
    def monthly_start(self):
        return timezone.now() - timedelta(days=30)

    def _supporter_count_annotation(self):  # noqa: PLR6301
        return Count(
            "support_transactions__id",
            filter=Q(support_transactions__payment_status="completed"),
            distinct=True,
        )

    def _monthly_income_annotation(self):
        return Sum(
            "support_transactions__amount",
            filter=Q(
                support_transactions__payment_status="completed",
                support_transactions__created_at__gte=self.monthly_start,
            ),
        )

    def _can_receive_payment_annotation(self):  # noqa: PLR6301
        return Case(
            When(
                user__is_verified=True,
                user__kyc__status="approved",
                then=Value(True),
            ),
            default=Value(False),
            output_field=BooleanField(),
        )

    def _creator_stats(self):
        return {
            "supporter_count": self._supporter_count_annotation(),
            "monthly_income": self._monthly_income_annotation(),
            "can_receive_payment": self._can_receive_payment_annotation(),
        }

    def is_creators(self):
        return self.filter(
            user__is_active=True,
            user__is_staff=False,
            user__role=User.Roles.CREATOR,
        )

    def active_creators(self):
        return self.is_creators().filter(
            user__is_verified=True,
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
                "user__is_verified",
                "user__kyc__status",
            )
            .annotate(**self._creator_stats())
        )

    def by_username_active(self, username):
        return (
            self.active_creators()
            .filter(user__username=username)
            .select_related("user", "user__kyc")
            .annotate(**self._creator_stats())
        )

    def search(self, text):
        queryset = self.active_creators()
        if not text:
            return queryset

        return queryset.filter(
            Q(display_name__icontains=text)
            | Q(user__username__icontains=text)
            | Q(bio__icontains=text)
        )

    def sort_supporters(self):
        return (
            self.active_creators()
            .annotate(supporter_count=self._supporter_count_annotation())
            .order_by("-supporter_count")
        )

    def sort_recent(self):
        return self.active_creators().order_by("-user__date_joined")

    def sort_monthly(self):
        return (
            self.active_creators()
            .annotate(monthly_income=self._monthly_income_annotation())
            .order_by("-monthly_income")
        )

    def sort_display(self):
        return self.active_creators().order_by("display_name")

    def apply_sort(self, sort_key):
        sort_methods = {
            "supporters": self.sort_supporters,
            "recent": self.sort_recent,
            "monthly": self.sort_monthly,
            "alphabetic": self.sort_display,
        }

        sort_method = sort_methods.get(sort_key, self.sort_supporters)
        return sort_method()
