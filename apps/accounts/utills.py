from datetime import timedelta

from django.conf import settings
from django.core import signing
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone


def generate_email_verification_token(user_id):
    data = {"user_id": user_id, "timestamp": timezone.now().timestamp()}
    return signing.dumps(data, salt=settings.TOKEN_SALT)


def verify_email_verification_token(token):
    try:
        data = signing.loads(
            token,
            salt=settings.TOKEN_SALT,
            max_age=timedelta(hours=settings.TOKEN_EXPIRATION_HOURS),
        )
        return data["user_id"]
    except signing.BadSignature:
        return None
    except signing.SignatureExpired:
        return None


def send_verification_email(user):
    token = generate_email_verification_token(user.id)
    verify_url = settings.SITE_BASE_URL + reverse("accounts:verify_email") + f"?token={token}"
    subject = "Verify your MeroCoffee account email"
    message = f"Hi {user.username},\n\nPlease verify your email by clicking the link below:\n \
    {verify_url}\n\nIf you did not request this, ignore this email."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
