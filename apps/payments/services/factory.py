from apps.payments.services.esewa import EsewaStrategy
from apps.payments.services.stripe import StripeStrategy


class PaymentFactory:
    @staticmethod
    def get_strategy(slug: str):
        if slug == "esewa":
            return EsewaStrategy()
        elif slug == "stripe":
            return StripeStrategy()
        else:
            raise ValueError(f"Unknown payment gateway: {slug}")
