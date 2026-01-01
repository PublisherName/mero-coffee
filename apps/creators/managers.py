from django.db import models

from .querysets import CreatorProfileQuerySet


class CreatorProfileManager(models.Manager):
    def get_queryset(self):
        return CreatorProfileQuerySet(self.model, using=self._db)

    def is_creators(self):
        return self.get_queryset().is_creators()

    def active_creators(self):
        return self.get_queryset().active_creators()

    def active_creators_with_stats(self):
        return self.get_queryset().active_creators_with_stats()

    def by_username(self, username):
        return self.get_queryset().by_username(username)

    def by_username_active(self, username):
        return self.get_queryset().by_username_active(username)

    def search(self, text):
        return self.get_queryset().search(text)

    def apply_sort(self, key):
        return self.get_queryset().apply_sort(key)
