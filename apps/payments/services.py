import base64
import hashlib
import hmac
import json
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import requests
from django.urls import reverse

from apps.payments.models import PaymentGateway, PaymentLog, SupportTransaction


class PaymentStrategy(ABC):
    """Abstract base class for payment strategies"""

    @abstractmethod
    def get_payment_context(self, transaction: SupportTransaction, request=None) -> Dict[str, Any]:
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
    def base64_decode(encoded_data: Optional[str]):
        if not encoded_data:
            return None, "Invalid payment response - no data received"

        try:
            decoded_bytes = base64.b64decode(encoded_data)
            decoded_str = decoded_bytes.decode("utf-8")
            data = json.loads(decoded_str)
            return data, None

        except (base64.binascii.Error, json.JSONDecodeError, UnicodeDecodeError) as e:
            return None, f"Invalid payment response format: {str(e)}"


class PaymentFactory:
    @staticmethod
    def get_strategy(slug: str) -> PaymentStrategy:
        if slug == "esewa":
            return EsewaStrategy()
        else:
            raise ValueError(f"Unknown payment gateway: {slug}")


class EsewaStrategy(PaymentStrategy):
    """All eSewa payment logic encapsulated here"""

    def verify_signature(
        self, data: dict, gateway: PaymentGateway, transaction: SupportTransaction
    ) -> bool:
        signed_field_names = data.get("signed_field_names", "")
        signature = data.get("signature")

        message_parts = []
        for field in signed_field_names.split(","):
            field_value = data.get(field, "")
            message_parts.append(f"{field}={field_value}")
        message = ",".join(message_parts)

        expected_signature = self._generate_signature(gateway.secret_key.strip(), message)

        if signature != expected_signature:
            transaction.payment_status = "failed"
            transaction.save()

            PaymentLog.objects.create(
                transaction=transaction,
                gateway=PaymentLog.Gateways.ESEWA,
                request_payload={},
                response_payload=data,
                status="signature_mismatch",
            )

            return False
        return True

    @staticmethod
    def verify_payment(transaction: SupportTransaction):
        gateway = PaymentGateway.objects.get(slug="esewa")
        base_url = gateway.sandbox_url if gateway.is_sandbox else gateway.base_url
        status_url = f"{base_url}/transaction/status/"
        params = {
            "product_code": gateway.merchant_id.strip(),
            "total_amount": float(transaction.amount),
            "transaction_uuid": transaction.transaction_id,
        }

        try:
            response = requests.get(status_url, params=params, timeout=10)
            response.raise_for_status()
            api_response = response.json()
            api_status = api_response.get("status")
            PaymentLog.objects.create(
                transaction=transaction,
                gateway=PaymentLog.Gateways.ESEWA,
                request_payload={"action": "double_verification"},
                response_payload=api_response,
                status=f"api_{api_status.lower() if api_status else 'unknown'}",
            )
            if api_status != "COMPLETE":
                return None, f"Payment verification failed (Status: {api_status})"
            return api_response, None
        except requests.RequestException as e:
            PaymentLog.objects.create(
                transaction=transaction,
                gateway=PaymentLog.Gateways.ESEWA,
                request_payload={"action": "double_verification_failed"},
                response_payload={"error": str(e)},
                status="api_error",
            )
            return None, "Payment verification failed. Please contact support."

    @staticmethod
    def handle_status(
        transaction: SupportTransaction,
        gateway: PaymentGateway,
        data: dict,
        ref_id: Optional[str],
    ):
        status = data.get("status")
        transaction_code = data.get("transaction_code")

        if status == "COMPLETE":
            transaction.payment_status = "completed"
            transaction.save()
            PaymentLog.objects.create(
                transaction=transaction,
                gateway=PaymentLog.Gateways.ESEWA,
                request_payload={},
                response_payload=data,
                status="success",
            )
            context = {
                "transaction": transaction,
                "gateway": gateway,
                "payment_data": data,
                "transaction_code": transaction_code,
                "ref_id": ref_id,
            }
            return "payment_success.html", context

        if status == "PENDING":
            PaymentLog.objects.create(
                transaction=transaction,
                gateway=PaymentLog.Gateways.ESEWA,
                request_payload={},
                response_payload=data,
                status="pending",
            )
            return (
                "payment_failed.html",
                {
                    "error": "Payment is still pending. Please wait for confirmation.",
                    "transaction": transaction,
                },
            )

        if status in ["FULL_REFUND", "PARTIAL_REFUND"]:
            transaction.payment_status = "failed"
            transaction.save()
            PaymentLog.objects.create(
                transaction=transaction,
                gateway=PaymentLog.Gateways.ESEWA,
                request_payload={},
                response_payload=data,
                status=status.lower(),
            )
            return (
                "payment_failed.html",
                {
                    "error": f"Payment was refunded ({status.replace('_', ' ').title()})",
                    "transaction": transaction,
                },
            )

        if status == "AMBIGUOUS":
            PaymentLog.objects.create(
                transaction=transaction,
                gateway=PaymentLog.Gateways.ESEWA,
                request_payload={},
                response_payload=data,
                status="ambiguous",
            )
            return (
                "payment_failed.html",
                {
                    "error": "Payment status is unclear. Please contact support.",
                    "transaction": transaction,
                },
            )

        if status in ["NOT_FOUND", "CANCELED"]:
            transaction.payment_status = "failed"
            transaction.save()
            PaymentLog.objects.create(
                transaction=transaction,
                gateway=PaymentLog.Gateways.ESEWA,
                request_payload={},
                response_payload=data,
                status=status.lower(),
            )
            error_msg = (
                "Payment session expired" if status == "NOT_FOUND" else "Payment was cancelled"
            )
            return "payment_failed.html", {"error": error_msg, "transaction": transaction}

        PaymentLog.objects.create(
            transaction=transaction,
            gateway=PaymentLog.Gateways.ESEWA,
            request_payload={},
            response_payload=data,
            status=f"unknown_status_{status.lower() if status else 'none'}",
        )
        return "payment_failed.html", {
            "error": f"Unknown payment status: {status}",
            "transaction": transaction,
        }

    def get_payment_context(self, transaction: SupportTransaction, request=None) -> Dict[str, Any]:
        gateway = PaymentGateway.objects.get(slug="esewa")

        if not transaction.transaction_id:
            transaction.transaction_id = uuid.uuid4().hex
            transaction.save()

        amount = f"{transaction.amount:.2f}"
        tax_amount = "0"
        total_amount = f"{transaction.amount + float(tax_amount):.2f}"
        transaction_uuid = transaction.transaction_id
        product_code = gateway.merchant_id.strip()

        message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"  # noqa: E501
        secret_key = gateway.secret_key.strip()
        signature = self._generate_signature(secret_key, message)

        if request:
            success_url = request.build_absolute_uri(reverse("payments:esewa_success"))
            failure_url = request.build_absolute_uri(reverse("payments:esewa_failure"))
        else:
            success_url = gateway.success_url
            failure_url = gateway.failure_url

        params = {
            "amount": amount,
            "tax_amount": tax_amount,
            "total_amount": total_amount,
            "transaction_uuid": transaction_uuid,
            "product_code": product_code,
            "product_service_charge": "0",
            "product_delivery_charge": "0",
            "success_url": success_url,
            "failure_url": failure_url,
            "signed_field_names": "total_amount,transaction_uuid,product_code",
            "signature": signature,
        }

        payment_base_url = gateway.sandbox_url if gateway.is_sandbox else gateway.base_url
        payment_url = f"{payment_base_url}/main/v2/form"
        return {
            "payment_url": payment_url,
            "payment_params": params,
            "method": "POST",
        }

    @staticmethod
    def _generate_signature(secret: str, message: str) -> str:
        hmac_sha256 = hmac.new(secret.encode(), message.encode(), hashlib.sha256)
        digest = hmac_sha256.digest()
        signature = base64.b64encode(digest).decode("utf-8")
        return signature

    @staticmethod
    def handle_failure(encoded_data: Optional[str]):
        if not encoded_data:
            return "payment_failed.html", {"error": "Payment was cancelled or failed"}

        try:
            decoded_bytes = base64.b64decode(encoded_data)
            decoded_str = decoded_bytes.decode("utf-8")
            data = json.loads(decoded_str)
        except (base64.binascii.Error, json.JSONDecodeError, UnicodeDecodeError):
            return "payment_failed.html", {"error": "Payment was cancelled or failed"}

        transaction_uuid = data.get("transaction_uuid")

        if transaction_uuid:
            transaction = SupportTransaction.objects.filter(
                transaction_id=transaction_uuid
            ).first()
            if transaction:
                transaction.payment_status = "failed"
                transaction.save()

                PaymentLog.objects.create(
                    transaction=transaction,
                    gateway=PaymentLog.Gateways.ESEWA,
                    request_payload={},
                    response_payload=data,
                    status="failed",
                )
                return "payment_failed.html", {
                    "transaction": transaction,
                    "error": "Payment was cancelled or failed",
                }
            else:
                return "payment_failed.html", {"error": "Transaction not found"}
        else:
            return "payment_failed.html", {"error": "Payment was cancelled or failed"}
