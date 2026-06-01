from typing import ClassVar
from unittest.mock import patch

from django.conf import settings
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse

from .base import BaseTestCase


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
    RATELIMIT_ENABLE=False,
)
class ActivateEmailViewTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.activate_url = reverse("accounts:activate_email")
        cache.clear()

    def test_activate_email_get(self):
        """Test GET request renders the activate email form"""
        response = self.client.get(self.activate_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "activate_email.html")
        self.assertIn("form", response.context)

    @patch("apps.emails.services.EmailService.send_template_email")
    def test_activate_email_valid_email(self, mock_send_email):
        """Test POST with valid email redirects to email confirmation sent page"""
        user = self.create_user(is_verified=False)
        data = self.mock_turnstile_response({"email": user.email})

        response = self.client.post(self.activate_url, data, follow=True)

        self.assertRedirects(
            response, reverse("accounts:email_confirmation_sent_view", args=[user.id])
        )
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args
        self.assertEqual(call_args[1]["template_name"], "email_verification")
        self.assertEqual(call_args[1]["recipient"], user.email)
        self.assertIn("verification_url", call_args[1]["context"])

    @patch("apps.emails.services.EmailService.send_template_email")
    def test_activate_email_valid_email_case_insensitive(self, mock_send_email):
        """Test POST with valid email redirects to email confirmation sent page"""
        user = self.create_user(is_verified=False, email="Test@Example.Com")
        data = self.mock_turnstile_response({"email": "test@example.com"})

        response = self.client.post(self.activate_url, data, follow=True)

        self.assertRedirects(
            response, reverse("accounts:email_confirmation_sent_view", args=[user.id])
        )
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args
        self.assertEqual(call_args[1]["template_name"], "email_verification")
        self.assertEqual(call_args[1]["recipient"], user.email)
        self.assertIn("verification_url", call_args[1]["context"])

    def test_activate_email_user_not_found(self):
        """Test POST with non-existent email shows error message"""
        data = self.mock_turnstile_response({"email": "nonexistent@example.com"})

        response = self.client.post(self.activate_url, data)

        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn("No account found with this email address", str(messages[0]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "activate_email.html")

    def test_activate_email_invalid_form(self):
        """Test POST with invalid form data"""
        data = self.mock_turnstile_response({"email": "invalid-email"})

        response = self.client.post(self.activate_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "activate_email.html")
        self.assertTrue(response.context["form"].errors)

    def test_activate_email_missing_turnstile(self):
        """Test POST without turnstile token"""
        data = {"email": "test@example.com"}

        response = self.client.post(self.activate_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "activate_email.html")
        self.assertTrue(response.context["form"].errors)

    TEST_MIDDLEWARE: ClassVar[list] = list(settings.MIDDLEWARE)
    TEST_MIDDLEWARE.insert(-1, "django_ratelimit.middleware.RatelimitMiddleware")

    @override_settings(
        RATELIMIT_ENABLE=True,
        RATELIMIT_RATE="3/30m",
        MIDDLEWARE=TEST_MIDDLEWARE,
    )
    def test_activate_email_rate_limit(self):
        """Test rate limiting for activate email view"""
        user = self.create_user(is_verified=False)
        data = self.mock_turnstile_response({"email": user.email})

        for _ in range(3):
            self.client.post(self.activate_url, data)

        response = self.client.post(self.activate_url, data)
        self.assertEqual(response.status_code, 429)
