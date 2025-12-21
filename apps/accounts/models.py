import uuid

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _

from root.storage import PrivateMediaStorage

from .enums import VerificationDocumentType


class User(AbstractUser):
    class Roles(models.TextChoices):
        CREATOR = "creator", _("Creator")
        SUPPORTER = "supporter", _("Supporter")
        ADMIN = "admin", _("Admin")

    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.CREATOR)
    verified = models.BooleanField(default=False)

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

    def save(self, *args, **kwargs):
        if self.is_superuser and self.role != self.Roles.ADMIN:
            self.role = self.Roles.ADMIN
            self.verified = True
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

    def __str__(self):
        return f"KYC - {self.user.username} ({self.status})"
