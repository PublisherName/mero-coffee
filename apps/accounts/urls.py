from django.urls import path

from apps.accounts.views import (
    email_confirmation_sent_view,
    login_view,
    logout_view,
    password_reset,
    resend_confirmation_view,
    signup_view,
    verify_email_view,
)

app_name = "accounts"

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("reset/", password_reset, name="password_reset"),
    path(
        "email-confirmation/sent/<int:user_id>/",
        email_confirmation_sent_view,
        name="email_confirmation_sent_view",
    ),
    path(
        "email-confirmation/resend/<int:user_id>/",
        resend_confirmation_view,
        name="resend_confirmation",
    ),
    path("verify-email/", verify_email_view, name="verify_email"),
]
