from unittest.mock import patch

from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .base import BaseTestCase


class PasswordResetTests(BaseTestCase):
    """Tests for password reset functionality"""

    def setUp(self):
        self.password_reset_url = reverse("accounts:password_reset")
        self.password_reset_done_url = reverse("accounts:password_reset_done")

    @patch("apps.emails.services.EmailService.send_template_email")
    def test_password_reset_request_existing_user(self, mock_send_email):
        """Test password reset request for existing user sends email"""
        user = self.create_user()
        response = self.client.post(self.password_reset_url, {"email": user.email})

        self.assertRedirects(response, self.password_reset_done_url)
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args
        self.assertEqual(call_args[1]["template_name"], "password_reset")
        self.assertEqual(call_args[1]["recipient"], user.email)
        self.assertIn("password_reset_url", call_args[1]["context"])

    @patch("apps.emails.services.EmailService.send_template_email")
    def test_password_reset_request_nonexistent_user(self, mock_send_email):
        """Test password reset request for non-existent user still redirects (security)"""
        response = self.client.post(self.password_reset_url, {"email": "nonexistent@example.com"})

        self.assertRedirects(response, self.password_reset_done_url)
        mock_send_email.assert_not_called()

    def test_password_reset_get_request(self):
        """Test GET request to password reset page"""
        response = self.client.get(self.password_reset_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "password_reset_form.html")


class PasswordResetConfirmTests(BaseTestCase):
    """Tests for password reset confirmation and email verification"""

    def setUp(self):
        self.new_password = "newpassword123"

    @classmethod
    def _get_password_reset_confirm_url(cls, user):
        """Helper to generate password reset confirm URL"""
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        return reverse("accounts:password_reset_confirm", kwargs={"uidb64": uid, "token": token})

    def test_password_reset_confirm_unverified_user_verifies_email(self):
        """Test that password reset for unverified user also verifies their email"""
        user = self.create_user(is_verified=False)
        old_password = self.user_password

        reset_url = self._get_password_reset_confirm_url(user)

        response = self.client.get(reset_url)
        self.assertEqual(response.status_code, 302)  # Redirects to set-password form

        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            response.wsgi_request.path,
            {"new_password1": self.new_password, "new_password2": self.new_password},
        )

        user.refresh_from_db()

        self.assertTrue(user.check_password(self.new_password))
        self.assertFalse(user.check_password(old_password))
        self.assertTrue(user.is_verified)

        messages = list(response.wsgi_request._messages)
        self.assertTrue(
            any("email has been verified" in str(message).lower() for message in messages)
        )

    def test_password_reset_confirm_verified_user_stays_verified(self):
        """Test that password reset for verified user keeps them verified"""
        user = self.create_user(is_verified=True)
        old_password = self.user_password

        reset_url = self._get_password_reset_confirm_url(user)
        response = self.client.get(reset_url)
        self.assertEqual(response.status_code, 302)

        response = self.client.get(response.url)
        response = self.client.post(
            response.wsgi_request.path,
            {"new_password1": self.new_password, "new_password2": self.new_password},
        )

        user.refresh_from_db()

        self.assertTrue(user.check_password(self.new_password))
        self.assertFalse(user.check_password(old_password))

        self.assertTrue(user.is_verified)

    def test_password_reset_confirm_invalid_token(self):
        """Test password reset with invalid token fails"""
        user = self.create_user(is_verified=False)

        invalid_url = reverse(
            "accounts:password_reset_confirm",
            kwargs={
                "uidb64": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": "invalid-token",
            },
        )

        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 200)

        user.refresh_from_db()
        self.assertFalse(user.is_verified)

    def test_unverified_user_can_login_after_password_reset(self):
        """Test complete flow: unverified user resets password and can login"""
        user = self.create_user(username="unverifieduser", is_verified=False)

        reset_url = self._get_password_reset_confirm_url(user)

        response = self.client.get(reset_url)
        response = self.client.get(response.url)
        self.client.post(
            response.wsgi_request.path,
            {"new_password1": self.new_password, "new_password2": self.new_password},
        )

        user.refresh_from_db()
        self.assertTrue(user.is_verified)

        login_url = reverse("accounts:login")
        with patch("turnstile.fields.TurnstileField.validate", return_value=True):
            response = self.client.post(
                login_url,
                self.mock_turnstile_response(
                    {"username": "unverifieduser", "password": self.new_password}
                ),
            )

        self.assertTrue("_auth_user_id" in self.client.session)
        self.assertRedirects(response, reverse("dashboard:dashboard"))

    def test_password_reset_confirm_mismatched_passwords(self):
        """Test password reset with mismatched passwords fails"""
        user = self.create_user(is_verified=False)

        reset_url = self._get_password_reset_confirm_url(user)

        response = self.client.get(reset_url)
        response = self.client.get(response.url)
        response = self.client.post(
            response.wsgi_request.path,
            {"new_password1": self.new_password, "new_password2": "differentpassword"},
        )

        self.assertEqual(response.status_code, 200)

        user.refresh_from_db()
        self.assertFalse(user.is_verified)
        self.assertTrue(user.check_password(self.user_password))
