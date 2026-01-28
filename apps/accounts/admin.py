from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import reverse
from django.utils.html import format_html

from .models import KYC, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "role", "is_verified", "is_active", "date_joined")
    list_filter = ("role", "is_verified", "is_active", "is_staff", "date_joined")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-date_joined",)

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("role", "is_verified")}),
    )

    add_fieldsets = (
        (None, {"fields": ("username", "usable_password", "password1", "password2")}),
        ("Personal Information", {"fields": ("email", "first_name", "last_name")}),
        (
            "Permission",
            {
                "fields": (
                    "role",
                    "is_verified",
                    "is_active",
                )
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        """Ensure role permissions are properly assigned when user is saved via admin."""
        from apps.accounts.signals.roles import assign_user_group, get_expected_flags

        super().save_model(request, obj, form, change)

        expected_staff, expected_superuser = get_expected_flags(obj.role)
        if obj.is_staff != expected_staff or obj.is_superuser != expected_superuser:
            obj.is_staff = expected_staff
            obj.is_superuser = expected_superuser
            super().save_model(request, obj, form, change)

        assign_user_group(obj)


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
        "full_name",
        "phone",
        "country_name",
        "region_name",
        "subregion_name",
        "city_name",
        "address",
        "id_type",
        "id_number",
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
                    "country_name",
                    "region_name",
                    "subregion_name",
                    "city_name",
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
                    "preview_front_image",
                    "preview_back_image",
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
            user__is_verified=True,
        ).filter(status__in=[KYC.Status.PENDING])

    @staticmethod
    def country_name(obj):
        return obj.country.name if obj.country else "-"

    country_name.short_description = "Country"

    @staticmethod
    def region_name(obj):
        return obj.region.name if obj.region else "-"

    region_name.short_description = "Region"

    @staticmethod
    def subregion_name(obj):
        return obj.subregion.name if obj.subregion else "-"

    subregion_name.short_description = "Subregion"

    @staticmethod
    def city_name(obj):
        return obj.city.name if obj.city else "-"

    city_name.short_description = "City"

    @staticmethod
    def preview_front_image(obj):
        if obj.front_image:
            url = reverse("accounts:serve_kyc_document", args=[obj.id, "front_image"])
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-height: 200px; max-width: 300px;" />'
                "</a>",
                url,
                url,
            )
        return "No image uploaded"

    preview_front_image.short_description = "Front Image Preview"

    @staticmethod
    def preview_back_image(obj):
        if obj.back_image:
            url = reverse("accounts:serve_kyc_document", args=[obj.id, "back_image"])
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-height: 200px; max-width: 300px;" />'
                "</a>",
                url,
                url,
            )
        return "No image uploaded"

    preview_back_image.short_description = "Back Image Preview"

    @staticmethod
    def preview_selfie(obj):
        if obj.selfie_with_document:
            url = reverse("accounts:serve_kyc_document", args=[obj.id, "selfie_with_document"])
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-height: 200px; max-width: 300px;" />'
                "</a>",
                url,
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
