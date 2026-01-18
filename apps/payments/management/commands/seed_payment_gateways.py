from django.conf import settings
from django.core.management.base import BaseCommand

from apps.payments.models import PaymentGateway


class Command(BaseCommand):
    help = "Seeds the database with default payment gateways (eSewa, Khalti, Stripe)"

    def handle(self, *args, **options):
        gateways = [
            {
                "name": "eSewa",
                "slug": "esewa",
                "is_active": True,
                "is_sandbox": True,
                "base_url": "https://epay.esewa.com.np/api/epay",
                "sandbox_url": "https://rc-epay.esewa.com.np/api/epay",
                "success_url": f"{settings.SITE_BASE_URL.rstrip('/')}/esewa/success/",
                "failure_url": f"{settings.SITE_BASE_URL.rstrip('/')}/esewa/failure/",
                "signature": "HMAC-SHA256",
                "secret_key": "8gBm/:&EnhH.1/q",
                "merchant_id": "EPAYTEST",
                "description": "Pay with eSewa",
                "brand_color": "#60bb46",
            },
            {
                "name": "Khalti",
                "slug": "khalti",
                "is_active": True,
                "is_sandbox": True,
                "base_url": "https://khalti.com/api/v2/",
                "sandbox_url": "https://dev.khalti.com/api/v2/",
                "description": "Pay with Khalti",
                "brand_color": "#5c2d91",
            },
            {
                "name": "Stripe",
                "slug": "stripe",
                "is_active": True,
                "is_sandbox": True,
                "base_url": "https://api.stripe.com/v1/",
                "sandbox_url": "https://api.stripe.com/v1/",
                "success_url": f"{settings.SITE_BASE_URL.rstrip('/')}/stripe/success/",
                "failure_url": f"{settings.SITE_BASE_URL.rstrip('/')}/stripe/cancel/",
                "description": "Pay with Stripe",
                "brand_color": "#6772e5",
                "secret_key": "sk_test_BQokikJOvBiI2HlWgH4olfQ2",
            },
        ]

        for data in gateways:
            gateway, created = PaymentGateway.objects.update_or_create(
                slug=data["slug"], defaults=data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created gateway: {gateway.name}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Updated gateway: {gateway.name}"))
