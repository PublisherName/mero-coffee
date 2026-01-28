from django.contrib.auth.models import Group
from django.test import TestCase

from apps.accounts.models import User


class RoleAssignmentTests(TestCase):
    """Test role-based permission assignment via signals."""

    @classmethod
    def setUp(cls):
        for role in User.Roles:
            Group.objects.get_or_create(name=role)

    def test_super_admin_role_assignment(self):
        """Test SUPER_ADMIN gets is_staff=True, is_superuser=True and correct group."""
        user = User.objects.create_user(
            username="superadmin",
            email="superadmin@test.com",
            password="testpass123",
            role=User.Roles.SUPER_ADMIN,
        )

        user.refresh_from_db()
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertIn(Group.objects.get(name=User.Roles.SUPER_ADMIN), user.groups.all())

    def test_admin_role_assignment(self):
        """Test ADMIN gets is_staff=True, is_superuser=False and correct group."""
        user = User.objects.create_user(
            username="admin", email="admin@test.com", password="testpass123", role=User.Roles.ADMIN
        )

        user.refresh_from_db()
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertIn(Group.objects.get(name=User.Roles.ADMIN), user.groups.all())

    def test_merchant_role_assignment(self):
        """Test MERCHANT gets is_staff=True, is_superuser=False and correct group."""
        user = User.objects.create_user(
            username="merchant",
            email="merchant@test.com",
            password="testpass123",
            role=User.Roles.MERCHANT,
        )

        user.refresh_from_db()
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertIn(Group.objects.get(name=User.Roles.MERCHANT), user.groups.all())

    def test_support_role_assignment(self):
        """Test SUPPORT gets is_staff=True, is_superuser=False and correct group."""
        user = User.objects.create_user(
            username="support",
            email="support@test.com",
            password="testpass123",
            role=User.Roles.SUPPORT,
        )

        user.refresh_from_db()
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertIn(Group.objects.get(name=User.Roles.SUPPORT), user.groups.all())

    def test_creator_role_assignment(self):
        """Test CREATOR gets is_staff=False, is_superuser=False and correct group."""
        user = User.objects.create_user(
            username="creator",
            email="creator@test.com",
            password="testpass123",
            role=User.Roles.CREATOR,
        )

        user.refresh_from_db()
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertIn(Group.objects.get(name=User.Roles.CREATOR), user.groups.all())

    def test_role_change_updates_permissions(self):
        """Test that changing role updates permissions and group."""
        user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
            role=User.Roles.CREATOR,
        )

        # Initially creator
        user.refresh_from_db()
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertIn(Group.objects.get(name=User.Roles.CREATOR), user.groups.all())

        # Change to admin
        user.role = User.Roles.ADMIN
        user.save()

        user.refresh_from_db()
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertIn(Group.objects.get(name=User.Roles.ADMIN), user.groups.all())
        # Should not be in creator group anymore
        self.assertNotIn(Group.objects.get(name=User.Roles.CREATOR), user.groups.all())

    def test_superuser_creation_with_role(self):
        """Test creating superuser directly gets SUPER_ADMIN role."""
        user = User.objects.create_superuser(
            username="directsuper", email="directsuper@test.com", password="testpass123"
        )

        user.refresh_from_db()
        self.assertEqual(user.role, User.Roles.SUPER_ADMIN)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertIn(Group.objects.get(name=User.Roles.SUPER_ADMIN), user.groups.all())

    def test_super_admin_to_supporter_role_change(self):
        """Test that changing from SUPER_ADMIN to SUPPORTER updates permissions and group."""
        user = User.objects.create_user(
            username="superto supporter",
            email="superto supporter@test.com",
            password="testpass123",
            role=User.Roles.SUPER_ADMIN,
        )

        # Initially super admin
        user.refresh_from_db()
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertIn(Group.objects.get(name=User.Roles.SUPER_ADMIN), user.groups.all())

        # Change to supporter
        user.role = User.Roles.SUPPORTER
        user.save()

        user.refresh_from_db()
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertIn(Group.objects.get(name=User.Roles.SUPPORTER), user.groups.all())
        # Should not be in super admin group anymore
        self.assertNotIn(Group.objects.get(name=User.Roles.SUPER_ADMIN), user.groups.all())

    def test_super_admin_to_admin_role_change(self):
        """Test that changing from SUPER_ADMIN to ADMIN updates permissions and group."""
        user = User.objects.create_user(
            username="supertoadmin",
            email="supertoadmin@test.com",
            password="testpass123",
            role=User.Roles.SUPER_ADMIN,
        )

        # Initially super admin
        user.refresh_from_db()
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertIn(Group.objects.get(name=User.Roles.SUPER_ADMIN), user.groups.all())

        # Change to admin
        user.role = User.Roles.ADMIN
        user.save()

        user.refresh_from_db()
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertIn(Group.objects.get(name=User.Roles.ADMIN), user.groups.all())
        # Should not be in super admin group anymore
        self.assertNotIn(Group.objects.get(name=User.Roles.SUPER_ADMIN), user.groups.all())

    def test_admin_save_model_with_manual_group_assignment(self):
        """Test that admin's save_model method corrects manual group assignments."""
        from django.contrib.admin.sites import AdminSite
        from django.contrib.auth.models import Group

        from apps.accounts.admin import UserAdmin

        user = User.objects.create_user(
            username="adminmodeltest",
            email="adminmodeltest@test.com",
            password="testpass123",
            role=User.Roles.SUPER_ADMIN,
        )

        # Simulate manual group assignment
        wrong_group = Group.objects.get(name=User.Roles.CREATOR)
        user.groups.add(wrong_group)
        user.save()

        user.refresh_from_db()
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertIn(Group.objects.get(name=User.Roles.SUPER_ADMIN), user.groups.all())
        self.assertIn(wrong_group, user.groups.all())

        # Simulate admin save
        admin_site = AdminSite()
        user_admin = UserAdmin(User, admin_site)

        from django.forms import modelform_factory

        UserForm = modelform_factory(User, fields=["role", "is_staff", "is_superuser"])

        form = UserForm({"role": User.Roles.SUPER_ADMIN}, instance=user)

        user_admin.save_model(None, user, form, change=True)

        user.refresh_from_db()
        # Should only be in one group - SUPER_ADMIN
        self.assertEqual(len(user.groups.all()), 1)
        self.assertIn(Group.objects.get(name=User.Roles.SUPER_ADMIN), user.groups.all())
