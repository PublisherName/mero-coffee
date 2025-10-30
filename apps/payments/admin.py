from django.contrib import admin

from apps.payments.models import (
    Membership,
    PaymentLog,
    Subscription,
    SupportTransaction,
    Withdrawal,
)


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
    search_fields = ("creator__display_name", "bank_account")


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
