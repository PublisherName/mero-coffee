from django.core.management.base import BaseCommand

from apps.payments.models import PaymentGateway


class Command(BaseCommand):
    help = "Seeds the database with default payment gateways (eSewa, Khalti)"

    def handle(self, *args, **options):
        gateways = [
            {
                "name": "eSewa",
                "slug": "esewa",
                "is_active": True,
                "is_sandbox": True,
                "base_url": "https://epay.esewa.com.np/api/epay",
                "sandbox_url": "https://rc-epay.esewa.com.np/api/epay",
                "success_url": "http://127.0.0.1/esewa/success/",
                "failure_url": "http://127.0.0.1/esewa/failure/",
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
                "sanbox_url": "https://dev.khalti.com/api/v2/",
                "description": "Pay with Khalti",
                "brand_color": "#5c2d91",
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
