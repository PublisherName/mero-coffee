from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseAdmin
from django.db import transaction
from django.urls import reverse
from django.utils.html import format_html

from .forms import CustomAdminUserCreationForm, CustomUserChangeForm
from .models import KYC, User


@admin.register(User)
class UserAdmin(BaseAdmin):
    form = CustomUserChangeForm
    add_form = CustomAdminUserCreationForm

    list_display = (
        "username",
        "email",
        "role",
        "is_staff",
        "is_superuser",
        "is_active",
        "is_verified",
        "date_joined",
    )

    list_filter = (
        "role",
        "is_verified",
        "is_active",
        "is_staff",
        "date_joined",
    )

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
    )

    ordering = ("-date_joined",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "username",
                    "email",
                    "password",
                    "role",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "is_superuser",
                    "is_staff",
                    "is_active",
                    "is_verified",
                )
            },
        ),
        (
            "Important dates",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "usable_password",
                    "password1",
                    "password2",
                    "role",
                ),
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "is_superuser",
                    "is_staff",
                    "is_active",
                    "is_verified",
                )
            },
        ),
    )

    def get_form(self, request, obj=None, **kwargs):
        form_class = super().get_form(request, obj, **kwargs)

        def form_wrapper(*args, **form_kwargs):
            form_kwargs["request"] = request
            return form_class(*args, **form_kwargs)

        return form_wrapper

    def save_model(self, request, obj, form, change):
        with transaction.atomic():
            super().save_model(request, obj, form, change)


@admin.register(KYC)
class KYCAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "country", "state", "city", "status", "created_at")
    list_filter = ("status", "country", "created_at")
    readonly_fields = (
        "user",
        "created_at",
        "updated_at",
        "preview_front_image",
        "preview_back_image",
        "preview_selfie",
        "full_name",
        "phone",
        "country_name",
        "state_name",
        "city_name",
        "address",
        "id_type",
        "id_number",
    )
    autocomplete_fields = ["country", "state", "city"]
    fieldsets = (
        (
            "Personal Details",
            {
                "fields": (
                    "user",
                    "full_name",
                    "phone",
                    "country_name",
                    "state_name",
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
        )

    @staticmethod
    def country_name(obj):
        return obj.country.name if obj.country else "-"

    country_name.short_description = "Country"

    @staticmethod
    def state_name(obj):
        return obj.state.name if obj.state else "-"

    state_name.short_description = "State"

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
