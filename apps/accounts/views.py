from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoginForm, SignUpForm
from .utills import send_verification_email, verify_email_verification_token

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
                user_obj = User.objects.get(username=login_input)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                try:
                    user_obj = User.objects.get(email=login_input)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None

            if user is not None:
                login(request, user)
                return redirect("dashboard:dashboard")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("core:homepage")


def email_confirmation_sent_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, "accounts/email_confirmation_sent.html", {"user": user})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:dashboard")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_verification_email(user)
            messages.success(request, "A confirmation email has been sent to your inbox.")
            return redirect("accounts:email_confirmation_sent_view", user_id=user.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignUpForm()

    return render(request, "accounts/signup.html", {"form": form})


def password_reset(request):
    # TODO: Add password reset template
    return render(request, "accounts/singup.html")


def resend_confirmation_view(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if user.verified:
        messages.info(request, "Your email is already verified.")
        return redirect("accounts:login")

    send_verification_email(user)
    messages.success(request, "A new confirmation email has been sent to your inbox.")
    return redirect("accounts:email_confirmation_sent_view", user_id=user.id)


def verify_email_view(request):
    token = request.GET.get("token")
    if not token:
        messages.error(request, "Invalid verification link.")
        return redirect("accounts:login")

    user_id = verify_email_verification_token(token)
    if user_id is None:
        messages.error(request, "Verification link is invalid or expired.")
        return redirect("accounts:login")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect("accounts:login")

    if user.is_active:
        messages.info(request, "Your email is already verified. Please , login.")
    else:
        user.is_active = True
        user.save()
        messages.success(request, "Your email has been verified successfully! You can now log in.")

    return redirect("accounts:login")
