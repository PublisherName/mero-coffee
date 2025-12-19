from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import KYC


@admin.register(KYC)
class KYCAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "country", "region", "city", "status", "created_at")
    list_filter = ("status", "country", "created_at")
    readonly_fields = (
        "created_at",
        "updated_at",
        "preview_front_image",
        "preview_back_image",
        "preview_selfie",
    )
    autocomplete_fields = ["country", "region", "subregion", "city"]
    fieldsets = (
        ("User Info", {"fields": ("user",)}),
        (
            "Personal Details",
            {
                "fields": (
                    "full_name",
                    "phone",
                    "country",
                    "region",
                    "subregion",
                    "city",
                    "address",
                )
            },
        ),
        (
            "ID Verification",
            {
                "fields": (
                    "id_type",
                    "id_number",
                    "front_image",
                    "preview_front_image",
                    "back_image",
                    "preview_back_image",
                    "selfie_with_document",
                    "preview_selfie",
                )
            },
        ),
        ("Status", {"fields": ("status", "rejection_reason")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
    actions = ["approve_kyc", "reject_kyc"]

    def get_queryset(self, request):
        """Exclude staff accounts from KYC list."""
        qs = super().get_queryset(request)
        return qs.filter(
            user__is_staff=False,
            user__verified=True,
        ).filter(status__in=[KYC.Status.PENDING])

    @staticmethod
    def preview_front_image(obj):
        if obj.front_image:
            url = reverse("accounts:serve_kyc_document", args=[obj.id, "front_image"])
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 300px;" />',
                url,
            )
        return "No image uploaded"

    preview_front_image.short_description = "Front Image Preview"

    @staticmethod
    def preview_back_image(obj):
        if obj.back_image:
            url = reverse("accounts:serve_kyc_document", args=[obj.id, "back_image"])
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 300px;" />',
                url,
            )
        return "No image uploaded"

    preview_back_image.short_description = "Back Image Preview"

    @staticmethod
    def preview_selfie(obj):
        if obj.selfie_with_document:
            url = reverse("accounts:serve_kyc_document", args=[obj.id, "selfie_with_document"])
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 300px;" />',
                url,
            )
        return "No image uploaded"

    preview_selfie.short_description = "Selfie Preview"

    @admin.action(description="Approve selected KYC")
    def approve_kyc(self, request, queryset):
        updated = queryset.filter(status=KYC.Status.PENDING).update(status=KYC.Status.APPROVED)
        self.message_user(request, f"{updated} KYC(s) approved.")

    @admin.action(description="Reject selected KYC")
    def reject_kyc(self, request, queryset):
        updated = queryset.filter(status=KYC.Status.PENDING).update(status=KYC.Status.REJECTED)
        self.message_user(request, f"{updated} KYC(s) rejected.")
