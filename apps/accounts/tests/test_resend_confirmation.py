from unittest.mock import patch

from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse

from .base import BaseTestCase


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
)
class ResendConfirmationViewTests(BaseTestCase):
    def setUp(self):
        self.login_url = reverse("accounts:login")
        cache.clear()

    @patch("apps.accounts.views.send_verification_email")
    def test_resend_confirmation_unverified_user(self, mock_send_email):
        user = self.create_user(verified=False)
        resend_url = reverse("accounts:resend_confirmation", args=[user.id])

        response = self.client.post(resend_url)

        mock_send_email.assert_called_once_with(user)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn("new confirmation email has been sent", str(messages[0]))
        self.assertRedirects(
            response, reverse("accounts:email_confirmation_sent_view", args=[user.id])
        )

    def test_resend_confirmation_verified_user(self):
        user = self.create_user(verified=True)
        resend_url = reverse("accounts:resend_confirmation", args=[user.id])

        response = self.client.post(resend_url)

        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn("already verified", str(messages[0]))
        self.assertRedirects(response, self.login_url)

    def test_resend_confirmation_invalid_user(self):
        resend_url = reverse("accounts:resend_confirmation", args=[99999])
        response = self.client.post(resend_url)
        self.assertEqual(response.status_code, 404)

    @patch("apps.accounts.views.send_verification_email")
    def test_resend_confirmation_rate_limit(self, mock_send_email):
        user = self.create_user(verified=False)
        resend_url = reverse("accounts:resend_confirmation", args=[user.id])

        for _ in range(3):
            self.client.post(resend_url)

        response = self.client.post(resend_url)
        self.assertEqual(response.status_code, 429)
