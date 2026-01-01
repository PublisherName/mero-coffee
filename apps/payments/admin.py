from time import timezone

from django.contrib import admin

from apps.payments.models import (
    Membership,
    PaymentGateway,
    PaymentLog,
    Subscription,
    SupportTransaction,
    Withdrawal,
)


@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "is_sandbox")
    list_filter = ("is_active", "is_sandbox")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(SupportTransaction)
class SupportTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "creator",
        "supporter_name",
        "amount",
        "payment_method",
        "payment_status",
        "transaction_id",
        "created_at",
    )
    list_filter = ("payment_method", "payment_status", "created_at")
    search_fields = (
        "supporter_name",
        "supporter_email",
        "transaction_id",
        "creator__display_name",
    )


@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    list_display = ("transaction", "gateway", "status", "timestamp")
    list_filter = ("gateway", "status", "timestamp")
    search_fields = ("transaction__transaction_id",)


@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ("creator", "amount", "status", "requested_at", "processed_at")
    list_filter = ("status", "requested_at", "processed_at")
    search_fields = ("creator__display_name", "creator__user__email", "account_details")

    readonly_fields = (
        "creator",
        "amount",
        "payment_method",
        "account_details",
        "requested_at",
        "processed_at",
    )

    fieldsets = (
        (
            "Request Details",
            {
                "fields": (
                    "creator",
                    "amount",
                    "payment_method",
                    "account_details",
                    "requested_at",
                ),
                "classes": ("wide",),
            },
        ),
        (
            "Admin Actions",
            {"fields": ("status", "remarks", "processed_at"), "classes": ("collapse",)},
        ),
    )

    actions = ["mark_processed", "mark_rejected"]

    @admin.action(description="Mark selected withdrawals as processed")
    def mark_processed(self, request, queryset):
        updated = queryset.update(status=Withdrawal.Status.PROCESSED, processed_at=timezone.now())
        self.message_user(request, f"{updated} withdrawal(s) marked as processed.")

    @admin.action(description="Mark selected withdrawals as rejected")
    def mark_rejected(self, request, queryset):
        updated = queryset.update(status=Withdrawal.Status.REJECTED)
        self.message_user(request, f"{updated} withdrawal(s) marked as rejected.")


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("tier_name", "creator", "price", "billing_interval")
    list_filter = ("billing_interval",)
    search_fields = ("tier_name", "creator__display_name")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "membership",
        "supporter_email",
        "status",
        "start_date",
        "next_billing_date",
        "cancelled_at",
    )
    list_filter = ("status", "start_date", "next_billing_date")
    search_fields = ("supporter_email", "membership__tier_name")
