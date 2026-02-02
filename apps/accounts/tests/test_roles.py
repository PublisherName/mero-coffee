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

    def test_admin_save_model_with_role_change(self):
        """Test that admin's save_model method updates group when role is changed."""
        from django.contrib.admin.sites import AdminSite
        from django.contrib.auth.models import Group

        from apps.accounts.admin import UserAdmin

        user = User.objects.create_user(
            username="rolechangetest",
            email="rolechangetest@test.com",
            password="testpass123",
            role=User.Roles.CREATOR,
        )

        initial_group = Group.objects.get(name=User.Roles.CREATOR)
        self.assertIn(initial_group, user.groups.all())

        # Simulate admin changing role to ADMIN
        admin_site = AdminSite()
        _user_admin = UserAdmin(User, admin_site)

        from django.forms import modelform_factory

        UserForm = modelform_factory(User, fields=["role", "is_staff", "is_superuser"])

        form = UserForm({"role": User.Roles.ADMIN}, instance=user)
        user = form.save(commit=False)

        user._admin_save = True
        if "role" in form.changed_data:
            from apps.accounts.signals.roles import get_expected_flags

            expected_staff, expected_superuser = get_expected_flags(user.role)
            user.is_staff = expected_staff
            user.is_superuser = expected_superuser
            user.save()
            role_group = Group.objects.get(name=user.role)
            user.groups.clear()
            user.groups.add(role_group)

        user.refresh_from_db()

        # Should now be in ADMIN group, not CREATOR group
        self.assertEqual(len(user.groups.all()), 1)
        self.assertIn(Group.objects.get(name=User.Roles.ADMIN), user.groups.all())
        self.assertNotIn(initial_group, user.groups.all())

    def test_multiple_groups_assignment(self):
        """Test that users can have multiple groups assigned."""
        user = User.objects.create_user(
            username="multigroup",
            email="multigroup@test.com",
            password="testpass123",
            role=User.Roles.CREATOR,
        )

        # Initially has creator group
        user.refresh_from_db()
        self.assertIn(Group.objects.get(name=User.Roles.CREATOR), user.groups.all())

        # Add additional group
        admin_group = Group.objects.get(name=User.Roles.ADMIN)
        user.groups.add(admin_group)

        user.refresh_from_db()
        self.assertEqual(len(user.groups.all()), 2)
        self.assertIn(Group.objects.get(name=User.Roles.CREATOR), user.groups.all())
        self.assertIn(admin_group, user.groups.all())

    def test_role_group_fallback_when_no_groups(self):
        """Test that role group is assigned when user has no groups."""
        user = User.objects.create_user(
            username="nogroups",
            email="nogroups@test.com",
            password="testpass123",
            role=User.Roles.SUPPORT,
        )

        # Remove all groups
        user.groups.clear()
        user.refresh_from_db()
        self.assertEqual(len(user.groups.all()), 0)

        # Save user - should trigger fallback group assignment
        user.save()

        user.refresh_from_db()
        self.assertEqual(len(user.groups.all()), 1)
        self.assertIn(Group.objects.get(name=User.Roles.SUPPORT), user.groups.all())

    def test_preserve_multiple_groups_on_non_role_change(self):
        """Test that multiple groups are preserved when role is not changed."""
        user = User.objects.create_user(
            username="preserve",
            email="preserve@test.com",
            password="testpass123",
            role=User.Roles.CREATOR,
        )

        # Add multiple groups
        admin_group = Group.objects.get(name=User.Roles.ADMIN)
        support_group = Group.objects.get(name=User.Roles.SUPPORT)
        user.groups.add(admin_group, support_group)

        user.refresh_from_db()
        self.assertEqual(len(user.groups.all()), 3)

        # Change non-role field
        user.first_name = "Updated"
        user.save()

        user.refresh_from_db()
        # Groups should be preserved
        self.assertEqual(len(user.groups.all()), 3)
        self.assertIn(Group.objects.get(name=User.Roles.CREATOR), user.groups.all())
        self.assertIn(admin_group, user.groups.all())
        self.assertIn(support_group, user.groups.all())

    def test_supporter_role_assignment(self):
        """Test SUPPORTER gets is_staff=False, is_superuser=False and correct group."""
        user = User.objects.create_user(
            username="supporter",
            email="supporter@test.com",
            password="testpass123",
            role=User.Roles.SUPPORTER,
        )

        user.refresh_from_db()
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertIn(Group.objects.get(name=User.Roles.SUPPORTER), user.groups.all())

    def test_admin_save_model_without_role_change(self):
        """Test that admin's save_model preserves groups when role is not changed."""
        from django.contrib.admin.sites import AdminSite
        from django.contrib.auth.models import Group

        from apps.accounts.admin import UserAdmin

        user = User.objects.create_user(
            username="norolechange",
            email="norolechange@test.com",
            password="testpass123",
            role=User.Roles.CREATOR,
        )

        # Add additional groups
        admin_group = Group.objects.get(name=User.Roles.ADMIN)
        user.groups.add(admin_group)

        user.refresh_from_db()
        self.assertEqual(len(user.groups.all()), 2)

        # Simulate admin changing non-role field
        admin_site = AdminSite()
        _user_admin = UserAdmin(User, admin_site)

        from django.forms import modelform_factory

        UserForm = modelform_factory(User, fields=["first_name", "is_verified"])

        form = UserForm({"first_name": "Updated", "is_verified": True}, instance=user)
        user = form.save(commit=False)

        user._admin_save = True
        user.save()

        user.refresh_from_db()
        # Groups should be preserved
        self.assertEqual(len(user.groups.all()), 2)
        self.assertIn(Group.objects.get(name=User.Roles.CREATOR), user.groups.all())
        self.assertIn(admin_group, user.groups.all())

    def test_signal_disabled_for_admin_save(self):
        """Test that signal is disabled when saving from admin."""
        user = User.objects.create_user(
            username="signaltest",
            email="signaltest@test.com",
            password="testpass123",
            role=User.Roles.CREATOR,
        )

        # Mark as admin save and change role
        user._admin_save = True
        user.role = User.Roles.ADMIN
        user.save()

        user.refresh_from_db()
        self.assertIn(Group.objects.get(name=User.Roles.CREATOR), user.groups.all())
        self.assertEqual(user.role, User.Roles.ADMIN)

    def test_new_user_gets_role_group(self):
        """Test that new users get assigned to their role group."""
        user = User.objects.create_user(
            username="newuser",
            email="newuser@test.com",
            password="testpass123",
            role=User.Roles.MERCHANT,
        )

        user.refresh_from_db()
        self.assertEqual(len(user.groups.all()), 1)
        self.assertIn(Group.objects.get(name=User.Roles.MERCHANT), user.groups.all())

    def test_user_cannot_change_own_role_in_admin(self):
        """Test that users cannot change their own role through admin."""
        from django.contrib.admin.sites import AdminSite
        from django.core.exceptions import PermissionDenied
        from django.forms import modelform_factory

        from apps.accounts.admin import UserAdmin

        user = User.objects.create_user(
            username="selfchange",
            email="selfchange@test.com",
            password="testpass123",
            role=User.Roles.ADMIN,
        )

        admin_site = AdminSite()
        user_admin = UserAdmin(User, admin_site)

        UserForm = modelform_factory(User, fields=["role"])
        form = UserForm({"role": User.Roles.SUPER_ADMIN}, instance=user)
        user = form.save(commit=False)

        class MockRequest:
            def __init__(self, user):
                self.user = user

        request = MockRequest(user)

        with self.assertRaises(PermissionDenied) as cm:
            user_admin.save_model(request, user, form, change=True)

        self.assertEqual(str(cm.exception), "You cannot change your own role.")

    def test_superuser_cannot_downgrade_own_role_in_admin(self):
        """Test that super users cannot downgrade their own role through admin."""
        from django.contrib.admin.sites import AdminSite
        from django.core.exceptions import PermissionDenied
        from django.forms import modelform_factory

        from apps.accounts.admin import UserAdmin

        user = User.objects.create_user(
            username="superdowngrade",
            email="superdowngrade@test.com",
            password="testpass123",
            role=User.Roles.SUPER_ADMIN,
        )

        admin_site = AdminSite()
        user_admin = UserAdmin(User, admin_site)

        UserForm = modelform_factory(User, fields=["role"])
        form = UserForm({"role": User.Roles.ADMIN}, instance=user)
        user = form.save(commit=False)

        class MockRequest:
            def __init__(self, user):
                self.user = user

        request = MockRequest(user)

        with self.assertRaises(PermissionDenied) as cm:
            user_admin.save_model(request, user, form, change=True)

        self.assertEqual(str(cm.exception), "Super users cannot downgrade their own role.")

    def test_admin_can_change_other_user_role(self):
        """Test that admins can change other users' roles."""
        from django.contrib.admin.sites import AdminSite
        from django.forms import modelform_factory

        from apps.accounts.admin import UserAdmin

        admin_user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass123",
            role=User.Roles.SUPER_ADMIN,
        )

        target_user = User.objects.create_user(
            username="target",
            email="target@test.com",
            password="testpass123",
            role=User.Roles.CREATOR,
        )

        admin_site = AdminSite()
        _user_admin = UserAdmin(User, admin_site)

        UserForm = modelform_factory(User, fields=["role"])
        form = UserForm({"role": User.Roles.ADMIN}, instance=target_user)
        target_user = form.save(commit=False)

        class MockRequest:
            def __init__(self, user):
                self.user = user

        _request = MockRequest(admin_user)

        # This should not raise an exception
        target_user._admin_save = True
        if "role" in form.changed_data:
            from apps.accounts.signals.roles import get_expected_flags

            expected_staff, expected_superuser = get_expected_flags(target_user.role)
            target_user.is_staff = expected_staff
            target_user.is_superuser = expected_superuser
            target_user.save()
            role_group = Group.objects.get(name=target_user.role)
            target_user.groups.clear()
            target_user.groups.add(role_group)

        target_user.refresh_from_db()
        self.assertEqual(target_user.role, User.Roles.ADMIN)
        self.assertIn(Group.objects.get(name=User.Roles.ADMIN), target_user.groups.all())
