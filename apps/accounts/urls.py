from django.contrib.auth import views as auth_views
from django.urls import path

from apps.accounts.views import (
    email_confirmation_sent_view,
    login_view,
    logout_view,
    resend_confirmation_view,
    signup_view,
    verify_email_view,
)

app_name = "accounts"

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
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
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="password_reset_form.html",
            email_template_name="includes/email/password_reset_email.html",
            subject_template_name="includes/email/password_reset_subject.txt",
            success_url="/password_reset/done/",
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="password_reset_confirm.html",
            success_url="/password_reset_complete/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "password_reset_complete/",
        auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"),
        name="password_reset_complete",
    ),
]
