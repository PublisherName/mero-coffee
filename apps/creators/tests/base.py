from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.models import KYC
from apps.creators.models import CreatorProfile

User = get_user_model()


class BaseCreatorsTestCase(TestCase):
    user_password = "testpass123"

    def create_user(self, username="testuser", email="test@example.com", is_verified=True):
        user = User.objects.create_user(
            username=username, email=email, password=self.user_password
        )
        user.is_verified = is_verified
        user.save()
        if is_verified:
            KYC.objects.create(user=user, status="approved")
        return user

    def create_creator_profile(self, user=None, **kwargs):
        if user is None:
            user = self.create_user()
        profile, created = CreatorProfile.objects.get_or_create(user=user, defaults=kwargs)
        if not created:
            for key, value in kwargs.items():
                setattr(profile, key, value)
            profile.save()
        return profile
