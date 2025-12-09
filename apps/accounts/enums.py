from django.db import models
from django.utils.translation import gettext_lazy as _


class VerificationDocumentType(models.TextChoices):
    NATIONAL_ID = "national_id", _("National ID")
    CITIZENSHIP = "citizenship", _("Citizenship")
    DRIVER_LICENSE = "driver_license", _("Driver License")
    PASSPORT = "passport", _("Passport")
