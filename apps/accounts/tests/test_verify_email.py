from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse

from .base import BaseTestCase


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
    RATELIMIT_ENABLE=False,
)
class VerifyEmailViewTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.login_url = reverse("accounts:login")
        cache.clear()

    @classmethod
    def _build_url(cls, user, token):
        uidb64 = user.pk
        return reverse(
            "accounts:verify_email",
            kwargs={"uidb64": uidb64, "token": token},
        )

    def test_verify_email_invalid_uid(self):
        url = reverse(
            "accounts:verify_email",
            kwargs={"uidb64": "invalid-uid", "token": "some-token"},
        )
        response = self.client.get(url)

        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn("Invalid verification link", str(messages[0]))
        self.assertRedirects(response, self.login_url)

    @patch("apps.accounts.views.default_token_generator")
    def test_verify_email_invalid_token(self, mock_token_gen):
        user = self.create_user(is_verified=False)
        uidb64 = user.pk
        token = "invalid-token"

        mock_token_gen.check_token.return_value = False

        url = reverse(
            "accounts:verify_email",
            kwargs={"uidb64": uidb64, "token": token},
        )
        response = self.client.get(url)

        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn("invalid or expired", str(messages[0]))
        self.assertRedirects(response, self.login_url)

    def test_verify_email_user_not_found(self):
        uidb64 = 99999
        token = "some-token"

        url = reverse(
            "accounts:verify_email",
            kwargs={"uidb64": uidb64, "token": token},
        )
        response = self.client.get(url)

        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn("Invalid verification link", str(messages[0]))
        self.assertRedirects(response, self.login_url)

    @patch("apps.accounts.views.default_token_generator")
    def test_verify_email_already_verified(self, mock_token_gen):
        user = self.create_user(is_verified=True)
        user.save()

        uidb64 = user.pk
        token = "valid-token"
        mock_token_gen.check_token.return_value = True

        url = reverse(
            "accounts:verify_email",
            kwargs={"uidb64": uidb64, "token": token},
        )
        response = self.client.get(url)

        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn("already verified", str(messages[0]))
        self.assertRedirects(response, self.login_url)

    def test_verify_email_success(self):
        user = self.create_user(is_verified=False)
        user.save()

        uidb64 = user.pk
        token = default_token_generator.make_token(user)

        url = reverse(
            "accounts:verify_email",
            kwargs={"uidb64": uidb64, "token": token},
        )
        response = self.client.get(url)

        user.refresh_from_db()
        self.assertTrue(user.is_verified)

        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn("verified successfully", str(messages[0]))
        self.assertRedirects(response, self.login_url)

    TEST_MIDDLEWARE = list(settings.MIDDLEWARE)
    TEST_MIDDLEWARE.insert(-1, "django_ratelimit.middleware.RatelimitMiddleware")

    @override_settings(
        RATELIMIT_ENABLE=True,
        RATELIMIT_RATE="3/30m",
        MIDDLEWARE=TEST_MIDDLEWARE,
    )
    def test_verify_email_rate_limit(self):
        user = self.create_user(is_verified=False)
        uidb64 = user.pk
        token = default_token_generator.make_token(user)

        url = reverse(
            "accounts:verify_email",
            kwargs={"uidb64": uidb64, "token": token},
        )

        for _ in range(3):
            self.client.get(url)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 429)
