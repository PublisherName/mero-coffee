"""Tests for role-to-group assignment functionality."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

User = get_user_model()


class RoleGroupAssignmentTests(TestCase):
    """Test that users are assigned to the correct group based on their role."""

    @classmethod
    def setUpTestData(cls):
        cls.user_password = "testpass123"

        # Create groups that match role names
        role_groups = [
            "super_admin",
            "admin",
            "manager",
            "merchant",
            "support",
            "creator",
            "supporter",
        ]
        cls.groups = {}
        for role_name in role_groups:
            group, _ = Group.objects.get_or_create(name=role_name)
            cls.groups[role_name] = group

    def _create_user_with_role(self, username, role):
        """Helper to create a user with a specific role."""
        return User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password=self.user_password,
            role=role,
            is_active=True,
        )

    def test_creator_role_gets_creator_group(self):
        """Test that a user with creator role gets the creator group."""
        user = self._create_user_with_role("creator_user", User.Roles.CREATOR)

        user.refresh_from_db()

        self.assertTrue(user.groups.filter(name="creator").exists())
        self.assertEqual(user.groups.count(), 1)
        self.assertEqual(list(user.groups.all())[0].name, "creator")

    def test_supporter_role_gets_supporter_group(self):
        """Test that a user with supporter role gets the supporter group."""
        user = self._create_user_with_role("supporter_user", User.Roles.SUPPORTER)

        user.refresh_from_db()

        self.assertTrue(user.groups.filter(name="supporter").exists())
        self.assertEqual(user.groups.count(), 1)
        self.assertEqual(list(user.groups.all())[0].name, "supporter")

    def test_manager_role_gets_manager_group(self):
        """Test that a user with manager role gets the manager group."""
        user = self._create_user_with_role("manager_user", User.Roles.MANAGER)

        user.refresh_from_db()

        self.assertTrue(user.groups.filter(name="manager").exists())
        self.assertEqual(user.groups.count(), 1)
        self.assertEqual(list(user.groups.all())[0].name, "manager")

    def test_admin_role_gets_admin_group(self):
        """Test that a user with admin role gets the admin group."""
        user = self._create_user_with_role("admin_user", User.Roles.ADMIN)

        user.refresh_from_db()

        self.assertTrue(user.groups.filter(name="admin").exists())
        self.assertEqual(user.groups.count(), 1)
        self.assertEqual(list(user.groups.all())[0].name, "admin")

    def test_super_admin_role_gets_super_admin_group(self):
        """Test that a user with super_admin role gets the super_admin group."""
        user = self._create_user_with_role("super_admin_user", User.Roles.SUPER_ADMIN)

        user.refresh_from_db()

        self.assertTrue(user.groups.filter(name="super_admin").exists())
        self.assertEqual(user.groups.count(), 1)
        self.assertEqual(list(user.groups.all())[0].name, "super_admin")

    def test_merchant_role_gets_merchant_group(self):
        """Test that a user with merchant role gets the merchant group."""
        user = self._create_user_with_role("merchant_user", User.Roles.MERCHANT)

        user.refresh_from_db()

        self.assertTrue(user.groups.filter(name="merchant").exists())
        self.assertEqual(user.groups.count(), 1)
        self.assertEqual(list(user.groups.all())[0].name, "merchant")

    def test_support_role_gets_support_group(self):
        """Test that a user with support role gets the support group."""
        user = self._create_user_with_role("support_user", User.Roles.SUPPORT)

        user.refresh_from_db()

        self.assertTrue(user.groups.filter(name="support").exists())
        self.assertEqual(user.groups.count(), 1)
        self.assertEqual(list(user.groups.all())[0].name, "support")

    def test_role_change_updates_group(self):
        """Test that changing a user's role updates their group assignment."""
        user = self._create_user_with_role("role_change_user", User.Roles.SUPPORTER)

        user.refresh_from_db()
        self.assertTrue(user.groups.filter(name="supporter").exists())

        user.role = User.Roles.CREATOR
        user.save()

        user.refresh_from_db()
        self.assertTrue(user.groups.filter(name="creator").exists())
        self.assertFalse(user.groups.filter(name="supporter").exists())
        self.assertEqual(user.groups.count(), 1)

    def test_all_roles_assigned_correctly(self):
        """Comprehensive test for all role-to-group assignments."""
        roles_and_groups = [
            (User.Roles.SUPER_ADMIN, "super_admin"),
            (User.Roles.ADMIN, "admin"),
            (User.Roles.MANAGER, "manager"),
            (User.Roles.MERCHANT, "merchant"),
            (User.Roles.SUPPORT, "support"),
            (User.Roles.CREATOR, "creator"),
            (User.Roles.SUPPORTER, "supporter"),
        ]

        for role, expected_group in roles_and_groups:
            with self.subTest(role=role):
                user = self._create_user_with_role(f"test_{role}_user", role)

                user.refresh_from_db()

                self.assertTrue(
                    user.groups.filter(name=expected_group).exists(),
                    f"User with role {role} should be in group {expected_group}",
                )
                self.assertEqual(
                    user.groups.count(),
                    1,
                    f"User with role {role} should have exactly 1 group",
                )
