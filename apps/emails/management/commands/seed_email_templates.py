from django.core.management.base import BaseCommand
from django.db import transaction

from apps.emails.models import EmailTemplate


class Command(BaseCommand):
    help = "Seed email templates in the database"

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force update existing templates",
        )

    @classmethod
    def _get_newsletter_verification_html(cls):
        """Generate newsletter verification HTML content"""
        return (
            "<!DOCTYPE html>\n"
            '<html lang="en">\n'
            "    <head>\n"
            '        <meta charset="UTF-8">\n'
            '        <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            "        <title>Verify Your Subscription</title>\n"
            "    </head>\n"
            '    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; '
            'background-color: #0f172a;">\n'
            '        <table width="100%" cellpadding="0" cellspacing="0" '
            'style="background-color: #0f172a; padding: 40px 20px;">\n'
            "            <tr>\n"
            '                <td align="center">\n'
            '                    <table width="600" cellpadding="0" cellspacing="0" '
            'style="background: linear-gradient(to bottom, #1e293b, #0f172a); '
            "border-radius: 16px; overflow: hidden; "
            'box-shadow: 0 20px 50px rgba(0,0,0,0.5)">\n'
            "                        <tr>\n"
            '                            <td style="padding: 40px; text-align: center; '
            "background: linear-gradient(to right, #ef4444, #f97316); "
            'border-bottom: 4px solid #dc2626">\n'
            '                                <h1 style="margin: 0; color: #ffffff; '
            'font-size: 32px; font-weight: bold;">✨ {{ site_name }}</h1>\n'
            "                            </td>\n"
            "                        </tr>\n"
            "                        <tr>\n"
            '                            <td style="padding: 40px; color: #cbd5e1;">\n'
            '                                <h2 style="color: #ffffff; margin-top: 0; '
            'font-size: 24px;">Verify Your Email</h2>\n'
            '                                <p style="font-size: 16px; line-height: 1.6; '
            'margin: 20px 0;">\n'
            "                                    Thank you for subscribing to the "
            "{{ site_name }} newsletter! Click the button below to verify your "
            "email address and start receiving updates.\n"
            "                                </p>\n"
            '                                <table width="100%" cellpadding="0" '
            'cellspacing="0" style="margin: 30px 0;">\n'
            "                                    <tr>\n"
            '                                        <td align="center">\n'
            '                                            <a href="{{ verification_url }}" '
            'style="display: inline-block; padding: 16px 40px; '
            "background: linear-gradient(to right, #ef4444, #f97316); "
            "color: #ffffff; text-decoration: none; border-radius: 8px; "
            'font-weight: bold; font-size: 16px">Verify Email</a>\n'
            "                                        </td>\n"
            "                                    </tr>\n"
            "                                </table>\n"
            '                                <p style="font-size: 14px; color: #94a3b8; '
            'margin: 20px 0;">\n'
            "                                    Or copy and paste this link into your browser:\n"
            "                                    <br>\n"
            '                                    <a href="{{ verification_url }}" '
            'style="color: #f97316; word-break: break-all;">'
            "{{ verification_url }}</a>\n"
            "                                </p>\n"
            '                                <p style="font-size: 14px; color: #94a3b8; '
            'margin-top: 30px;">\n'
            "                                    If you didn't subscribe to our newsletter, "
            "please ignore this email.\n"
            "                                </p>\n"
            "                            </td>\n"
            "                        </tr>\n"
            "                        <tr>\n"
            '                            <td style="padding: 30px; text-align: center; '
            'background-color: #0f172a; border-top: 1px solid #334155">\n'
            '                                <p style="margin: 0; color: #64748b; '
            'font-size: 14px;">© 2025 {{ site_name }} Nepal. All rights reserved.'
            "</p>\n"
            "                            </td>\n"
            "                        </tr>\n"
            "                    </table>\n"
            "                </td>\n"
            "            </tr>\n"
            "        </table>\n"
            "    </body>\n"
            "</html>"
        )

    @classmethod
    def _get_newsletter_verification_text(cls):
        """Generate newsletter verification text content"""
        return (
            "Thank you for subscribing to the {{ site_name }} newsletter!\n\n"
            "Click this link to verify your email address: {{ verification_url }}\n\n"
            "If you didn't subscribe to our newsletter, please ignore this email.\n\n"
            "© 2025 {{ site_name }} Nepal. All rights reserved."
        )

    @classmethod
    def _get_newsletter_welcome_html(cls):
        """Generate newsletter welcome HTML content"""
        return (
            "<!DOCTYPE html>\n"
            '<html lang="en">\n'
            "    <head>\n"
            '        <meta charset="UTF-8">\n'
            '        <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            "        <title>Welcome to {{ site_name }} Newsletter</title>\n"
            "    </head>\n"
            '    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; '
            'background-color: #0f172a;">\n'
            '        <table width="100%" cellpadding="0" cellspacing="0" '
            'style="background-color: #0f172a; padding: 40px 20px;">\n'
            "            <tr>\n"
            '                <td align="center">\n'
            '                    <table width="600" cellpadding="0" cellspacing="0" '
            'style="background: linear-gradient(to bottom, #1e293b, #0f172a); '
            "border-radius: 16px; overflow: hidden; "
            'box-shadow: 0 20px 50px rgba(0,0,0,0.5)">\n'
            "                        <tr>\n"
            '                            <td style="padding: 40px; text-align: center; '
            "background: linear-gradient(to right, #ef4444, #f97316); "
            'border-bottom: 4px solid #dc2626">\n'
            '                                <h1 style="margin: 0; color: #ffffff; '
            'font-size: 32px; font-weight: bold;">✨ {{ site_name }}</h1>\n'
            "                            </td>\n"
            "                        </tr>\n"
            "                        <tr>\n"
            '                            <td style="padding: 40px; color: #cbd5e1;">\n'
            '                                <h2 style="color: #ffffff; margin-top: 0; '
            'font-size: 28px;">Welcome to Our Newsletter! 🎉</h2>\n'
            '                                <p style="font-size: 16px; line-height: 1.6; '
            'margin: 20px 0;">\n'
            "                                    Thank you for verifying your email and "
            "joining the {{ site_name }} community!\n"
            "                                </p>\n"
            '                                <p style="font-size: 16px; line-height: 1.6; '
            "margin: 20px 0;\">You'll now receive:</p>\n"
            '                                <ul style="font-size: 16px; line-height: 1.8; '
            'color: #cbd5e1; text-align: left; margin: 20px 0;">\n'
            "                                    <li>Latest updates about {{ site_name }} "
            "features</li>\n"
            "                                    <li>Success stories from Nepali creators</li>\n"
            "                                    <li>Tips to grow your creator page</li>\n"
            "                                    <li>Exclusive offers and announcements</li>\n"
            "                                </ul>\n"
            '                                <table width="100%" cellpadding="0" '
            'cellspacing="0" style="margin: 30px 0;">\n'
            "                                    <tr>\n"
            '                                        <td align="center">\n'
            '                                            <a href="{{ site_url }}" '
            'style="display: inline-block; padding: 16px 40px; '
            "background: linear-gradient(to right, #ef4444, #f97316); "
            "color: #ffffff; text-decoration: none; border-radius: 8px; "
            'font-weight: bold; font-size: 16px">Visit {{ site_name }}</a>\n'
            "                                        </td>\n"
            "                                    </tr>\n"
            "                                </table>\n"
            '                                <p style="font-size: 16px; line-height: 1.6; '
            'margin: 20px 0; color: #ffffff;">\n'
            "                                    Ready to start your creator journey? "
            "Create your page today and start receiving support from your fans!\n"
            "                                </p>\n"
            '                                <p style="font-size: 14px; color: #94a3b8; '
            'margin-top: 30px;">Made with ❤️ for Nepali creators</p>\n'
            "                            </td>\n"
            "                        </tr>\n"
            "                        <tr>\n"
            '                            <td style="padding: 30px; text-align: center; '
            'background-color: #0f172a; border-top: 1px solid #334155">\n'
            '                                <p style="margin: 0 0 10px 0; color: #64748b; '
            'font-size: 14px;">© 2025 {{ site_name }} Nepal. All rights reserved.'
            "</p>\n"
            '                                <p style="margin: 0; color: #64748b; '
            'font-size: 12px;">\n'
            "                                    You're receiving this because you "
            "subscribed to our newsletter.\n"
            "                                </p>\n"
            "                            </td>\n"
            "                        </tr>\n"
            "                    </table>\n"
            "                </td>\n"
            "            </tr>\n"
            "        </table>\n"
            "    </body>\n"
            "</html>"
        )

    @classmethod
    def _get_newsletter_welcome_text(cls):
        """Generate newsletter welcome text content"""
        return (
            "Welcome to {{ site_name }} Newsletter!\n\n"
            "Thank you for verifying your email and joining the {{ site_name }} "
            "community!\n\n"
            "You'll now receive:\n"
            "- Latest updates about {{ site_name }} features\n"
            "- Success stories from Nepali creators\n"
            "- Tips to grow your creator page\n"
            "- Exclusive offers and announcements\n\n"
            "Visit us at: {{ site_url }}\n\n"
            "Ready to start your creator journey? Create your page today and start "
            "receiving support from your fans!\n\n"
            "Made with ❤️ for Nepali creators\n\n"
            "© 2025 {{ site_name }} Nepal. All rights reserved."
        )

    @classmethod
    def _get_email_verification_html(cls):
        """Generate email verification HTML content"""
        return (
            "<!DOCTYPE html>\n"
            '<html lang="en">\n'
            "    <head>\n"
            '        <meta charset="UTF-8">\n'
            '        <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            "        <title>Verify Your Email - {{ site_name }}</title>\n"
            "    </head>\n"
            '    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; '
            'background-color: #0f172a;">\n'
            '        <table width="100%" cellpadding="0" cellspacing="0" '
            'style="background-color: #0f172a; padding: 40px 20px;">\n'
            "            <tr>\n"
            '                <td align="center">\n'
            '                    <table width="600" cellpadding="0" cellspacing="0" '
            'style="background: linear-gradient(to bottom, #1e293b, #0f172a); '
            "border-radius: 16px; overflow: hidden; "
            'box-shadow: 0 20px 50px rgba(0,0,0,0.5)">\n'
            "                        <tr>\n"
            '                            <td style="padding: 40px; text-align: center; '
            "background: linear-gradient(to right, #ef4444, #f97316); "
            'border-bottom: 4px solid #dc2626">\n'
            '                                <h1 style="margin: 0; color: #ffffff; '
            'font-size: 32px; font-weight: bold;">✨ {{ site_name }}</h1>\n'
            "                            </td>\n"
            "                        </tr>\n"
            "                        <tr>\n"
            '                            <td style="padding: 40px; color: #cbd5e1;">\n'
            '                                <h2 style="color: #ffffff; margin-top: 0; '
            'font-size: 24px;">Verify Your Email Address</h2>\n'
            '                                <p style="font-size: 16px; line-height: 1.6; '
            'margin: 20px 0;">\n'
            "                                    Hi {{ username }},<br>\n"
            "                                    Thank you for joining {{ site_name }}! "
            "Please verify your email address to activate your account and start "
            "your creator journey.\n"
            "                                </p>\n"
            '                                <table width="100%" cellpadding="0" '
            'cellspacing="0" style="margin: 30px 0;">\n'
            "                                    <tr>\n"
            '                                        <td align="center">\n'
            '                                            <a href="{{ verification_url }}" '
            'style="display: inline-block; padding: 16px 40px; '
            "background: linear-gradient(to right, #ef4444, #f97316); "
            "color: #ffffff; text-decoration: none; border-radius: 8px; "
            'font-weight: bold; font-size: 16px">Verify Email</a>\n'
            "                                        </td>\n"
            "                                    </tr>\n"
            "                                </table>\n"
            '                                <p style="font-size: 14px; color: #94a3b8; '
            'margin: 20px 0;">\n'
            "                                    Or copy and paste this link into your browser:\n"
            "                                    <br>\n"
            '                                    <a href="{{ verification_url }}" '
            'style="color: #f97316; word-break: break-all;">'
            "{{ verification_url }}</a>\n"
            "                                </p>\n"
            '                                <p style="font-size: 14px; color: #94a3b8; '
            'margin-top: 30px;">\n'
            "                                    This link will expire in {{ expiration_hours }}"
            " hours.\n"
            "                                    <br>\n"
            "                                    If you didn't create an account with "
            "{{ site_name }}, please ignore this email.\n"
            "                                </p>\n"
            "                            </td>\n"
            "                        </tr>\n"
            "                        <tr>\n"
            '                            <td style="padding: 30px; text-align: center; '
            'background-color: #0f172a; border-top: 1px solid #334155">\n'
            '                                <p style="margin: 0; color: #64748b; '
            'font-size: 14px;">© 2025 {{ site_name }} Nepal. All rights reserved.'
            "</p>\n"
            "                            </td>\n"
            "                        </tr>\n"
            "                    </table>\n"
            "                </td>\n"
            "            </tr>\n"
            "        </table>\n"
            "    </body>\n"
            "</html>"
        )

    @classmethod
    def _get_email_verification_text(cls):
        """Generate email verification text content"""
        return (
            "Hi {{ username }},\n\n"
            "Thank you for joining {{ site_name }}! Please verify your email "
            "address to activate your account and start your creator journey.\n\n"
            "Click this link to verify your email: {{ verification_url }}\n\n"
            "This link will expire in {{ expiration_hours }} hours.\n\n"
            "If you didn't create an account with {{ site_name }}, please "
            "ignore this email.\n\n"
            "© 2025 {{ site_name }} Nepal. All rights reserved."
        )

    @classmethod
    def _get_password_reset_html(cls):
        """Generate password reset HTML content"""
        return (
            "<!DOCTYPE html>\n"
            '<html lang="en">\n'
            "    <head>\n"
            '        <meta charset="UTF-8">\n'
            '        <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            "        <title>Reset Your Password - {{ site_name }}</title>\n"
            "    </head>\n"
            '    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; '
            'background-color: #0f172a;">\n'
            '        <table width="100%" cellpadding="0" cellspacing="0" '
            'style="background-color: #0f172a; padding: 40px 20px;">\n'
            "            <tr>\n"
            '                <td align="center">\n'
            '                    <table width="600" cellpadding="0" cellspacing="0" '
            'style="background: linear-gradient(to bottom, #1e293b, #0f172a); '
            "border-radius: 16px; overflow: hidden; "
            'box-shadow: 0 20px 50px rgba(0,0,0,0.5)">\n'
            "                        <tr>\n"
            '                            <td style="padding: 40px; text-align: center; '
            "background: linear-gradient(to right, #ef4444, #f97316); "
            'border-bottom: 4px solid #dc2626">\n'
            '                                <h1 style="margin: 0; color: #ffffff; '
            'font-size: 32px; font-weight: bold;">✨ {{ site_name }}</h1>\n'
            "                            </td>\n"
            "                        </tr>\n"
            "                        <tr>\n"
            '                            <td style="padding: 40px; color: #cbd5e1;">\n'
            '                                <h2 style="color: #ffffff; margin-top: 0; '
            'font-size: 24px;">Reset Your Password</h2>\n'
            '                                <p style="font-size: 16px; line-height: 1.6; '
            'margin: 20px 0;">\n'
            "                                    Hi {{ username }},<br>\n"
            "                                    You requested to reset your password for "
            "your {{ site_name }} account. Click the button below to set a new "
            "password.\n"
            "                                </p>\n"
            '                                <table width="100%" cellpadding="0" '
            'cellspacing="0" style="margin: 30px 0;">\n'
            "                                    <tr>\n"
            '                                        <td align="center">\n'
            '                                            <a href="{{ password_reset_url }}" '
            'style="display: inline-block; padding: 16px 40px; '
            "background: linear-gradient(to right, #ef4444, #f97316); "
            "color: #ffffff; text-decoration: none; border-radius: 8px; "
            'font-weight: bold; font-size: 16px">Reset Password</a>\n'
            "                                        </td>\n"
            "                                    </tr>\n"
            "                                </table>\n"
            '                                <p style="font-size: 14px; color: #94a3b8; '
            'margin: 20px 0;">\n'
            "                                    Or copy and paste this link into your browser:\n"
            "                                    <br>\n"
            '                                    <a href="{{ password_reset_url }}" '
            'style="color: #f97316; word-break: break-all;">'
            "{{ password_reset_url }}</a>\n"
            "                                </p>\n"
            '                                <p style="font-size: 14px; color: #94a3b8; '
            'margin-top: 30px;">\n'
            "                                    This link will expire in {{ expiration_hours }} "
            " hours.\n"
            "                                    <br>\n"
            "                                    If you did not request this password reset, "
            "please ignore this email.\n"
            "                                </p>\n"
            "                            </td>\n"
            "                        </tr>\n"
            "                        <tr>\n"
            '                            <td style="padding: 30px; text-align: center; '
            'background-color: #0f172a; border-top: 1px solid #334155">\n'
            '                                <p style="margin: 0; color: #64748b; '
            'font-size: 14px;">© 2025 {{ site_name }} Nepal. All rights reserved.'
            "</p>\n"
            "                            </td>\n"
            "                        </tr>\n"
            "                    </table>\n"
            "                </td>\n"
            "            </tr>\n"
            "        </table>\n"
            "    </body>\n"
            "</html>"
        )

    @classmethod
    def _get_password_reset_text(cls):
        """Generate password reset text content"""
        return (
            "Hi {{ username }},\n\n"
            "You requested to reset your password for your {{ site_name }} "
            "account. Click the link below to reset your password:\n\n"
            "{{ password_reset_url }}\n\n"
            "This link will expire in {{ expiration_hours }} hours.\n\n"
            "If you did not request this password reset, please ignore this email.\n\n"
            "© 2025 {{ site_name }} Nepal. All rights reserved."
        )

    def handle(self, *args, **options):
        force = options.get("force", False)

        # Define email templates
        templates = [
            # Newsletter Templates
            {
                "name": "newsletter_verification",
                "template_type": "newsletter_verification",
                "subject": ("Verify your {{ site_name }} Newsletter Subscription"),
                "html_content": self._get_newsletter_verification_html(),
                "text_content": self._get_newsletter_verification_text(),
            },
            {
                "name": "newsletter_welcome",
                "template_type": "newsletter_welcome",
                "subject": "Welcome to {{ site_name }} Newsletter!",
                "html_content": self._get_newsletter_welcome_html(),
                "text_content": self._get_newsletter_welcome_text(),
            },
            # Account Templates
            {
                "name": "email_verification",
                "template_type": "email_verification",
                "subject": "Verify your {{ site_name }} account email",
                "html_content": self._get_email_verification_html(),
                "text_content": self._get_email_verification_text(),
            },
            {
                "name": "password_reset",
                "template_type": "password_reset",
                "subject": "Reset your {{ site_name }} password",
                "html_content": self._get_password_reset_html(),
                "text_content": self._get_password_reset_text(),
            },
        ]

        created_count = 0
        updated_count = 0

        with transaction.atomic():
            for template_data in templates:
                name = template_data["name"]

                try:
                    # Check if template exists
                    existing_template = EmailTemplate.objects.get(name=name)

                    if force:
                        # Update existing template
                        for field, value in template_data.items():
                            setattr(existing_template, field, value)
                        existing_template.save()
                        updated_count += 1
                        self.stdout.write(self.style.WARNING(f"Updated existing template: {name}"))
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Template "{name}" already exists. Use --force to update.'
                            )
                        )

                except EmailTemplate.DoesNotExist:
                    # Create new template
                    EmailTemplate.objects.create(**template_data)
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Created new template: {name}"))

        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f"\\nSeeding completed!\\nCreated: {created_count}\\nUpdated: {updated_count}"
            )
        )

        if created_count > 0 or updated_count > 0:
            self.stdout.write(
                "\\nTo view templates, visit the Django admin at /admin/emails/emailtemplate/"
            )
