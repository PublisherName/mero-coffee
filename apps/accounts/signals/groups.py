# your_app/signals.py
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


@receiver(post_save, sender=User)
def assign_user_role_group(sender, instance, created, **kwargs):
    """
    Assign group based on user.role after every save.
    """
    # TODO: flag to update only on change
    if instance.role:
        try:
            role_group = Group.objects.get(name=instance.role)
            instance.groups.clear()
            instance.groups.add(role_group)
        except ObjectDoesNotExist:
            pass
