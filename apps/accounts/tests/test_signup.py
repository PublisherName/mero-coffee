from unittest.mock import patch

from django.urls import reverse

from .base import BaseTestCase


class SignUpViewTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.signup_url = reverse("accounts:signup")
        self.dashboard_url = reverse("dashboard:dashboard")

        self.base_signup_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "password1": "securepass123",
            "password2": "securepass123",
        }

    def _post_signup(self, overrides=None):
        data = self.base_signup_data.copy()
        if overrides:
            data.update(overrides)
        return self.client.post(
            self.signup_url,
            self.mock_turnstile_response(data),
        )

    @patch("apps.accounts.views.send_verification_email")
    @patch("turnstile.fields.TurnstileField.validate")
    def test_signup_success(self, mock_turnstile, mock_send_email):
        mock_turnstile.return_value = True

        response = self._post_signup()

        self.assertEqual(self.user_model.objects.count(), 1)
        user = self.user_model.objects.first()
        self.assertEqual(user.username, self.base_signup_data["username"])
        self.assertFalse(user.is_active)
        self.assertFalse(user.verified)
        mock_send_email.assert_called_once_with(user)

        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn("confirmation email has been sent", str(messages[0]))
        self.assertRedirects(
            response, reverse("accounts:email_confirmation_sent_view", args=[user.id])
        )

    @patch("turnstile.fields.TurnstileField.validate")
    def test_signup_password_mismatch(self, mock_turnstile):
        mock_turnstile.return_value = True

        response = self._post_signup(
            {"password2": "differentpass123"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user_model.objects.count(), 0)
        self.assertContains(response, "Passwords don&#x27;t match")

        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn("correct the errors", str(messages[0]))

    @patch("turnstile.fields.TurnstileField.validate")
    def test_signup_duplicate_username(self, mock_turnstile):
        mock_turnstile.return_value = True
        self.create_user(username="existinguser", email="existing@example.com")

        response = self._post_signup(
            {
                "username": "existinguser",
                "email": "new@example.com",
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user_model.objects.count(), 1)
        self.assertContains(
            response,
            "A user with that username already exists.",
        )

        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn("correct the errors", str(messages[0]))

    @patch("turnstile.fields.TurnstileField.validate")
    def test_signup_turnstile_failure(self, mock_turnstile):
        mock_turnstile.return_value = False

        response = self._post_signup()
        self.assertEqual(response.status_code, 302)

    def test_signup_get_request(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "signup.html")

    def test_signup_redirect_authenticated_user(self):
        user = self.create_user()
        self.client.force_login(user)

        response = self.client.get(self.signup_url)

        self.assertRedirects(response, self.dashboard_url)
