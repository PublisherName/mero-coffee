from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse

from .base import BaseTestCase

User = get_user_model()


class LowercaseNormalizationTests(BaseTestCase):
    """Test suite for username and email lowercase normalization"""

    def setUp(self):
        super().setUp()
        self.signup_url = reverse("accounts:signup")
        self.login_url = reverse("accounts:login")

    # ========== Model Layer Tests ==========

    def test_model_save_normalizes_username_to_lowercase(self):
        """Test that User.save() converts username to lowercase"""
        user = User.objects.create_user(
            username="TestUser",
            email="test@example.com",
            password="testpass123",
        )
        self.assertEqual(user.username, "testuser")

    def test_model_save_normalizes_email_to_lowercase(self):
        """Test that User.save() converts email to lowercase"""
        user = User.objects.create_user(
            username="testuser",
            email="Test@Example.COM",
            password="testpass123",
        )
        self.assertEqual(user.email, "test@example.com")

    def test_model_save_normalizes_mixed_case_username_and_email(self):
        """Test that both username and email are normalized together"""
        user = User.objects.create_user(
            username="MixedCaseUser",
            email="MixedCase@Example.COM",
            password="testpass123",
        )
        self.assertEqual(user.username, "mixedcaseuser")
        self.assertEqual(user.email, "mixedcase@example.com")

    def test_model_update_normalizes_username(self):
        """Test that updating username also normalizes it"""
        user = self.create_user()
        user.username = "UpdatedUser"
        user.save()
        user.refresh_from_db()
        self.assertEqual(user.username, "updateduser")

    def test_model_update_normalizes_email(self):
        """Test that updating email also normalizes it"""
        user = self.create_user()
        user.email = "Updated@Example.COM"
        user.save()
        user.refresh_from_db()
        self.assertEqual(user.email, "updated@example.com")

    # ========== Form Layer Tests - SignUp ==========

    @patch("apps.emails.services.EmailService.send_template_email")
    @patch("turnstile.fields.TurnstileField.validate")
    def test_signup_form_normalizes_username_uppercase(self, mock_turnstile, mock_email):
        """Test signup with uppercase username is normalized"""
        mock_turnstile.return_value = True

        self.client.post(
            self.signup_url,
            self.mock_turnstile_response(
                {
                    "username": "UPPERCASE",
                    "email": "test@example.com",
                    "first_name": "Test",
                    "last_name": "User",
                    "password1": "securepass123",
                    "password2": "securepass123",
                }
            ),
        )

        self.assertEqual(User.objects.count(), 1)
        user = User.objects.first()
        self.assertEqual(user.username, "uppercase")

    @patch("apps.emails.services.EmailService.send_template_email")
    @patch("turnstile.fields.TurnstileField.validate")
    def test_signup_form_normalizes_email_mixed_case(self, mock_turnstile, mock_email):
        """Test signup with mixed case email is normalized"""
        mock_turnstile.return_value = True

        self.client.post(
            self.signup_url,
            self.mock_turnstile_response(
                {
                    "username": "testuser",
                    "email": "Test@Example.COM",
                    "first_name": "Test",
                    "last_name": "User",
                    "password1": "securepass123",
                    "password2": "securepass123",
                }
            ),
        )

        self.assertEqual(User.objects.count(), 1)
        user = User.objects.first()
        self.assertEqual(user.email, "test@example.com")

    @patch("turnstile.fields.TurnstileField.validate")
    def test_signup_prevents_duplicate_username_different_case(self, mock_turnstile):
        """Test that signup prevents duplicate username with different case"""
        mock_turnstile.return_value = True
        self.create_user(username="testuser", email="first@example.com")

        response = self.client.post(
            self.signup_url,
            self.mock_turnstile_response(
                {
                    "username": "TestUser",
                    "email": "second@example.com",
                    "first_name": "Test",
                    "last_name": "User",
                    "password1": "securepass123",
                    "password2": "securepass123",
                }
            ),
        )

        self.assertEqual(User.objects.count(), 1)
        self.assertContains(response, "A user with that username already exists")

    @patch("turnstile.fields.TurnstileField.validate")
    def test_signup_prevents_duplicate_email_different_case(self, mock_turnstile):
        """Test that signup prevents duplicate email with different case"""
        mock_turnstile.return_value = True
        self.create_user(username="firstuser", email="test@example.com")

        response = self.client.post(
            self.signup_url,
            self.mock_turnstile_response(
                {
                    "username": "seconduser",
                    "email": "Test@Example.COM",
                    "first_name": "Test",
                    "last_name": "User",
                    "password1": "securepass123",
                    "password2": "securepass123",
                }
            ),
        )

        self.assertEqual(User.objects.count(), 1)
        self.assertContains(response, "A user with that email already exists")

    # ========== Login Tests - Case Insensitive ==========

    @patch("turnstile.fields.TurnstileField.validate")
    def test_login_with_uppercase_username(self, mock_turnstile):
        """Test login with uppercase username works"""
        mock_turnstile.return_value = True
        self.create_user(username="testuser", email="test@example.com")

        response = self.client.post(
            self.login_url,
            self.mock_turnstile_response({"username": "TESTUSER", "password": self.user_password}),
        )

        self.assertTrue("_auth_user_id" in self.client.session)
        self.assertRedirects(response, reverse("dashboard:dashboard"))

    @patch("turnstile.fields.TurnstileField.validate")
    def test_login_with_mixed_case_username(self, mock_turnstile):
        """Test login with mixed case username works"""
        mock_turnstile.return_value = True
        self.create_user(username="testuser", email="test@example.com")

        response = self.client.post(
            self.login_url,
            self.mock_turnstile_response({"username": "TestUser", "password": self.user_password}),
        )

        self.assertTrue("_auth_user_id" in self.client.session)
        self.assertRedirects(response, reverse("dashboard:dashboard"))

    @patch("turnstile.fields.TurnstileField.validate")
    def test_login_with_uppercase_email(self, mock_turnstile):
        """Test login with uppercase email works"""
        mock_turnstile.return_value = True
        self.create_user(username="testuser", email="test@example.com")

        response = self.client.post(
            self.login_url,
            self.mock_turnstile_response(
                {"username": "TEST@EXAMPLE.COM", "password": self.user_password}
            ),
        )

        self.assertTrue("_auth_user_id" in self.client.session)
        self.assertRedirects(response, reverse("dashboard:dashboard"))

    @patch("turnstile.fields.TurnstileField.validate")
    def test_login_with_mixed_case_email(self, mock_turnstile):
        """Test login with mixed case email works"""
        mock_turnstile.return_value = True
        self.create_user(username="testuser", email="test@example.com")

        response = self.client.post(
            self.login_url,
            self.mock_turnstile_response(
                {"username": "Test@Example.Com", "password": self.user_password}
            ),
        )

        self.assertTrue("_auth_user_id" in self.client.session)
        self.assertRedirects(response, reverse("dashboard:dashboard"))

    # ========== Edge Cases ==========

    def test_empty_username_handled_gracefully(self):
        """Test that empty username doesn't cause errors"""
        user = User(username="", email="test@example.com")
        user.save()
        self.assertEqual(user.username, "")

    def test_empty_email_handled_gracefully(self):
        """Test that empty email doesn't cause errors"""
        user = User(username="testuser", email="")
        user.save()
        self.assertEqual(user.email, "")

    def test_all_lowercase_username_unchanged(self):
        """Test that already lowercase username remains unchanged"""
        user = User.objects.create_user(
            username="alllowercase",
            email="test@example.com",
            password="testpass123",
        )
        self.assertEqual(user.username, "alllowercase")

    def test_all_lowercase_email_unchanged(self):
        """Test that already lowercase email remains unchanged"""
        user = User.objects.create_user(
            username="testuser",
            email="alllowercase@example.com",
            password="testpass123",
        )
        self.assertEqual(user.email, "alllowercase@example.com")

    def test_special_characters_in_email_preserved(self):
        """Test that special characters in email are preserved"""
        user = User.objects.create_user(
            username="testuser",
            email="Test.User+Tag@Example.COM",
            password="testpass123",
        )
        self.assertEqual(user.email, "test.user+tag@example.com")

    # ========== Database Query Tests ==========

    def test_case_insensitive_username_lookup(self):
        """Test that username lookups are case-insensitive"""
        self.create_user(username="testuser", email="test@example.com")

        user_lower = User.objects.filter(username__iexact="testuser").first()
        user_upper = User.objects.filter(username__iexact="TESTUSER").first()
        user_mixed = User.objects.filter(username__iexact="TestUser").first()

        self.assertIsNotNone(user_lower)
        self.assertIsNotNone(user_upper)
        self.assertIsNotNone(user_mixed)
        self.assertEqual(user_lower.id, user_upper.id)
        self.assertEqual(user_lower.id, user_mixed.id)

    def test_case_insensitive_email_lookup(self):
        """Test that email lookups are case-insensitive"""
        self.create_user(username="testuser", email="test@example.com")

        user_lower = User.objects.filter(email__iexact="test@example.com").first()
        user_upper = User.objects.filter(email__iexact="TEST@EXAMPLE.COM").first()
        user_mixed = User.objects.filter(email__iexact="Test@Example.Com").first()

        self.assertIsNotNone(user_lower)
        self.assertIsNotNone(user_upper)
        self.assertIsNotNone(user_mixed)
        self.assertEqual(user_lower.id, user_upper.id)
        self.assertEqual(user_lower.id, user_mixed.id)
