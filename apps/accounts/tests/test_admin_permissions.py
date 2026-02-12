from unittest.mock import Mock

from django.contrib.auth import get_user_model

from apps.accounts.tests.base import BaseTestCase

User = get_user_model()


class UserAdminPermissionTestCase(BaseTestCase):
    """Test cases for UserAdmin permission methods - focused on major scenarios"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user_password = "testpass123"
        # Create users once for all tests (faster than setUp)
        cls.super_admin = User.objects.create_superuser(
            username="superadmin",
            email="superadmin@example.com",
            password=cls.user_password,
            role=User.Roles.SUPER_ADMIN,
        )
        cls.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password=cls.user_password,
            role=User.Roles.ADMIN,
            is_staff=True,
        )
        cls.manager = User.objects.create_user(
            username="manager",
            email="manager@example.com",
            password=cls.user_password,
            role=User.Roles.MANAGER,
            is_staff=True,
        )
        cls.creator = User.objects.create_user(
            username="creator",
            email="creator@example.com",
            password=cls.user_password,
            role=User.Roles.CREATOR,
            is_staff=False,
        )
        cls.supporter = User.objects.create_user(
            username="supporter",
            email="supporter@example.com",
            password=cls.user_password,
            role=User.Roles.SUPPORTER,
            is_staff=False,
        )

    def setUp(self):
        # Create UserAdmin instance in setUp to avoid deepcopy issues with module references
        from apps.accounts.admin import UserAdmin

        self.user_admin = UserAdmin(User, None)

    # ========== Super Admin Tests ==========

    def test_super_admin_has_all_permissions(self):
        """Super admin can change and delete all users"""
        targets = [self.admin, self.manager, self.creator, self.supporter]
        for target in targets:
            self.assertTrue(self.user_admin.has_change_permission(self.super_admin, target))
            self.assertTrue(self.user_admin.has_delete_permission(self.super_admin, target))

    def test_super_admin_can_change_self(self):
        """Super admin can change their own account"""
        self.assertTrue(self.user_admin.has_change_permission(self.super_admin, self.super_admin))

    # ========== Admin Tests ==========

    def test_admin_cannot_change_or_delete_super_admin(self):
        """Admin cannot change or delete super admin"""
        self.assertFalse(self.user_admin.has_change_permission(self.admin, self.super_admin))
        self.assertFalse(self.user_admin.has_delete_permission(self.admin, self.super_admin))

    def test_admin_can_change_and_delete_lower_roles(self):
        """Admin can change and delete manager, creator, supporter"""
        targets = [self.manager, self.creator, self.supporter]
        for target in targets:
            self.assertTrue(self.user_admin.has_change_permission(self.admin, target))
            self.assertTrue(self.user_admin.has_delete_permission(self.admin, target))

    # ========== Manager Tests ==========

    def test_manager_cannot_change_or_delete_admin_and_above(self):
        """Manager cannot change or delete admin or super admin"""
        self.assertFalse(self.user_admin.has_change_permission(self.manager, self.super_admin))
        self.assertFalse(self.user_admin.has_delete_permission(self.manager, self.super_admin))
        self.assertFalse(self.user_admin.has_change_permission(self.manager, self.admin))
        self.assertFalse(self.user_admin.has_delete_permission(self.manager, self.admin))

    def test_manager_can_change_and_delete_creator_supporter(self):
        """Manager can change and delete creator and supporter"""
        targets = [self.creator, self.supporter]
        for target in targets:
            self.assertTrue(self.user_admin.has_change_permission(self.manager, target))
            self.assertTrue(self.user_admin.has_delete_permission(self.manager, target))

    # ========== List View Tests ==========

    def test_staff_can_access_list_view(self):
        """Staff users can access the user list view"""
        self.assertTrue(self.user_admin.has_change_permission(self.super_admin, None))
        self.assertTrue(self.user_admin.has_change_permission(self.admin, None))
        self.assertTrue(self.user_admin.has_change_permission(self.manager, None))

    def test_non_staff_cannot_access_list_view(self):
        """Non-staff users cannot access the user list view"""
        self.assertFalse(self.user_admin.has_change_permission(self.creator, None))
        self.assertFalse(self.user_admin.has_change_permission(self.supporter, None))

    # ========== Non-staff Tests ==========

    def test_non_staff_cannot_delete_any_user(self):
        """Non-staff users cannot delete any user"""
        self.assertFalse(self.user_admin.has_delete_permission(self.creator, self.creator))
        self.assertFalse(self.user_admin.has_delete_permission(self.creator, self.supporter))

    def test_creator_can_change_self(self):
        """Creator can change their own account"""
        self.assertTrue(self.user_admin.has_change_permission(self.creator, self.creator))

    def test_supporter_can_change_self(self):
        """Supporter can change their own account"""
        self.assertTrue(self.user_admin.has_change_permission(self.supporter, self.supporter))


def _mock_request(user):
    """Create a mock request object with the given user."""
    request = Mock()
    request.user = user
    return request


class UserAdminQuerysetTestCase(BaseTestCase):
    """Test cases for UserAdmin get_queryset method - filtering users by role hierarchy"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user_password = "testpass123"
        cls.super_admin = User.objects.create_superuser(
            username="superadmin",
            email="superadmin@example.com",
            password=cls.user_password,
            role=User.Roles.SUPER_ADMIN,
        )
        cls.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password=cls.user_password,
            role=User.Roles.ADMIN,
            is_staff=True,
        )
        cls.manager = User.objects.create_user(
            username="manager",
            email="manager@example.com",
            password=cls.user_password,
            role=User.Roles.MANAGER,
            is_staff=True,
        )
        cls.creator = User.objects.create_user(
            username="creator",
            email="creator@example.com",
            password=cls.user_password,
            role=User.Roles.CREATOR,
            is_staff=False,
        )
        cls.supporter = User.objects.create_user(
            username="supporter",
            email="supporter@example.com",
            password=cls.user_password,
            role=User.Roles.SUPPORTER,
            is_staff=False,
        )

    def setUp(self):
        from apps.accounts.admin import UserAdmin

        self.user_admin = UserAdmin(User, None)

    def _get_queryset_for_user(self, user):
        """Helper to get the queryset filtered for a specific user"""
        request = _mock_request(user)
        return self.user_admin.get_queryset(request)

    def test_super_admin_sees_all_users(self):
        """Super admin should see all users including themselves"""
        qs = self._get_queryset_for_user(self.super_admin)
        user_ids = list(qs.values_list("pk", flat=True))
        self.assertIn(self.super_admin.pk, user_ids)
        self.assertIn(self.admin.pk, user_ids)
        self.assertIn(self.manager.pk, user_ids)
        self.assertIn(self.creator.pk, user_ids)
        self.assertIn(self.supporter.pk, user_ids)

    def test_admin_sees_self_and_lower_roles(self):
        """Admin should see themselves and users below admin level (manager, creator, supporter)"""
        qs = self._get_queryset_for_user(self.admin)
        user_ids = list(qs.values_list("pk", flat=True))
        self.assertIn(self.admin.pk, user_ids)
        self.assertIn(self.manager.pk, user_ids)
        self.assertIn(self.creator.pk, user_ids)
        self.assertIn(self.supporter.pk, user_ids)
        self.assertNotIn(self.super_admin.pk, user_ids)

    def test_manager_sees_self_and_lower_roles(self):
        """Manager should see themselves and users below manager level (creator, supporter)"""
        qs = self._get_queryset_for_user(self.manager)
        user_ids = list(qs.values_list("pk", flat=True))
        self.assertIn(self.manager.pk, user_ids)
        self.assertIn(self.creator.pk, user_ids)
        self.assertIn(self.supporter.pk, user_ids)
        self.assertNotIn(self.super_admin.pk, user_ids)
        self.assertNotIn(self.admin.pk, user_ids)

    def test_creator_sees_self_and_lower_roles(self):
        """Creator should see themselves and users below creator level (supporter)"""
        qs = self._get_queryset_for_user(self.creator)
        user_ids = list(qs.values_list("pk", flat=True))
        self.assertIn(self.creator.pk, user_ids)
        self.assertIn(self.supporter.pk, user_ids)
        self.assertNotIn(self.super_admin.pk, user_ids)
        self.assertNotIn(self.admin.pk, user_ids)
        self.assertNotIn(self.manager.pk, user_ids)

    def test_supporter_sees_only_self(self):
        """Supporter should only see themselves (no users below supporter level)"""
        qs = self._get_queryset_for_user(self.supporter)
        user_ids = list(qs.values_list("pk", flat=True))
        self.assertIn(self.supporter.pk, user_ids)
        self.assertNotIn(self.super_admin.pk, user_ids)
        self.assertNotIn(self.admin.pk, user_ids)
        self.assertNotIn(self.manager.pk, user_ids)
        self.assertNotIn(self.creator.pk, user_ids)
