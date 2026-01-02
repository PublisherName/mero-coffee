from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class BaseTestCase(TestCase):
    """Base test case with common setup for all account tests"""

    @classmethod
    def setUpTestData(cls):
        cls.user_password = "testpass123"
        cls.user_model = User

    def create_user(self, username="testuser", email="test@example.com", is_verified=True):
        """Helper method to create a test user"""
        return User.objects.create_user(
            username=username,
            email=email,
            password=self.user_password,
            is_active=True,
            is_verified=is_verified,
        )

    @staticmethod
    def mock_turnstile_response(data):
        """Helper to add turnstile response to POST data"""
        data["cf-turnstile-response"] = "dummy-token"
        return data
