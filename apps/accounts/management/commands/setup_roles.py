from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from apps.accounts.models import User


class Command(BaseCommand):
    help = "Set up role-based groups and assign permissions"

    def handle(self, *args, **options):
        role_permissions = {
            User.Roles.SUPER_ADMIN: [],
            User.Roles.ADMIN: [
                # Accounts
                "accounts.add_user",
                "accounts.change_user",
                "accounts.view_user",
                "accounts.add_kyc",
                "accounts.change_kyc",
                "accounts.view_kyc",
                # Payments
                "payments.view_supporttransaction",
                "payments.view_paymentlog",
                # Creators
                "creators.add_creatorprofile",
                "creators.change_creatorprofile",
                "creators.view_creatorprofile",
                # Emails
                "emails.add_emailtemplate",
                "emails.change_emailtemplate",
                "emails.view_emailtemplate",
            ],
            User.Roles.MERCHANT: [
                # Payments
                "payments.view_supporttransaction",
                "payments.view_paymentlog",
            ],
            User.Roles.SUPPORT: [
                # Emails
                "emails.view_emailtemplate",
            ],
            User.Roles.CREATOR: [
                # Creators
                "creators.add_creatorprofile",
                "creators.change_creatorprofile",
                "creators.view_creatorprofile",
            ],
            User.Roles.SUPPORTER: [],
        }

        for role, perms in role_permissions.items():
            group, created = Group.objects.get_or_create(name=role)
            if created:
                self.stdout.write(f"Created group: {role}")
            else:
                self.stdout.write(f"Group {role} already exists")

            group.permissions.clear()

            for perm_codename in perms:
                try:
                    app_label, codename = perm_codename.split(".")
                    perm = Permission.objects.get(
                        content_type__app_label=app_label, codename=codename
                    )
                    group.permissions.add(perm)
                    self.stdout.write(f"Added permission {perm_codename} to {role}")
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f"Permission {perm_codename} does not exist")
                    )

        self.stdout.write(self.style.SUCCESS("Role setup completed"))
