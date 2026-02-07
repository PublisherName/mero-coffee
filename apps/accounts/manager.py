from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import Group
from django.db import transaction


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Username is required")

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", self.model.Roles.SUPER_ADMIN)
        extra_fields.setdefault("is_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, password, **extra_fields)

    @classmethod
    @transaction.atomic
    def _assign_role_group(cls, user):
        """Assign user to group matching their role."""
        if hasattr(user, "role") and user.role:
            try:
                group = Group.objects.get(name=user.role)
                user.groups.set([group])
            except Group.DoesNotExist:
                pass
