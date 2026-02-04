from unittest.mock import Mock

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.accounts.utills.roles import validate_user_role_change

User = get_user_model()


class ValidateRoleChangeTestCase(TestCase):
    def setUp(self):
        self.super_admin = User.objects.create_user(
            username="superadmin",
            email="super@test.com",
            role=User.Roles.SUPER_ADMIN,
            is_superuser=True,
        )
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            role=User.Roles.ADMIN,
        )
        self.creator = User.objects.create_user(
            username="creator",
            email="creator@test.com",
            role=User.Roles.CREATOR,
        )

        self.support = User.objects.create_user(
            username="support",
            email="support@test.com",
            role=User.Roles.SUPPORT,
        )

    def test_self_upgrade_blocked(self):
        """Test that users cannot upgrade their own role"""
        request = Mock()
        request.user = self.creator

        with self.assertRaises(ValidationError) as cm:
            validate_user_role_change(self.creator, User.Roles.ADMIN, request)

        self.assertIn("Cannot self upgrade", str(cm.exception))

    def test_self_downgrade_admin_creator_blocked(self):
        """Test that users cannot downgrade their own role"""
        request = Mock()
        request.user = self.admin

        with self.assertRaises(ValidationError) as cm:
            validate_user_role_change(self.admin, User.Roles.CREATOR, request)

        self.assertIn("Cannot self downgrade", str(cm.exception))

    def test_non_super_cannot_assign_super_admin(self):
        """Test that non-super admins cannot assign super admin role"""
        request = Mock()
        request.user = self.admin
        request.user.is_superuser = False

        with self.assertRaises(ValidationError) as cm:
            validate_user_role_change(self.creator, User.Roles.SUPER_ADMIN, request)

        self.assertIn("Only Super Admins can assign Super Admin role", str(cm.exception))

    def test_non_super_cannot_upgrade_others_to_higher_roles(self):
        """Test that non-super admins cannot upgrade other users"""
        request = Mock()
        request.user = self.support
        request.user.is_superuser = False

        with self.assertRaises(ValidationError) as cm:
            validate_user_role_change(self.creator, User.Roles.MANAGER, request)

        self.assertIn("exceeds your permission level", str(cm.exception))

    def test_super_admin_can_assign_any_role(self):
        """Test that super admins can assign any role"""
        request = Mock()
        request.user = self.super_admin
        request.user.is_superuser = True

        # Should not raise any exception
        validate_user_role_change(self.creator, User.Roles.ADMIN, request)
        validate_user_role_change(self.admin, User.Roles.SUPER_ADMIN, request)

    def test_no_request_blocks_role_change(self):
        """Test that role changes doesn't work without request context"""

        with self.assertRaises(ValidationError) as cm:
            validate_user_role_change(self.creator, User.Roles.SUPPORTER)

        self.assertIn("Role changes require authenticated user", str(cm.exception))

    def test_no_user_instance_blocks_role_change(self):
        """Test that role changes blocks without user instance context"""
        request = Mock()
        request.user = self.super_admin
        request.user.is_superuser = True

        with self.assertRaises(ValidationError) as cm:
            validate_user_role_change(None, User.Roles.SUPPORTER, request)

        self.assertIn("User instance required for role validation", str(cm.exception))

    def test_super_admin_self_role_change_pass(self):
        """Test that super admin can change their own role to super admin"""
        request = Mock()
        request.user = self.super_admin
        request.user.is_superuser = True
        validate_user_role_change(self.super_admin, User.Roles.SUPER_ADMIN, request)

    def test_admin_downgrade_support_to_supporter(self):
        """Test that admin can change lower role of users"""
        request = Mock()
        request.user = self.admin
        request.user.is_superuser = False

        validate_user_role_change(self.support, User.Roles.SUPPORTER, request)

    def test_admin_cannot_downgrade_super_admin_to_support(self):
        """Test that admin cannot change higher role user to lower"""
        request = Mock()
        request.user = self.admin
        request.user.is_superuser = False

        with self.assertRaises(ValidationError) as cm:
            validate_user_role_change(self.super_admin, User.Roles.SUPPORT, request)

        self.assertIn(
            "You don't have permission to downgrade users with higher roles", str(cm.exception)
        )
