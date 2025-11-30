from datetime import timedelta

from django.db.models import Count, Q, Sum
from django.utils import timezone


def filter_creators(search_query, queryset):
    if search_query:
        return queryset.filter(
            Q(display_name__icontains=search_query)
            | Q(user__username__icontains=search_query)
            | Q(bio__icontains=search_query)
        )
    return queryset


def sort_creators(sort_by, queryset):
    if sort_by == "supporters":
        return queryset.annotate(
            supporter_count=Count(
                "support_transactions__supporter_name",
                filter=Q(support_transactions__payment_status="completed"),
                distinct=True,
            )
        ).order_by("-supporter_count")
    elif sort_by == "recent":
        return queryset.order_by("-user__date_joined")
    elif sort_by == "monthly":
        thirty_days_ago = timezone.now() - timedelta(days=30)
        return queryset.annotate(
            monthly_income=Sum(
                "support_transactions__amount",
                filter=Q(
                    support_transactions__payment_status="completed",
                    support_transactions__created_at__gte=thirty_days_ago,
                ),
            )
        ).order_by("-monthly_income")
    else:
        return queryset.order_by("display_name")
