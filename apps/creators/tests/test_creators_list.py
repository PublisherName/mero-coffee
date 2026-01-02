from django.urls import reverse

from .base import BaseCreatorsTestCase


class CreatorsListViewTests(BaseCreatorsTestCase):
    def setUp(self):
        self.creator1 = self.create_creator_profile(
            user=self.create_user(
                username="creator1", email="creator1@example.com", is_verified=True
            ),
            display_name="Creator One",
        )
        self.creator2 = self.create_creator_profile(
            user=self.create_user(
                username="creator2", email="creator2@example.com", is_verified=True
            ),
            display_name="Creator Two",
        )
        self.unverified_creator = self.create_creator_profile(
            user=self.create_user(
                username="creator3", email="creator3@example.com", is_verified=False
            ),
            display_name="Creator Three",
        )
        self.url = reverse("creators:creators_list")

    def test_creators_list_get_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.creator1.display_name)
        self.assertContains(response, self.creator2.display_name)
        self.assertNotContains(response, self.unverified_creator.display_name)

    def test_creators_list_search(self):
        response = self.client.get(self.url, {"q": "One"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.creator1.display_name)
        self.assertNotContains(response, self.creator2.display_name)

    def test_creators_list_sort(self):
        response = self.client.get(self.url, {"sort": "recent"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.creator1.display_name)
        self.assertContains(response, self.creator2.display_name)
        self.assertNotContains(response, self.unverified_creator.display_name)
