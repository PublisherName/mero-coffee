from unittest.mock import patch

from django.urls import reverse

from .base import BaseTestCase


class LoginViewTests(BaseTestCase):
    def setUp(self):
        self.login_url = reverse("accounts:login")
        self.dashboard_url = reverse("dashboard:dashboard")
        self.user = self.create_user()

    @patch("turnstile.fields.TurnstileField.validate")
    def test_login_with_username_success(self, mock_turnstile):
        mock_turnstile.return_value = True
        response = self.client.post(
            self.login_url,
            self.mock_turnstile_response({"username": "testuser", "password": self.user_password}),
        )
        self.assertTrue("_auth_user_id" in self.client.session)
        self.assertRedirects(response, self.dashboard_url)

    @patch("turnstile.fields.TurnstileField.validate")
    def test_login_with_email_success(self, mock_turnstile):
        mock_turnstile.return_value = True
        response = self.client.post(
            self.login_url,
            self.mock_turnstile_response(
                {"username": "test@example.com", "password": self.user_password}
            ),
        )
        self.assertTrue("_auth_user_id" in self.client.session)
        self.assertRedirects(response, self.dashboard_url)

    @patch("turnstile.fields.TurnstileField.validate")
    def test_login_invalid_credentials(self, mock_turnstile):
        mock_turnstile.return_value = True
        response = self.client.post(
            self.login_url,
            self.mock_turnstile_response({"username": "testuser", "password": "wrongpassword"}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password")

    @patch("turnstile.fields.TurnstileField.validate")
    def test_login_unverified_user(self, mock_turnstile):
        mock_turnstile.return_value = True
        self.user.is_verified = False
        self.user.save()
        response = self.client.post(
            self.login_url,
            self.mock_turnstile_response({"username": "testuser", "password": self.user_password}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please verify your email before logging in.")

    @patch("turnstile.fields.TurnstileField.validate")
    def test_login_non_creator_user(self, mock_turnstile):
        mock_turnstile.return_value = True
        self.user.role = self.user_model.Roles.SUPPORTER
        self.user.save()
        response = self.client.post(
            self.login_url,
            self.mock_turnstile_response({"username": "testuser", "password": self.user_password}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Access is restricted to creators only")

    @patch("turnstile.fields.TurnstileField.validate")
    def test_login_turnstile_failure(self, mock_turnstile):
        mock_turnstile.return_value = False
        response = self.client.post(
            self.login_url,
            self.mock_turnstile_response({"username": "testuser", "password": self.user_password}),
        )
        self.assertEqual(response.status_code, 302)

    def test_login_get_request(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")

    def test_login_redirect_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.login_url)
        self.assertRedirects(response, self.dashboard_url)
