from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import User

from .models import CreatorProfile


@receiver(post_save, sender=User)
def create_creator_profile(sender, instance, created, **kwargs):
    if created:
        display_name = f"{instance.first_name} {instance.last_name}".strip()
        CreatorProfile.objects.create(user=instance, display_name=display_name)


@receiver(post_save, sender=User)
def save_creator_profile(sender, instance, **kwargs):
    if hasattr(instance, "creator_profile"):
        instance.creator_profile.save()
