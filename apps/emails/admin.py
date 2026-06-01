from typing import ClassVar

from django.contrib import admin

from .models import EmailTemplate


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    """Admin interface for EmailTemplate model"""

    list_display: ClassVar[list[str]] = [
        "name",
        "template_type",
        "subject",
        "is_active",
        "created_at",
        "updated_at",
    ]
    list_filter: ClassVar[list[str]] = [
        "template_type",
        "is_active",
        "created_at",
        "updated_at",
    ]
    search_fields: ClassVar[list[str]] = [
        "name",
        "subject",
        "html_content",
        "text_content",
    ]
    readonly_fields: ClassVar[list[str]] = [
        "created_at",
        "updated_at",
        "context_variables_preview",
    ]

    fieldsets = (
        ("Basic Information", {"fields": ("name", "template_type", "subject", "is_active")}),
        ("Content", {"fields": ("html_content", "text_content"), "classes": ("wide",)}),
        (
            "Metadata",
            {
                "fields": ("created_at", "updated_at", "context_variables_preview"),
                "classes": ("wide",),
            },
        ),
    )

    @admin.display(description="Template Variables")
    @classmethod
    def context_variables_preview(cls, obj):
        """Display template variables for this template"""
        if obj:
            variables = obj.get_context_variables()
            return ", ".join(variables) if variables else "No variables found"
        return "-"

    actions: ClassVar[list[str]] = ["mark_active", "mark_inactive"]

    @admin.action(description="Mark selected templates as active")
    def mark_active(self, request, queryset):
        """Mark selected templates as active"""
        count = queryset.update(is_active=True)
        self.message_user(request, f"{count} template(s) marked as active.")

    @admin.action(description="Mark selected templates as inactive")
    def mark_inactive(self, request, queryset):
        """Mark selected templates as inactive"""
        count = queryset.update(is_active=False)
        self.message_user(request, f"{count} template(s) marked as inactive.")
