from apps.payments.services.esewa import EsewaStrategy
from apps.payments.services.paypal import PayPalStrategy
from apps.payments.services.stripe import StripeStrategy


class PaymentFactory:
    @staticmethod
    def get_strategy(slug: str):
        if slug == "esewa":
            return EsewaStrategy()
        elif slug == "stripe":
            return StripeStrategy()
        elif slug == "paypal":
            return PayPalStrategy()
        else:
            raise ValueError(f"Unknown payment gateway: {slug}")
