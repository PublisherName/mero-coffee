from django.conf import settings
from django.db import models


class CreatorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="creator_profile"
    )
    display_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    avatar_url = models.URLField(blank=True)
    page_url = models.SlugField(unique=True)
    coffee_price = models.PositiveIntegerField(default=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.display_name or self.user.username
