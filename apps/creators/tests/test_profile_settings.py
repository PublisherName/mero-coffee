from unittest.mock import patch

from django.urls import reverse

from .base import BaseCreatorsTestCase


class ProfileSettingsViewTests(BaseCreatorsTestCase):
    def setUp(self):
        self.user = self.create_user()
        self.url = reverse("dashboard:profile_settings")

    def test_profile_settings_login_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    @patch("apps.creators.views.get_kyc_context")
    def test_profile_settings_get_request(self, mock_kyc_context):
        mock_kyc_context.return_value = {}
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    @patch("apps.creators.views.get_kyc_context")
    def test_profile_settings_post_valid_data(self, mock_kyc_context):
        mock_kyc_context.return_value = {}
        self.client.force_login(self.user)
        data = {
            "display_name": "New Name",
            "bio": "New bio",
            "coffee_price": 150,
            "avatar_url": "https://example.com/avatar.jpg",
        }
        response = self.client.post(self.url, data)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn("saved", str(messages[0]))
        self.assertRedirects(response, self.url)

    @patch("apps.creators.views.get_kyc_context")
    def test_profile_settings_post_invalid_data(self, mock_kyc_context):
        mock_kyc_context.return_value = {}
        self.client.force_login(self.user)
        data = {"coffee_price": -100}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn("correct the errors", str(messages[0]))
