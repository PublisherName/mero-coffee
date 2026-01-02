from django.contrib.auth import get_user_model

from apps.creators.models import CreatorProfile

from .base import BaseCreatorsTestCase

User = get_user_model()


class CreatorProfileManagerTests(BaseCreatorsTestCase):
    def setUp(self):
        self.verified_creator = self.create_creator_profile(
            user=self.create_user(username="verified", email="verified@example.com"),
            display_name="Verified Creator",
        )
        self.unverified_creator = self.create_creator_profile(
            user=self.create_user(
                username="unverified", email="unverified@example.com", is_verified=False
            ),
            display_name="Unverified Creator",
        )
        self.staff_creator = self.create_creator_profile(
            user=User.objects.create_user(
                username="staff",
                email="staff@example.com",
                password="testpass123",
                is_staff=True,
                is_verified=True,
            ),
            display_name="Staff Creator",
        )

    def test_active_creators(self):
        creators = CreatorProfile.objects.active_creators()
        self.assertEqual(creators.count(), 1)
        self.assertIn(self.verified_creator, creators)
        self.assertNotIn(self.unverified_creator, creators)
        self.assertNotIn(self.staff_creator, creators)

    def test_by_username(self):
        creator = CreatorProfile.objects.by_username("verified").first()
        self.assertEqual(creator, self.verified_creator)

    def test_by_username_unverified(self):
        creator = CreatorProfile.objects.by_username("unverified").first()
        self.assertEqual(creator, self.unverified_creator)

    def test_by_username_active(self):
        creator = CreatorProfile.objects.by_username_active("verified").first()
        self.assertEqual(creator, self.verified_creator)

    def test_by_username_active_unverified_not_found(self):
        creator = CreatorProfile.objects.by_username_active("unverified").first()
        self.assertIsNone(creator)

    def test_by_username_not_found(self):
        creator = CreatorProfile.objects.by_username("nonexistent").first()
        self.assertIsNone(creator)

    def test_search_by_display_name(self):
        creators = CreatorProfile.objects.search("Verified")
        self.assertEqual(creators.count(), 1)
        self.assertIn(self.verified_creator, creators)

    def test_search_by_username(self):
        creators = CreatorProfile.objects.search("verified")
        self.assertEqual(creators.count(), 1)
        self.assertIn(self.verified_creator, creators)

    def test_search_empty_returns_all_active(self):
        creators = CreatorProfile.objects.search("")
        self.assertEqual(creators.count(), 1)
        self.assertIn(self.verified_creator, creators)

    def test_apply_sort_recent(self):
        creators = CreatorProfile.objects.apply_sort("recent")
        self.assertEqual(creators.count(), 1)
        self.assertEqual(creators.first(), self.verified_creator)

    def test_apply_sort_default(self):
        creators = CreatorProfile.objects.apply_sort("")
        self.assertEqual(creators.count(), 1)
        self.assertEqual(creators.first(), self.verified_creator)
