from unittest.mock import patch

from django.conf import settings
from django.core import mail
from django.test import override_settings
from django.urls import reverse

from apps.newsletter.models import NewsletterSubscriber
from apps.newsletter.tests.base import BaseNewsletterTestCase


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
    RATELIMIT_ENABLE=False,
)
class NewsletterSubscribeTestCase(BaseNewsletterTestCase):
    def test_subscribe_creates_subscriber(self):
        response = self.client.post(reverse("newsletter:subscribe"), {"email": "test@example.com"})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("core:homepage"), fetch_redirect_response=False)

        self.assert_message(response, "check your email to verify")

        self.assertEqual(NewsletterSubscriber.objects.count(), 1)
        subscriber = NewsletterSubscriber.objects.first()
        self.assertEqual(subscriber.email, "test@example.com")
        self.assertFalse(subscriber.is_verified)

    @patch("apps.newsletter.views.EmailService.send_template_email")
    def test_subscribe_sends_verification_email(self, mock_send_email):
        response = self.client.post(reverse("newsletter:subscribe"), {"email": "test@example.com"})
        self.assertEqual(response.status_code, 302)
        mock_send_email.assert_called_once()
        self.assertEqual(mock_send_email.call_args[1]["template_name"], "newsletter_verification")

    def test_subscribe_invalid_email(self):
        response = self.client.post(reverse("newsletter:subscribe"), {"email": "invalid-email"})
        self.assertEqual(response.status_code, 302)

        self.assert_message(response, "email")
        self.assertEqual(NewsletterSubscriber.objects.count(), 0)

    def test_subscribe_duplicate_email(self):
        response1 = self.client.post(
            reverse("newsletter:subscribe"), {"email": "test@example.com"}
        )
        self.assertEqual(response1.status_code, 302)

        response2 = self.client.post(
            reverse("newsletter:subscribe"), {"email": "test@example.com"}
        )
        self.assertEqual(response2.status_code, 302)

        self.assert_message(response2, "check your email")
        self.assertEqual(NewsletterSubscriber.objects.count(), 1)

    def test_verify_email_success(self):
        subscriber = NewsletterSubscriber.objects.create(email="test@example.com")
        self.assertFalse(subscriber.is_verified)

        response = self.client.get(
            reverse("newsletter:verify_email", args=[subscriber.verification_token])
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("core:homepage"), fetch_redirect_response=False)

        self.assert_message(response, "verified successfully")

        subscriber.refresh_from_db()
        self.assertTrue(subscriber.is_verified)
        self.assertIsNotNone(subscriber.verified_at)

    @patch("apps.newsletter.views.EmailService.send_template_email")
    def test_verify_email_sends_welcome_email(self, mock_send_email):
        subscriber = NewsletterSubscriber.objects.create(email="test@example.com")
        response = self.client.get(
            reverse("newsletter:verify_email", args=[subscriber.verification_token])
        )
        self.assertEqual(response.status_code, 302)
        mock_send_email.assert_called_once()
        self.assertEqual(mock_send_email.call_args[1]["template_name"], "newsletter_welcome")

    def test_verify_email_invalid_token(self):
        response = self.client.get(
            reverse("newsletter:verify_email", args=["00000000-0000-0000-0000-000000000000"])
        )
        self.assertEqual(response.status_code, 302)

        self.assert_message(response, "invalid")
        self.assertEqual(NewsletterSubscriber.objects.filter(is_verified=True).count(), 0)

    def test_verify_email_already_verified(self):
        subscriber = NewsletterSubscriber.objects.create(
            email="test@example.com", is_verified=True
        )
        response = self.client.get(
            reverse("newsletter:verify_email", args=[subscriber.verification_token])
        )
        self.assertEqual(response.status_code, 302)

        self.assert_message(response, "Your email is already verified.")
        self.assertEqual(len(mail.outbox), 0)


TEST_MIDDLEWARE = list(settings.MIDDLEWARE)
TEST_MIDDLEWARE.insert(-1, "django_ratelimit.middleware.RatelimitMiddleware")


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
    RATELIMIT_ENABLE=True,
    RATELIMIT_RATE="3/30m",
    MIDDLEWARE=TEST_MIDDLEWARE,
)
class NewsletterRateLimitTestCase(BaseNewsletterTestCase):
    def test_subscribe_rate_limit(self):
        for i in range(3):
            response = self.client.post(
                reverse("newsletter:subscribe"), {"email": f"test{i}@example.com"}
            )
            self.assertEqual(response.status_code, 302)

        response = self.client.post(
            reverse("newsletter:subscribe"), {"email": "test4@example.com"}
        )
        self.assertEqual(response.status_code, 429)

    def test_verify_email_rate_limit(self):
        subscribers = [
            NewsletterSubscriber.objects.create(email=f"test{i}@example.com") for i in range(5)
        ]

        for i in range(3):
            response = self.client.get(
                reverse("newsletter:verify_email", args=[subscribers[i].verification_token])
            )
            self.assertEqual(response.status_code, 302)

        response = self.client.get(
            reverse("newsletter:verify_email", args=[subscribers[4].verification_token])
        )
        self.assertEqual(response.status_code, 429)
