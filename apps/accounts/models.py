import uuid

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.managers import UserManager
from root.storage import PrivateMediaStorage

from .enums import VerificationDocumentType


class User(AbstractUser):
    class Roles(models.TextChoices):
        SUPER_ADMIN = "super_admin", _("Super Admin")
        ADMIN = "admin", _("Admin")

        MERCHANT = "merchant", _("Merchant")
        SUPPORT = "support", _("Support")

        CREATOR = "creator", _("Creator")
        SUPPORTER = "supporter", _("Supporter")

    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.CREATOR)
    is_verified = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",
        related_query_name="custom_user",
        blank=True,
        help_text=_("The groups this user belongs to."),
        verbose_name=_("groups"),
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_set",
        related_query_name="custom_user",
        blank=True,
        help_text=_("Specific permissions for this user."),
        verbose_name=_("user permissions"),
    )

    objects = UserManager()

    def save(self, *args, **kwargs):
        if self.username:
            self.username = self.username.lower()
        if self.email:
            self.email = self.email.lower()
        if self.first_name:
            self.first_name = self.first_name.strip().title()
        if self.last_name:
            self.last_name = self.last_name.strip().title()

        # Handle role and group synchronization only if not being saved from admin
        if self.pk and not getattr(self, "_admin_save", False):
            old_user = User.objects.get(pk=self.pk)
            if old_user.role != self.role:
                from apps.accounts.signals.roles import get_expected_flags

                expected_staff, expected_superuser = get_expected_flags(self.role)
                self.is_staff = expected_staff
                self.is_superuser = expected_superuser
                super().save(*args, **kwargs)
                try:
                    role_group = Group.objects.get(name=self.role)
                    self.groups.clear()
                    self.groups.add(role_group)
                except Group.DoesNotExist:
                    self.groups.clear()
                return

        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class KYC(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Status(models.TextChoices):
        NOT_FILED = "not_filed", _("Not Filed")
        PENDING = "pending", _("Pending")
        APPROVED = "approved", _("Approved")
        REJECTED = "rejected", _("Rejected")

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="kyc")
    full_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.ForeignKey(
        "cities_light.City",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="city",
    )
    region = models.ForeignKey(
        "cities_light.Region",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="region",
    )
    subregion = models.ForeignKey(
        "cities_light.Subregion",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subregion",
    )
    country = models.ForeignKey(
        "cities_light.Country",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="country",
    )
    id_type = models.CharField(max_length=50, choices=VerificationDocumentType.choices, blank=True)
    id_number = models.CharField(max_length=100, blank=True)
    front_image = models.ImageField(
        upload_to="kyc/documents/", storage=PrivateMediaStorage(), blank=True
    )
    back_image = models.ImageField(
        upload_to="kyc/documents/", storage=PrivateMediaStorage(), blank=True
    )
    selfie_with_document = models.ImageField(
        upload_to="kyc/documents/", storage=PrivateMediaStorage(), blank=True
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_FILED)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.full_name:
            self.full_name = self.full_name.strip().title()
        if self.address:
            segments = [seg.strip().title() for seg in self.address.split(",")]
            self.address = ", ".join(segments)
        if self.id_number:
            self.id_number = self.id_number.strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"KYC - {self.user.username} ({self.status})"
