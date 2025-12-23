from django.conf import settings
from django.core.mail import EmailMessage
from django.template import Context, Template
from django.utils.html import strip_tags

from apps.emails.models import EmailTemplate


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
        """
        Send email using a template from database

        Args:
            template_name (str): Name of the email template
            recipient_list (list): List of email addresses
            context (dict): Context variables for template rendering
            from_email (str): Override default from email
            attachments (list): List of file attachments

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            template = EmailTemplate.objects.get(name=template_name, is_active=True)
        except EmailTemplate.DoesNotExist:
            return False

        if not context:
            context = {}

        # Add default context variables
        default_context = {
            "site_url": cls._get_site_url,
            "site_name": getattr(settings, "SITE_NAME", "MeroCoffee"),
        }
        default_context.update(context)

        try:
            # Render subject
            subject_template = Template(template.subject)
            subject = subject_template.render(Context(default_context))

            # Render HTML content
            html_template = Template(template.html_content)
            html_message = html_template.render(Context(default_context))

            # Generate text content
            text_message = template.text_content
            if text_message:
                text_template = Template(text_message)
                text_message = text_template.render(Context(default_context))
            else:
                text_message = strip_tags(html_message)

            # Determine from email
            if from_email is None:
                from_email = settings.DEFAULT_FROM_EMAIL

            # Create email message
            email = EmailMessage(
                subject=subject,
                body=html_message,
                from_email=from_email,
                to=recipient_list,
            )
            email.content_subtype = "html"

            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    if isinstance(attachment, dict):
                        email.attach(
                            attachment.get("filename", "attachment"),
                            attachment.get("content", b""),
                            attachment.get("mimetype", "application/octet-stream"),
                        )
                    else:
                        # Assume it's a file-like object
                        email.attach(attachment)

            email.send()
            return True

        except Exception:
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
            except Exception as e:
                errors.append(f"Subject template error: {str(e)}")

            # Check HTML template
            try:
                Template(template.html_content).render(Context({}))
            except Exception as e:
                errors.append(f"HTML template error: {str(e)}")

            # Check text template if provided
            if template.text_content:
                try:
                    Template(template.text_content).render(Context({}))
                except Exception as e:
                    warnings.append(f"Text template error: {str(e)}")

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
