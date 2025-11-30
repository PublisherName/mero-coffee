from django.db import models

from .querysets import CreatorProfileQuerySet


class CreatorProfileManager(models.Manager):
    def get_queryset(self):
        return CreatorProfileQuerySet(self.model, using=self._db)

    def active_creators(self):
        return self.get_queryset().active_creators()

    def by_username(self, username):
        return self.get_queryset().by_username(username)

    def search(self, text):
        return self.get_queryset().search(text)

    def apply_sort(self, key):
        return self.get_queryset().apply_sort(key)
