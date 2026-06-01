from django.conf import settings
from django.core.mail import EmailMessage
from django.template import Context, Template

from apps.emails.models import EmailTemplate
from apps.emails.tasks import send_email_task


class EmailService:
    """Centralized email service for sending templates emails"""

    @staticmethod
    def _get_site_url():
        """Get the site URL from settings"""
        return getattr(settings, "SITE_BASE_URL", "http://localhost:8000").rstrip("/")

    @classmethod
    def send_email(
        cls, template_name, recipient_list, context=None, from_email=None, attachments=None
    ):
        """Simplified email sending with Celery support"""
        try:
            template = EmailTemplate.objects.get(name=template_name, is_active=True)

            context = context or {}
            ctx = {
                "site_url": cls._get_site_url(),
                "site_name": getattr(settings, "SITE_NAME", "MeroCoffee"),
                **context,
            }
            subject = Template(template.subject).render(Context(ctx))
            html_message = Template(template.html_content).render(Context(ctx))

            from_email = from_email or settings.DEFAULT_FROM_EMAIL

            if getattr(settings, "USE_CELERY", False):
                attachments_data = [
                    {
                        "filename": att.get("filename", "attachment"),
                        "content": att.get("content", b""),
                        "mimetype": att.get("mimetype", "application/octet-stream"),
                    }
                    for att in (attachments or [])
                    if isinstance(att, dict)
                ]
                send_email_task.delay(
                    subject, html_message, from_email, recipient_list, "html", attachments_data
                )
                return True
            else:
                email = EmailMessage(subject, html_message, from_email, recipient_list)
                email.content_subtype = "html"

                for att in attachments or []:
                    if isinstance(att, dict):
                        email.attach(
                            att.get("filename", "attachment"),
                            att.get("content", b""),
                            att.get("mimetype", "application/octet-stream"),
                        )
                    else:
                        email.attach(att)

                email.send()
                return True
        except Exception:  # noqa: BLE001
            return False

    @classmethod
    def send_template_email(cls, template_name, recipient, context=None, from_email=None):
        """
        Send email to single recipient using template

        Args:
            template_name (str): Name of the email template
            recipient (str): Email address of recipient
            context (dict): Context variables for template rendering
            from_email (str): Override default from email

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        return cls.send_email(
            template_name=template_name,
            recipient_list=[recipient],
            context=context,
            from_email=from_email,
        )

    @classmethod
    def get_template_variables(cls, template_name):
        """Get list of required variables for a template"""
        try:
            template = EmailTemplate.objects.get(name=template_name, is_active=True)
            return template.get_context_variables()
        except EmailTemplate.DoesNotExist:
            return []

    @classmethod
    def validate_template(cls, template_name):
        """Validate template syntax and return validation results"""
        try:
            template = EmailTemplate.objects.get(name=template_name, is_active=True)

            errors = []
            warnings = []

            # Check subject template
            try:
                Template(template.subject).render(Context({}))
            except Exception as e:  # noqa: BLE001
                errors.append(f"Subject template error: {e!s}")

            # Check HTML template
            try:
                Template(template.html_content).render(Context({}))
            except Exception as e:  # noqa: BLE001
                errors.append(f"HTML template error: {e!s}")

            # Check text template if provided
            if template.text_content:
                try:
                    Template(template.text_content).render(Context({}))
                except Exception as e:  # noqa: BLE001
                    warnings.append(f"Text template error: {e!s}")

            # Check for required variables
            variables = template.get_context_variables()
            required_vars = ["site_url", "site_name"]
            missing_vars = [var for var in required_vars if var not in variables]
            if missing_vars:
                warnings.append(f"Missing recommended variables: {', '.join(missing_vars)}")

            return {
                "is_valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "variables": variables,
            }

        except EmailTemplate.DoesNotExist:
            return {
                "is_valid": False,
                "errors": [f"Template '{template_name}' not found or inactive"],
                "warnings": [],
                "variables": [],
            }
