import base64
import json
import logging
from abc import ABC, abstractmethod
from typing import Any

from apps.payments.models import PaymentGateway, SupportTransaction

logger = logging.getLogger(__name__)


class PaymentStrategy(ABC):
    """Abstract base class for payment strategies"""

    @abstractmethod
    def get_payment_context(self, transaction: SupportTransaction, request=None) -> dict[str, Any]:
        pass

    @staticmethod
    def get_transaction_and_gateway(data: dict, gateway: str):
        transaction_uuid = data.get("transaction_uuid")

        if not transaction_uuid:
            return None, None, "Invalid payment response - missing transaction ID"

        transaction = SupportTransaction.objects.filter(transaction_id=transaction_uuid).first()
        gateway = PaymentGateway.objects.filter(slug=gateway).first()

        if not transaction or not gateway:
            return None, None, "Transaction or Gateway not found"

        return transaction, gateway, None

    @staticmethod
    def base64_decode(encoded_data: str | None):
        if not encoded_data:
            return None, "Invalid payment response - no data received"

        try:
            decoded_bytes = base64.b64decode(encoded_data)
            decoded_str = decoded_bytes.decode("utf-8")
            data = json.loads(decoded_str)
            return data, None

        except (base64.binascii.Error, json.JSONDecodeError, UnicodeDecodeError) as e:
            return None, f"Invalid payment response format: {e!s}"
