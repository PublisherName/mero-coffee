from django.contrib import admin

from .models import NewsletterSubscriber


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "is_verified", "subscribed_at", "verified_at")
    list_filter = ("is_verified", "subscribed_at")
    search_fields = ("email",)
    readonly_fields = ("verification_token", "subscribed_at", "verified_at")
