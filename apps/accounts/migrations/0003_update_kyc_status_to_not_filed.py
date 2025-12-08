# Generated manually

from django.db import migrations


def update_empty_kyc_to_not_filed(apps, schema_editor):
    """Update KYC records with no data to NOT_FILED status."""
    KYC = apps.get_model("accounts", "KYC")

    # Update KYC records that are pending but have no data filled in
    KYC.objects.filter(
        status="pending",
        full_name="",
        phone="",
        address="",
        city="",
        country="",
        id_type="",
        id_number=""
    ).update(status="not_filed")


def reverse_update(apps, schema_editor):
    """Reverse migration - set back to pending."""
    KYC = apps.get_model("accounts", "KYC")

    # Revert NOT_FILED records with no data back to pending
    KYC.objects.filter(
        status="not_filed",
        full_name="",
        phone="",
        address="",
        city="",
        country="",
        id_type="",
        id_number=""
    ).update(status="pending")


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_kyc_system'),
    ]

    operations = [
        migrations.RunPython(update_empty_kyc_to_not_filed, reverse_update),
    ]
