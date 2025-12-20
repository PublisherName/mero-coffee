from django.urls import reverse

from .base import BaseTestCase


class LogoutViewTests(BaseTestCase):
    def setUp(self):
        self.logout_url = reverse("accounts:logout")
        self.homepage_url = reverse("core:homepage")
        self.login_url = reverse("accounts:login")
        self.user = self.create_user()

    def test_logout_authenticated_user(self):
        self.client.force_login(self.user)
        self.assertTrue("_auth_user_id" in self.client.session)

        response = self.client.get(self.logout_url)

        self.assertRedirects(response, self.homepage_url)
        self.assertFalse("_auth_user_id" in self.client.session)

    def test_logout_unauthenticated_user(self):
        response = self.client.get(self.logout_url)

        self.assertRedirects(
            response, f"{self.login_url}?next={self.logout_url}", fetch_redirect_response=False
        )
