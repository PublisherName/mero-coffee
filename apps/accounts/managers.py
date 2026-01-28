from django.apps import apps
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user_object(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError("The given username must be set")
        email = self.normalize_email(email)
        GlobalUserModel = apps.get_model(self.model._meta.app_label, self.model._meta.object_name)
        username = GlobalUserModel.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        return user

    def _create_user(self, username, email, password, **extra_fields):
        user = self._create_user_object(username, email, password, **extra_fields)
        user.save(using=self._db)
        return user

    async def _acreate_user(self, username, email, password, **extra_fields):
        user = self._create_user_object(username, email, password, **extra_fields)
        await user.asave(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

    create_user.alters_data = True

    async def acreate_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return await self._acreate_user(username, email, password, **extra_fields)

    acreate_user.alters_data = True

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", self.model.Roles.SUPER_ADMIN)
        extra_fields.setdefault("is_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if extra_fields.get("role") != self.model.Roles.SUPER_ADMIN:
            raise ValueError("Superuser must have role=SUPER_ADMIN.")

        return self._create_user(username, email, password, **extra_fields)

    async def acreate_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", self.model.Roles.SUPER_ADMIN)
        extra_fields.setdefault("is_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if extra_fields.get("role") != self.model.Roles.SUPER_ADMIN:
            raise ValueError("Superuser must have role=SUPER_ADMIN.")

        return await self._acreate_user(username, email, password, **extra_fields)
