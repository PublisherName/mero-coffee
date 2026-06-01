from .test_activate_email import ActivateEmailViewTests
from .test_admin_permissions import UserAdminPermissionTestCase, UserAdminQuerysetTestCase
from .test_login import LoginViewTests
from .test_logout import LogoutViewTests
from .test_lowercase_normalization import LowercaseNormalizationTests
from .test_name_normalization import NameFieldNormalizationTests
from .test_password_reset import PasswordResetConfirmTests, PasswordResetTests
from .test_resend_confirmation import ResendConfirmationViewTests
from .test_role_group_assignment import RoleGroupAssignmentTests
from .test_serve_kyc_document import ServeKYCDocumentViewTests
from .test_signup import SignUpViewTests
from .test_validate_role_change import ValidateRoleChangeTestCase
from .test_verify_email import VerifyEmailViewTests

__all__ = [
    "ActivateEmailViewTests",
    "LoginViewTests",
    "LogoutViewTests",
    "LowercaseNormalizationTests",
    "NameFieldNormalizationTests",
    "PasswordResetConfirmTests",
    "PasswordResetTests",
    "ResendConfirmationViewTests",
    "RoleGroupAssignmentTests",
    "ServeKYCDocumentViewTests",
    "SignUpViewTests",
    "UserAdminPermissionTestCase",
    "UserAdminQuerysetTestCase",
    "ValidateRoleChangeTestCase",
    "VerifyEmailViewTests",
]
