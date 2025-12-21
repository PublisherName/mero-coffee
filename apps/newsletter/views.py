from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from django_ratelimit.decorators import ratelimit

from .emails import send_newsletter_verification_email, send_newsletter_welcome_email
from .forms import NewsletterSubscribeForm
from .models import NewsletterSubscriber


@ratelimit(key="ip", rate=settings.RATELIMIT_RATE, method="POST", block=True)
def subscribe(request):
    if request.method == "POST":
        form = NewsletterSubscribeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)

            if created or not subscriber.is_verified:
                send_newsletter_verification_email(subscriber)
                messages.success(request, "Please check your email to verify your subscription.")
            else:
                messages.info(request, "You are already subscribed to our newsletter.")

            return redirect("core:homepage")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
            return redirect("core:homepage")

    return redirect("core:homepage")


@ratelimit(key="ip", rate=settings.RATELIMIT_RATE, method="GET", block=True)
def verify_email(request, token):
    try:
        subscriber = NewsletterSubscriber.objects.get(verification_token=token)
        if not subscriber.is_verified:
            subscriber.is_verified = True
            subscriber.verified_at = timezone.now()
            subscriber.save()

            send_newsletter_welcome_email(subscriber)

            messages.success(
                request,
                "Email verified successfully! Welcome to MeroCoffee newsletter.",
            )
        else:
            messages.info(request, "Your email is already verified.")
    except NewsletterSubscriber.DoesNotExist:
        messages.error(request, "Invalid verification link.")

    return redirect("core:homepage")
