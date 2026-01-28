from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import User


def get_expected_flags(role):
    """Get expected is_staff and is_superuser for a role."""
    if role == User.Roles.SUPER_ADMIN:
        return True, True
    elif role in [User.Roles.ADMIN, User.Roles.MERCHANT, User.Roles.SUPPORT]:
        return True, False
    else:
        return False, False


def assign_user_group(instance):
    """Assign user to the appropriate group based on role."""
    try:
        group = Group.objects.get(name=instance.role)
        if instance.groups.count() != 1 or instance.groups.first().id != group.id:
            instance.groups.clear()
            instance.groups.add(group)
    except Group.DoesNotExist:
        pass


@receiver(post_save, sender=User)
def assign_role_permissions(sender, instance, created, **kwargs):
    """Assign staff/superuser status and group based on user role."""
    if hasattr(instance, "_signal_processing"):
        return

    expected_staff, expected_superuser = get_expected_flags(instance.role)

    needs_update = (
        instance.is_staff != expected_staff or instance.is_superuser != expected_superuser
    )

    with transaction.atomic():
        if needs_update:
            instance._signal_processing = True
            instance.is_staff = expected_staff
            instance.is_superuser = expected_superuser
            instance.save(update_fields=["is_staff", "is_superuser"])
            if hasattr(instance, "_signal_processing"):
                del instance._signal_processing
        assign_user_group(instance)
