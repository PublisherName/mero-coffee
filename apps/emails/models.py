from django.db import models


class EmailTemplate(models.Model):
    """Model for storing email templates in database"""

    TEMPLATE_TYPES = [
        ("newsletter_verification", "Newsletter Verification"),
        ("newsletter_welcome", "Newsletter Welcome"),
        ("user_registration", "User Registration"),
        ("password_reset", "Password Reset"),
        ("email_verification", "Email Verification"),
        ("custom", "Custom"),
    ]

    name = models.CharField(
        max_length=100, unique=True, help_text="Unique identifier for this template"
    )
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPES, default="custom")
    subject = models.CharField(max_length=255, help_text="Email subject line")
    html_content = models.TextField(help_text="HTML content with template variables")
    text_content = models.TextField(
        blank=True, help_text="Plain text content (optional, auto-generated if empty)"
    )
    is_active = models.BooleanField(default=True, help_text="Whether this template is active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
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
