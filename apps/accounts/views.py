from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetConfirmView
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django_ratelimit.decorators import ratelimit

from apps.accounts.decorators import role_required
from apps.accounts.forms import ActivateEmailForm
from apps.emails.services import EmailService

from .forms import LoginForm, SignUpForm
from .models import KYC

User = get_user_model()


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:dashboard")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            login_input = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = None
            try:
                user_obj = User.objects.get(username__iexact=login_input)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                try:
                    user_obj = User.objects.get(email__iexact=login_input)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None
            if user is not None:
                if user.role != User.Roles.CREATOR:
                    messages.error(
                        request,
                        "Access is restricted to creators only. "
                        "Supporters can enjoy the platform without logging in.",
                    )
                elif not user.is_verified:
                    messages.error(request, "Please verify your email before logging in.")
                else:
                    login(request, user)
                    return redirect("dashboard:dashboard")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("core:homepage")


def email_confirmation_sent_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, "email_confirmation_sent.html", {"user_id": user.id})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:dashboard")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            verify_url = settings.SITE_BASE_URL + reverse(
                "accounts:verify_email", kwargs={"uidb64": uid, "token": token}
            )

            context = {
                "username": user.username,
                "verification_url": verify_url,
                "expiration_hours": settings.TOKEN_EXPIRATION_HOURS,
            }

            EmailService.send_template_email(
                template_name="email_verification",
                recipient=user.email,
                context=context,
            )
            messages.success(request, "A confirmation email has been sent to your inbox.")
            return redirect("accounts:email_confirmation_sent_view", user_id=user.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignUpForm()

    return render(request, "signup.html", {"form": form})


@ratelimit(
    key="ip", rate=lambda group, request: settings.RATELIMIT_RATE, method="POST", block=True
)
def resend_confirmation_view(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if user.is_verified:
        messages.info(request, "Your email is already verified.")
        return redirect("accounts:login")

    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    verify_url = settings.SITE_BASE_URL + reverse(
        "accounts:verify_email", kwargs={"uidb64": uid, "token": token}
    )

    context = {
        "username": user.username,
        "verification_url": verify_url,
        "expiration_hours": settings.TOKEN_EXPIRATION_HOURS,
    }

    EmailService.send_template_email(
        template_name="email_verification",
        recipient=user.email,
        context=context,
    )
    messages.success(request, "A new confirmation email has been sent to your inbox.")
    return redirect("accounts:email_confirmation_sent_view", user_id=user.id)


@ratelimit(key="ip", rate=lambda group, request: settings.RATELIMIT_RATE, method="GET", block=True)
def verify_email_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64)
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, User.DoesNotExist):
        messages.error(request, "Invalid verification link.")
        return redirect("accounts:login")

    if not default_token_generator.check_token(user, token):
        messages.error(request, "Verification link is invalid or expired.")
        return redirect("accounts:login")

    if user.is_active and user.is_verified:
        messages.info(request, "Your email is already verified. Please log in.")
    else:
        user.is_verified = True
        user.save(update_fields=["is_verified"])
        messages.success(request, "Your email has been verified successfully! You can now log in.")

    return redirect("accounts:login")


@ratelimit(
    key="ip", rate=lambda group, request: settings.RATELIMIT_RATE, method="POST", block=True
)
def password_reset_view(request):
    """Custom password reset view using EmailService"""
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user = User.objects.get(email__iexact=email)

                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                password_reset_url = settings.SITE_BASE_URL + reverse(
                    "accounts:password_reset_confirm", kwargs={"uidb64": uid, "token": token}
                )

                context = {
                    "username": user.username,
                    "password_reset_url": password_reset_url,
                    "expiration_hours": settings.TOKEN_EXPIRATION_HOURS,
                }

                EmailService.send_template_email(
                    template_name="password_reset",
                    recipient=user.email,
                    context=context,
                )
                return redirect("accounts:password_reset_done")
            except User.DoesNotExist:
                return redirect("accounts:password_reset_done")
    else:
        form = PasswordResetForm()

    return render(request, "password_reset_form.html", {"form": form})


@login_required
@role_required(User.Roles.CREATOR, User.Roles.ADMIN)
def serve_kyc_document(request, kyc_id, field_name):
    kyc = get_object_or_404(KYC, id=kyc_id)

    if kyc.user != request.user and not request.user.is_superuser:
        raise Http404("Permission denied")

    allowed_fields = ["front_image", "back_image", "selfie_with_document"]
    if field_name not in allowed_fields:
        raise Http404("Invalid document type")

    file_field = getattr(kyc, field_name)
    if not file_field:
        raise Http404("File not found")

    try:
        return FileResponse(file_field.open(), content_type="image/jpeg")
    except FileNotFoundError:
        raise Http404("File not found on disk")


@ratelimit(
    key="ip", rate=lambda group, request: settings.RATELIMIT_RATE, method="POST", block=True
)
def activate_email_view(request):
    if request.method == "POST":
        form = ActivateEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            try:
                user = User.objects.get(email__iexact=email)
                return redirect("accounts:resend_confirmation", user_id=user.id)
            except User.DoesNotExist:
                messages.error(request, "No account found with this email address.")
    else:
        form = ActivateEmailForm()

    return render(request, "activate_email.html", {"form": form})


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Custom password reset confirm view that verifies user email on successful password reset"""

    template_name = "password_reset_confirm.html"
    success_url = "/password_reset_complete/"

    def form_valid(self, form):
        response = super().form_valid(form)

        user = form.user
        if not user.is_verified:
            user.is_verified = True
            user.save(update_fields=["is_verified"])
            messages.success(
                self.request,
                "Your password has been reset and your email has been verified. "
                "You can now log in.",
            )

        return response
