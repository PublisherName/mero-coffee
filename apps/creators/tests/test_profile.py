from unittest.mock import patch

from django.urls import reverse

from apps.payments.models import PaymentGateway

from .base import BaseCreatorsTestCase


class ProfileViewTests(BaseCreatorsTestCase):
    def setUp(self):
        self.creator = self.create_creator_profile(
            display_name="Test Creator", bio="Test bio", coffee_price=100
        )
        self.gateway = PaymentGateway.objects.create(name="eSewa", slug="esewa", is_active=True)

    def test_profile_get_request(self):
        url = reverse("creators:profile", args=[self.creator.user.username])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.creator.display_name)
        self.assertContains(response, self.creator.bio)

    @patch("apps.creators.views.uuid")
    def test_profile_post_valid_form(self, mock_uuid):
        mock_uuid.uuid4.return_value = "test-uuid"
        url = reverse("creators:profile", args=[self.creator.user.username])
        data = {
            "supporter_name": "John Doe",
            "amount": 100,
            "payment_provider": "esewa",
            "message": "Keep up the good work!",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual("/checkout/test-uuid/", response.url)

    def test_profile_post_invalid_form(self):
        url = reverse("creators:profile", args=[self.creator.user.username])
        data = {"supporter_name": "", "amount": 50, "payment_provider": "esewa"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn("correct the errors", str(messages[0]))

    def test_profile_post_amount_less_than_coffee_price(self):
        url = reverse("creators:profile", args=[self.creator.user.username])
        data = {
            "supporter_name": "John Doe",
            "amount": 50,
            "payment_provider": "esewa",
            "message": "Support",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "at least Rs. 100")

    def test_profile_user_not_found(self):
        url = reverse("creators:profile", args=["nonexistent"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
