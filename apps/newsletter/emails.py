from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse


def send_newsletter_verification_email(subscriber):
    verification_url = settings.SITE_BASE_URL.rstrip("/") + reverse(
        "newsletter:verify_email", args=[subscriber.verification_token]
    )

    html_message = render_to_string(
        "newsletter/email/verification.html",
        {"verification_url": verification_url, "email": subscriber.email},
    )

    send_mail(
        subject="Verify your MeroCoffee Newsletter Subscription",
        message=f"Click this link to verify: {verification_url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[subscriber.email],
        html_message=html_message,
    )


def send_newsletter_welcome_email(subscriber):
    html_message = render_to_string(
        "newsletter/email/welcome.html",
        {"email": subscriber.email, "site_url": settings.SITE_BASE_URL},
    )

    send_mail(
        subject="Welcome to MeroCoffee Newsletter!",
        message="Welcome to MeroCoffee Newsletter!",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[subscriber.email],
        html_message=html_message,
    )
