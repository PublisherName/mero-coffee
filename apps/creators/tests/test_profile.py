from unittest.mock import patch

from django.conf import settings
from django.urls import reverse

from apps.payments.models import PaymentGateway

from .base import BaseCreatorsTestCase


class ProfileViewTests(BaseCreatorsTestCase):
    def setUp(self):
        self.verified_creator = self.create_creator_profile(
            display_name="Verified Creator",
            bio="Verified bio",
            coffee_price=max(settings.MINIMUM_DONATION_AMOUNT, 100),
        )
        self.unverified_creator = self.create_creator_profile(
            user=self.create_user(
                username="unverified", email="unverified@example.com", is_verified=False
            ),
            display_name="Unverified Creator",
            bio="Unverified bio",
            coffee_price=max(settings.MINIMUM_DONATION_AMOUNT, 100),
        )
        self.gateway = PaymentGateway.objects.create(name="eSewa", slug="esewa", is_active=True)

    def test_verified_profile_public_access(self):
        """KYC verified profiles should be publicly accessible"""
        url = reverse("creators:profile", args=[self.verified_creator.user.username])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.verified_creator.display_name)
        self.assertContains(response, self.verified_creator.bio)

    def test_unverified_profile_private_for_non_owner(self):
        """Non-KYC verified profiles should return 400 for non-owners"""
        url = reverse("creators:profile", args=[self.unverified_creator.user.username])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertIn("This profile is private", response.content.decode())

    def test_unverified_profile_owner_can_view(self):
        """Profile owners should be able to view their private profile"""
        self.client.force_login(self.unverified_creator.user)
        url = reverse("creators:profile", args=[self.unverified_creator.user.username])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.unverified_creator.display_name)
        self.assertContains(response, self.unverified_creator.bio)
        self.assertContains(response, "This profile is private and only visible to the owner.")

    def test_unverified_profile_owner_can_support(self):
        """Unverified profile owners should not be able to support themselves"""
        self.client.force_login(self.unverified_creator.user)
        url = reverse("creators:profile", args=[self.unverified_creator.user.username])
        data = {
            "supporter_name": "Self Support",
            "amount": 100,
            "payment_provider": "esewa",
            "message": "Supporting my own work!",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "This profile cannot receive support until KYC verification is completed."
        )

    def test_profile_user_not_found(self):
        """Non-existent profiles should return 400"""
        url = reverse("creators:profile", args=["nonexistent"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Profile not found", response.content.decode())

    @patch("apps.creators.views.uuid")
    def test_verified_profile_post_valid_form(self, mock_uuid):
        """Test form submission for verified profiles"""
        mock_uuid.uuid4.return_value = "test-uuid"
        url = reverse("creators:profile", args=[self.verified_creator.user.username])
        data = {
            "supporter_name": "John Doe",
            "amount": settings.MINIMUM_DONATION_AMOUNT,
            "payment_provider": "esewa",
            "message": "Keep up the good work!",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual("/checkout/test-uuid/", response.url)

    def test_verified_profile_post_invalid_form(self):
        """Test invalid form submission for verified profiles"""
        url = reverse("creators:profile", args=[self.verified_creator.user.username])
        data = {"supporter_name": "", "amount": 50, "payment_provider": "esewa"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "correct the following errors")

    def test_verified_profile_post_amount_less_than_coffee_price(self):
        """Test amount validation for verified profiles"""
        url = reverse("creators:profile", args=[self.verified_creator.user.username])
        data = {
            "supporter_name": "John Doe",
            "amount": settings.MINIMUM_DONATION_AMOUNT - 1,
            "payment_provider": "esewa",
            "message": "Support",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "at least Rs.")

    def test_different_user_cannot_access_private_profile(self):
        """Different authenticated user should not access private profile"""
        other_user = self.create_user(
            username="other", email="other@example.com", is_verified=True
        )
        self.client.force_login(other_user)
        url = reverse("creators:profile", args=[self.unverified_creator.user.username])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertIn("This profile is private", response.content.decode())
