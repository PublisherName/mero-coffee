from apps.payments.services.esewa import EsewaStrategy
from apps.payments.services.paypal import PayPalStrategy
from apps.payments.services.stripe import StripeStrategy

from ..enums import PaymentMethods


class PaymentFactory:
    @staticmethod
    def get_strategy(slug: str):
        if slug == PaymentMethods.ESEWA:
            return EsewaStrategy()

        elif slug == PaymentMethods.STRIPE:
            return StripeStrategy()

        elif slug == PaymentMethods.PAYPAL:
            return PayPalStrategy()

        else:
            raise ValueError(f"Unknown payment gateway: {slug}")
