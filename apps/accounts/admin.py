from django.contrib import admin

from .models import KYC


@admin.register(KYC)
class KYCAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "country", "region", "city", "status", "created_at")
    list_filter = ("status", "country", "created_at")
    readonly_fields = ("created_at", "updated_at")
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
        ("ID Verification", {"fields": ("id_type", "id_number")}),
        ("Status", {"fields": ("status", "rejection_reason")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
    actions = ["approve_kyc", "reject_kyc"]

    def get_queryset(self, request):
        """Exclude staff accounts from KYC list."""
        qs = super().get_queryset(request)
        return qs.filter(user__is_staff=False, user__verified=True)

    @admin.action(description="Approve selected KYC")
    def approve_kyc(self, request, queryset):
        updated = queryset.filter(status=KYC.Status.PENDING).update(status=KYC.Status.APPROVED)
        self.message_user(request, f"{updated} KYC(s) approved.")

    @admin.action(description="Reject selected KYC")
    def reject_kyc(self, request, queryset):
        updated = queryset.filter(status=KYC.Status.PENDING).update(status=KYC.Status.REJECTED)
        self.message_user(request, f"{updated} KYC(s) rejected.")
