from typing import ClassVar

from django.db import models
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class EmailTemplate(models.Model):
    """Model for storing email templates in database"""

    class Type(TextChoices):
        NEWSLETTER_VERIFICATION = "newsletter_verification", _("Newsletter Verification")
        NEWSLETTER_WELCOME = "newsletter_welcome", _("Newsletter Welcome")
        USER_REGISTRATION = "user_registration", _("User Registration")
        PASSWORD_RESET = "password_reset", _("Password Reset")
        EMAIL_VERIFICATION = "email_verification", _("Email Verification")
        PAYMENT_SUCCESS_CREATOR = "payment_success_creator", _("Payment Success Creator")
        PAYMENT_SUCCESS_SUPPORTER = "payment_success_supporter", _("Payment Success Supporter")
        CUSTOM = "custom", _("Custom")

    name = models.CharField(
        max_length=100, unique=True, help_text="Unique identifier for this template"
    )
    template_type = models.CharField(max_length=50, choices=Type, default=Type.CUSTOM)
    subject = models.CharField(max_length=255, help_text="Email subject line")
    html_content = models.TextField(help_text="HTML content with template variables")
    text_content = models.TextField(
        blank=True, help_text="Plain text content (optional, auto-generated if empty)"
    )
    is_active = models.BooleanField(default=True, help_text="Whether this template is active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar[list[str]] = ["name"]
        indexes: ClassVar[list] = [
            models.Index(fields=["name"]),
            models.Index(fields=["template_type"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"

    def save(self, *args, **kwargs):
        if not self.text_content and self.html_content:
            import re

            text = re.sub("<[^<]+?>", "", self.html_content)
            text = re.sub(r"\s+", " ", text).strip()
            self.text_content = text
        super().save(*args, **kwargs)

    def get_context_variables(self):
        """Extract template variables from HTML and text content"""
        import re

        pattern = r"\{\{\s*(\w+)\s*\}\}"
        variables = set()

        for content in [self.html_content, self.text_content]:
            if content:
                variables.update(re.findall(pattern, content))

        return sorted(variables)
