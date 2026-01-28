from .test_activate_email import ActivateEmailViewTests
from .test_login import LoginViewTests
from .test_logout import LogoutViewTests
from .test_resend_confirmation import ResendConfirmationViewTests
from .test_roles import RoleAssignmentTests
from .test_serve_kyc_document import ServeKYCDocumentViewTests
from .test_signup import SignUpViewTests
from .test_verify_email import VerifyEmailViewTests

__all__ = [
    "LoginViewTests",
    "LogoutViewTests",
    "ResendConfirmationViewTests",
    "ServeKYCDocumentViewTests",
    "SignUpViewTests",
    "VerifyEmailViewTests",
    "ActivateEmailViewTests",
    "RoleAssignmentTests",
]
