from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django_ratelimit.decorators import ratelimit

from apps.emails.services import EmailService

from .forms import NewsletterSubscribeForm
from .models import NewsletterSubscriber


@ratelimit(
    key="ip", rate=lambda group, request: settings.RATELIMIT_RATE, method="POST", block=True
)
def subscribe(request):
    if request.method == "POST":
        form = NewsletterSubscribeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)

            if created or not subscriber.is_verified:
                verification_url = settings.SITE_BASE_URL.rstrip("/") + reverse(
                    "newsletter:verify_email", args=[subscriber.verification_token]
                )

                context = {
                    "verification_url": verification_url,
                    "email": subscriber.email,
                }

                EmailService.send_template_email(
                    template_name="newsletter_verification",
                    recipient=subscriber.email,
                    context=context,
                )
                messages.success(request, "Please check your email to verify your subscription.")
            else:
                messages.info(request, "You are already subscribed to our newsletter.")

            return redirect("core:homepage")
        else:
            for errors in form.errors.values():
                for error in errors:
                    messages.error(request, f"{error}")
            return redirect("core:homepage")

    return redirect("core:homepage")


@ratelimit(key="ip", rate=lambda group, request: settings.RATELIMIT_RATE, method="GET", block=True)
def verify_email(request, token):
    try:
        subscriber = NewsletterSubscriber.objects.get(verification_token=token)
        if not subscriber.is_verified:
            subscriber.is_verified = True
            subscriber.verified_at = timezone.now()
            subscriber.save()

            context = {
                "email": subscriber.email,
            }

            EmailService.send_template_email(
                template_name="newsletter_welcome", recipient=subscriber.email, context=context
            )

            messages.success(
                request,
                "Email verified successfully! Welcome to MeroCoffee newsletter.",
            )
        else:
            messages.info(request, "Your email is already verified.")
    except NewsletterSubscriber.DoesNotExist:
        messages.error(request, "Invalid verification link.")

    return redirect("core:homepage")
