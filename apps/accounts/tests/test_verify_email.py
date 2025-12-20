from unittest.mock import patch

from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse

from .base import BaseTestCase


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
)
class VerifyEmailViewTests(BaseTestCase):
    def setUp(self):
        self.verify_url = reverse("accounts:verify_email")
        self.login_url = reverse("accounts:login")
        self.token = {"token": "valid_token"}
        cache.clear()

    def test_verify_email_no_token(self):
        response = self.client.get(self.verify_url)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn("Invalid verification link", str(messages[0]))
        self.assertRedirects(response, self.login_url)

    @patch("apps.accounts.views.verify_email_verification_token")
    def test_verify_email_invalid_token(self, mock_verify_token):
        mock_verify_token.return_value = None
        response = self.client.get(self.verify_url, self.token)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn("invalid or expired", str(messages[0]))
        self.assertRedirects(response, self.login_url)

    @patch("apps.accounts.views.verify_email_verification_token")
    def test_verify_email_user_not_found(self, mock_verify_token):
        mock_verify_token.return_value = 99999
        response = self.client.get(self.verify_url, self.token)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn("User not found", str(messages[0]))
        self.assertRedirects(response, self.login_url)

    @patch("apps.accounts.views.verify_email_verification_token")
    def test_verify_email_already_verified(self, mock_verify_token):
        user = self.create_user(verified=True)
        mock_verify_token.return_value = user.id
        response = self.client.get(self.verify_url, self.token)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn("already verified", str(messages[0]))
        self.assertRedirects(response, self.login_url)

    @patch("apps.accounts.views.verify_email_verification_token")
    def test_verify_email_success(self, mock_verify_token):
        user = self.create_user(verified=False)
        user.is_active = False
        user.save()
        mock_verify_token.return_value = user.id

        response = self.client.get(self.verify_url, self.token)

        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(user.verified)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn("verified successfully", str(messages[0]))
        self.assertRedirects(response, self.login_url)

    @patch("apps.accounts.views.verify_email_verification_token")
    def test_verify_email_rate_limit(self, mock_verify_token):
        user = self.create_user(verified=False)
        mock_verify_token.return_value = user.id

        for _ in range(3):
            self.client.get(self.verify_url, self.token)

        response = self.client.get(self.verify_url, self.token)
        self.assertEqual(response.status_code, 429)
