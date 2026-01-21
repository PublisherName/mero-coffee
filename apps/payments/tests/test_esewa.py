import base64
import json
from unittest.mock import MagicMock, patch

import requests
from django.test import RequestFactory

from apps.emails.models import EmailTemplate
from apps.payments.enums import PaymentLogStatus, PaymentMethods, SupportTransactionStatus
from apps.payments.models import PaymentGateway, PaymentLog, SupportTransaction
from apps.payments.services.esewa import EsewaStrategy
from apps.payments.tests.base import BasePaymentsTestCase


class EsewaPaymentTestCase(BasePaymentsTestCase):
    def setUp(self):
        super().setUp()
        self.creator_profile = self.create_creator_profile()
        self.gateway = PaymentGateway.objects.create(
            name="eSewa",
            slug="esewa",
            merchant_id="EPAYTEST",
            secret_key="test_secret_key",
            base_url="https://epay.esewa.com.np/api/epay",
            sandbox_url="https://rc-epay.esewa.com.np/api/epay",
            is_active=True,
            is_sandbox=True,
        )
        self.factory = RequestFactory()
        self.strategy = EsewaStrategy()

    def test_get_gateway_success(self):
        """Test _get_gateway returns gateway when exists"""
        gateway = EsewaStrategy._get_gateway()
        self.assertEqual(gateway, self.gateway)

    def test_get_gateway_not_found(self):
        """Test _get_gateway returns None when gateway doesn't exist"""
        self.gateway.delete()
        gateway = EsewaStrategy._get_gateway()
        self.assertIsNone(gateway)

    def test_generate_signature(self):
        """Test _generate_signature generates correct HMAC signature"""
        secret = "test_secret"
        message = "total_amount=100.00,transaction_uuid=test123,product_code=EPAYTEST"

        signature = EsewaStrategy._generate_signature(secret, message)

        try:
            decoded = base64.b64decode(signature)
            self.assertEqual(len(decoded), 32)
        except Exception:
            self.fail("Signature is not valid base64")

    def test_create_payment_log(self):
        """Test _create_payment_log creates log entry"""
        transaction = SupportTransaction.objects.create(
            creator=self.creator_profile,
            supporter_name="Test Supporter",
            amount=100,
            message="Test message",
            payment_method=PaymentMethods.ESEWA,
            payment_status=SupportTransactionStatus.PENDING,
            transaction_id="test_txn_log",
        )

        request_payload = {"test": "request"}
        response_payload = {"test": "response"}

        log = EsewaStrategy._create_payment_log(
            transaction=transaction,
            request_payload=request_payload,
            response_payload=response_payload,
            status=PaymentLogStatus.SUCCESS,
        )

        self.assertEqual(log.transaction, transaction)
        self.assertEqual(log.payment_method, PaymentMethods.ESEWA)
        self.assertEqual(log.status, PaymentLogStatus.SUCCESS)
        self.assertEqual(log.request_payload, request_payload)
        self.assertEqual(log.response_payload, response_payload)

    def test_mark_transaction_failed_already_failed(self):
        """Test _mark_transaction_failed creates log even if already failed"""
        transaction = SupportTransaction.objects.create(
            creator=self.creator_profile,
            supporter_name="Test Supporter",
            amount=100,
            message="Test message",
            payment_method=PaymentMethods.ESEWA,
            payment_status=SupportTransactionStatus.FAILED,
            transaction_id="test_txn_already_failed",
        )

        response_data = {"status": "ERROR", "message": "Payment failed"}

        EsewaStrategy._mark_transaction_failed(transaction, response_data, PaymentLogStatus.FAILED)

        transaction.refresh_from_db()
        self.assertEqual(transaction.payment_status, SupportTransactionStatus.FAILED)

        logs_count = PaymentLog.objects.filter(
            transaction=transaction, status=PaymentLogStatus.FAILED
        ).count()
        self.assertEqual(logs_count, 1)

    def test_mark_transaction_failed_success(self):
        """Test _mark_transaction_failed marks as failed and creates log"""
        transaction = SupportTransaction.objects.create(
            creator=self.creator_profile,
            supporter_name="Test Supporter",
            amount=100,
            message="Test message",
            payment_method=PaymentMethods.ESEWA,
            payment_status=SupportTransactionStatus.PENDING,
            transaction_id="test_txn_fail",
        )

        response_data = {"status": "ERROR", "message": "Payment failed"}

        EsewaStrategy._mark_transaction_failed(transaction, response_data, PaymentLogStatus.FAILED)

        transaction.refresh_from_db()
        self.assertEqual(transaction.payment_status, SupportTransactionStatus.FAILED)

        log = PaymentLog.objects.get(transaction=transaction)
        self.assertEqual(log.status, PaymentLogStatus.FAILED)
        self.assertEqual(log.response_payload, response_data)

    def test_mark_transaction_completed_already_completed(self):
        """Test _mark_transaction_completed skips if already completed"""
        transaction = SupportTransaction.objects.create(
            creator=self.creator_profile,
            supporter_name="Test Supporter",
            amount=100,
            message="Test message",
            payment_method=PaymentMethods.ESEWA,
            payment_status=SupportTransactionStatus.COMPLETED,
            transaction_id="test_txn_already_completed",
        )

        response_data = {"status": "COMPLETE", "transaction_code": "123456"}

        EsewaStrategy._mark_transaction_completed(transaction, response_data)

        transaction.refresh_from_db()
        self.assertEqual(transaction.payment_status, SupportTransactionStatus.COMPLETED)

        logs_count = PaymentLog.objects.filter(
            transaction=transaction, status=PaymentLogStatus.SUCCESS
        ).count()
        self.assertEqual(logs_count, 0)

    @patch("apps.emails.services.EmailService.send_template_email")
    def test_mark_transaction_completed_success(self, mock_send_email):
        """Test _mark_transaction_completed marks as completed, creates log, and sends email"""
        transaction = SupportTransaction.objects.create(
            creator=self.creator_profile,
            supporter_name="Test Supporter",
            amount=100,
            message="Test message",
            payment_method=PaymentMethods.ESEWA,
            payment_status=SupportTransactionStatus.PENDING,
            transaction_id="test_txn_complete",
        )

        response_data = {"status": "COMPLETE", "transaction_code": "123456"}

        EsewaStrategy._mark_transaction_completed(transaction, response_data)

        transaction.refresh_from_db()
        self.assertEqual(transaction.payment_status, SupportTransactionStatus.COMPLETED)

        log = PaymentLog.objects.get(transaction=transaction)
        self.assertEqual(log.status, PaymentLogStatus.SUCCESS)
        self.assertEqual(log.response_payload, response_data)

        mock_send_email.assert_called_once()

    @patch("apps.emails.services.EmailService.send_template_email")
    def test_send_success_email(self, mock_send_email):
        """Test _send_success_email sends email to creator"""
        transaction = SupportTransaction.objects.create(
            creator=self.creator_profile,
            supporter_name="Test Supporter",
            amount=100,
            message="Test message",
            payment_method=PaymentMethods.ESEWA,
            payment_status=SupportTransactionStatus.PENDING,
            transaction_id="test_txn_email",
        )

        EsewaStrategy._send_success_email(transaction)

        mock_send_email.assert_called_once_with(
            template_name=EmailTemplate.Type.PAYMENT_SUCCESS_CREATOR,
            recipient=self.creator_profile.user.email,
            context={
                "creator_name": self.creator_profile.display_name
                or self.creator_profile.user.username,
                "supporter_name": transaction.supporter_name,
                "amount": transaction.amount,
                "message": transaction.message,
                "creator_dashboard_url": "http://127.0.0.1:8000/dashboard/",
            },
        )

    def test_verify_signature_missing_fields(self):
        """Test verify_signature fails with missing signature fields"""
        transaction = SupportTransaction.objects.create(
            creator=self.creator_profile,
            supporter_name="Test Supporter",
            amount=100,
            message="Test message",
            payment_method=PaymentMethods.ESEWA,
            payment_status=SupportTransactionStatus.PENDING,
            transaction_id="test_txn_sig_missing",
        )

        data = {"total_amount": "100.00", "transaction_uuid": "test123"}

        result = self.strategy.verify_signature(data, self.gateway, transaction)

        self.assertFalse(result)
        transaction.refresh_from_db()
        self.assertEqual(transaction.payment_status, SupportTransactionStatus.FAILED)

        log = PaymentLog.objects.get(transaction=transaction)
        self.assertEqual(log.status, PaymentLogStatus.SIGNATURE_MISMATCH)

    def test_verify_signature_mismatch(self):
        """Test verify_signature fails with signature mismatch"""
        transaction = SupportTransaction.objects.create(
            creator=self.creator_profile,
            supporter_name="Test Supporter",
            amount=100,
            message="Test message",
            payment_method=PaymentMethods.ESEWA,
            payment_status=SupportTransactionStatus.PENDING,
            transaction_id="test_txn_sig_mismatch",
        )

        data = {
            "total_amount": "100.00",
            "transaction_uuid": "test123",
            "product_code": "EPAYTEST",
            "signed_field_names": "total_amount,transaction_uuid,product_code",
            "signature": "invalid_signature",
        }

        result = self.strategy.verify_signature(data, self.gateway, transaction)

        self.assertFalse(result)
        transaction.refresh_from_db()
        self.assertEqual(transaction.payment_status, SupportTransactionStatus.FAILED)

        log = PaymentLog.objects.get(transaction=transaction)
        self.assertEqual(log.status, PaymentLogStatus.SIGNATURE_MISMATCH)

    def test_verify_signature_success(self):
        """Test verify_signature succeeds with valid signature"""
        transaction = SupportTransaction.objects.create(
            creator=self.creator_profile,
            supporter_name="Test Supporter",
            amount=100,
            message="Test message",
            payment_method=PaymentMethods.ESEWA,
            payment_status=SupportTransactionStatus.PENDING,
            transaction_id="test_txn_sig_valid",
        )

        message = "total_amount=100.00,transaction_uuid=test_txn_sig_valid,product_code=EPAYTEST"
        valid_signature = EsewaStrategy._generate_signature(self.gateway.secret_key, message)

        data = {
            "total_amount": "100.00",
            "transaction_uuid": "test_txn_sig_valid",
            "product_code": "EPAYTEST",
            "signed_field_names": "total_amount,transaction_uuid,product_code",
            "signature": valid_signature,
        }

        result = self.strategy.verify_signature(data, self.gateway, transaction)

        self.assertTrue(result)
        transaction.refresh_from_db()
        self.assertEqual(transaction.payment_status, SupportTransactionStatus.PENDING)

    @patch("requests.get")
    def test_verify_payment_gateway_not_found(self, mock_get):
        """Test verify_payment fails when gateway not found"""
        transaction = SupportTransaction.objects.create(
            creator=self.creator_profile,
            supporter_name="Test Supporter",
            amount=100,
            message="Test message",
            payment_method=PaymentMethods.ESEWA,
            payment_status=SupportTransactionStatus.PENDING,
            transaction_id="test_txn_verify_no_gateway",
        )

        self.gateway.delete()

        result, error = EsewaStrategy.verify_payment(transaction)

        self.assertIsNone(result)
        self.assertEqual(error, "Payment gateway not configured")

    @patch("requests.get")
    def test_verify_payment_success_complete(self, mock_get):
        """Test verify_payment succeeds with COMPLETE status"""
        transaction = SupportTransaction.objects.create(
            creator=self.creator_profile,
            supporter_name="Test Supporter",
            amount=100,
            message="Test message",
            payment_method=PaymentMethods.ESEWA,
            payment_status=SupportTransactionStatus.PENDING,
            transaction_id="test_txn_verify_complete",
        )

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "COMPLETE",
            "transaction_code": "123456",
            "total_amount": "100.00",
        }
        mock_get.return_value = mock_response

        result, error = EsewaStrategy.verify_payment(transaction)

        self.assertIsNotNone(result)
        self.assertIsNone(error)
        self.assertEqual(result["status"], "COMPLETE")

        log = PaymentLog.objects.get(transaction=transaction)
        self.assertEqual(log.status, PaymentLogStatus.API_COMPLETE)

    @patch("requests.get")
    def test_verify_payment_pending_status(self, mock_get):
        """Test verify_payment fails with PENDING status"""
        transaction = SupportTransaction.objects.create(
            creator=self.creator_profile,
            supporter_name="Test Supporter",
            amount=100,
            message="Test message",
            payment_method=PaymentMethods.ESEWA,
            payment_status=SupportTransactionStatus.PENDING,
            transaction_id="test_txn_verify_pending",
        )

        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "PENDING", "message": "Payment is pending"}
        mock_get.return_value = mock_response

        result, error = EsewaStrategy.verify_payment(transaction)

        self.assertIsNone(result)
        self.assertIn("Payment verification failed", error)

        log = PaymentLog.objects.get(transaction=transaction)
        self.assertEqual(log.status, PaymentLogStatus.API_PENDING)

    @patch("requests.get")
    def test_verify_payment_timeout(self, mock_get):
        """Test verify_payment handles timeout"""
        transaction = SupportTransaction.objects.create(
            creator=self.creator_profile,
            supporter_name="Test Supporter",
            amount=100,
            message="Test message",
            payment_method=PaymentMethods.ESEWA,
            payment_status=SupportTransactionStatus.PENDING,
            transaction_id="test_txn_verify_timeout",
        )

        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

        result, error = EsewaStrategy.verify_payment(transaction)

        self.assertIsNone(result)
        self.assertIn("Payment verification timed out", error)

        log = PaymentLog.objects.get(transaction=transaction)
        self.assertEqual(log.status, PaymentLogStatus.API_ERROR)

    def test_handle_status_complete(self):
        """Test handle_status with COMPLETE status"""
        transaction = SupportTransaction.objects.create(
            creator=self.creator_profile,
            supporter_name="Test Supporter",
            amount=100,
            message="Test message",
            payment_method=PaymentMethods.ESEWA,
            payment_status=SupportTransactionStatus.PENDING,
            transaction_id="test_txn_status_complete",
        )

        data = {"status": "COMPLETE", "transaction_code": "123456"}

        template, context = EsewaStrategy.handle_status(transaction, self.gateway, data, "ref123")

        self.assertEqual(template, "payment_success.html")
        self.assertEqual(context["transaction"], transaction)
        self.assertEqual(context["gateway"], self.gateway)
        self.assertEqual(context["transaction_code"], "123456")
        self.assertEqual(context["ref_id"], "ref123")

        transaction.refresh_from_db()
        self.assertEqual(transaction.payment_status, SupportTransactionStatus.COMPLETED)

    def test_handle_status_pending(self):
        """Test handle_status with PENDING status"""
        transaction = SupportTransaction.objects.create(
            creator=self.creator_profile,
            supporter_name="Test Supporter",
            amount=100,
            message="Test message",
            payment_method=PaymentMethods.ESEWA,
            payment_status=SupportTransactionStatus.PENDING,
            transaction_id="test_txn_status_pending",
        )

        data = {"status": "PENDING", "message": "Payment pending"}

        template, context = EsewaStrategy.handle_status(transaction, self.gateway, data, None)

        self.assertEqual(template, "payment_failed.html")
        self.assertIn("Payment is still pending", context["error"])
        self.assertEqual(context["transaction"], transaction)

        log = PaymentLog.objects.get(transaction=transaction)
        self.assertEqual(log.status, PaymentLogStatus.PENDING)

    def test_handle_status_full_refund(self):
        """Test handle_status with FULL_REFUND status"""
        transaction = SupportTransaction.objects.create(
            creator=self.creator_profile,
            supporter_name="Test Supporter",
            amount=100,
            message="Test message",
            payment_method=PaymentMethods.ESEWA,
            payment_status=SupportTransactionStatus.PENDING,
            transaction_id="test_txn_status_refund",
        )

        data = {"status": "FULL_REFUND", "refund_amount": "100.00"}

        template, context = EsewaStrategy.handle_status(transaction, self.gateway, data, None)

        self.assertEqual(template, "payment_failed.html")
        self.assertIn("Payment was refunded", context["error"])
        self.assertEqual(context["transaction"], transaction)

        transaction.refresh_from_db()
        self.assertEqual(transaction.payment_status, SupportTransactionStatus.FAILED)

        log = PaymentLog.objects.get(transaction=transaction)
        self.assertEqual(log.status, PaymentLogStatus.FULL_REFUND)

    def test_handle_status_ambiguous(self):
        """Test handle_status with AMBIGUOUS status"""
        transaction = SupportTransaction.objects.create(
            creator=self.creator_profile,
            supporter_name="Test Supporter",
            amount=100,
            message="Test message",
            payment_method=PaymentMethods.ESEWA,
            payment_status=SupportTransactionStatus.PENDING,
            transaction_id="test_txn_status_ambiguous",
        )

        data = {"status": "AMBIGUOUS", "message": "Status unclear"}

        template, context = EsewaStrategy.handle_status(transaction, self.gateway, data, None)

        self.assertEqual(template, "payment_failed.html")
        self.assertIn("Payment status is unclear", context["error"])
        self.assertEqual(context["transaction"], transaction)

        log = PaymentLog.objects.get(transaction=transaction)
        self.assertEqual(log.status, PaymentLogStatus.AMBIGUOUS)

    def test_handle_status_cancelled(self):
        """Test handle_status with CANCELLED status"""
        transaction = SupportTransaction.objects.create(
            creator=self.creator_profile,
            supporter_name="Test Supporter",
            amount=100,
            message="Test message",
            payment_method=PaymentMethods.ESEWA,
            payment_status=SupportTransactionStatus.PENDING,
            transaction_id="test_txn_status_cancelled",
        )

        data = {"status": "CANCELED", "message": "User cancelled"}

        template, context = EsewaStrategy.handle_status(transaction, self.gateway, data, None)

        self.assertEqual(template, "payment_failed.html")
        self.assertIn("Payment was cancelled", context["error"])
        self.assertEqual(context["transaction"], transaction)

        transaction.refresh_from_db()
        self.assertEqual(transaction.payment_status, SupportTransactionStatus.FAILED)

        log = PaymentLog.objects.get(transaction=transaction)
        self.assertEqual(log.status, PaymentLogStatus.CANCELED)

    def test_handle_status_unknown(self):
        """Test handle_status with unknown status"""
        transaction = SupportTransaction.objects.create(
            creator=self.creator_profile,
            supporter_name="Test Supporter",
            amount=100,
            message="Test message",
            payment_method=PaymentMethods.ESEWA,
            payment_status=SupportTransactionStatus.PENDING,
            transaction_id="test_txn_status_unknown",
        )

        data = {"status": "UNKNOWN_STATUS", "message": "Unknown status"}

        template, context = EsewaStrategy.handle_status(transaction, self.gateway, data, None)

        self.assertEqual(template, "payment_failed.html")
        self.assertIn("Unknown payment status", context["error"])
        self.assertEqual(context["transaction"], transaction)

        log = PaymentLog.objects.get(transaction=transaction)
        self.assertEqual(log.status, PaymentLogStatus.UNKNOWN_STATUS)

    def test_get_payment_context_gateway_not_found(self):
        """Test get_payment_context when gateway not found"""
        transaction = SupportTransaction.objects.create(
            creator=self.creator_profile,
            supporter_name="Test Supporter",
            amount=100,
            message="Test message",
            payment_method=PaymentMethods.ESEWA,
            payment_status=SupportTransactionStatus.PENDING,
            transaction_id="test_txn_context_no_gateway",
        )

        self.gateway.delete()

        result = self.strategy.get_payment_context(transaction)

        self.assertIn("error", result)
        self.assertEqual(result["transaction"], transaction)

    def test_get_payment_context_success(self):
        """Test get_payment_context successful creation"""
        transaction = SupportTransaction.objects.create(
            creator=self.creator_profile,
            supporter_name="Test Supporter",
            amount=100,
            message="Test message",
            payment_method=PaymentMethods.ESEWA,
            payment_status=SupportTransactionStatus.PENDING,
            transaction_id="test_txn_context_success",
        )

        request = self.factory.get("/payments/esewa/")
        result = self.strategy.get_payment_context(transaction, request)

        self.assertIn("payment_url", result)
        self.assertIn("payment_params", result)
        self.assertEqual(result["method"], "POST")

        params = result["payment_params"]
        self.assertEqual(params["amount"], "100.00")
        self.assertEqual(params["total_amount"], "100.00")
        self.assertEqual(params["transaction_uuid"], transaction.transaction_id)
        self.assertEqual(params["product_code"], "EPAYTEST")
        self.assertIn("signature", params)
        self.assertEqual(
            params["signed_field_names"], "total_amount,transaction_uuid,product_code"
        )

        transaction.refresh_from_db()
        self.assertIsNotNone(transaction.transaction_id)

    def test_handle_failure_no_data(self):
        """Test handle_failure with no encoded data"""
        template, context = EsewaStrategy.handle_failure(None)

        self.assertEqual(template, "payment_failed.html")
        self.assertIn("Payment verification failed", context["error"])

    def test_handle_failure_invalid_base64(self):
        """Test handle_failure with invalid base64 data"""
        template, context = EsewaStrategy.handle_failure("invalid_base64!")

        self.assertEqual(template, "payment_failed.html")
        self.assertIn("Payment verification failed", context["error"])

    def test_handle_failure_invalid_json(self):
        """Test handle_failure with invalid JSON data"""
        invalid_json = base64.b64encode(b"not json").decode()
        template, context = EsewaStrategy.handle_failure(invalid_json)

        self.assertEqual(template, "payment_failed.html")
        self.assertIn("Payment verification failed", context["error"])

    def test_handle_failure_no_transaction_uuid(self):
        """Test handle_failure with missing transaction_uuid"""
        data = {"status": "ERROR", "message": "Payment failed"}
        encoded_data = base64.b64encode(json.dumps(data).encode()).decode()

        template, context = EsewaStrategy.handle_failure(encoded_data)

        self.assertEqual(template, "payment_failed.html")
        self.assertIn("Payment verification failed", context["error"])

    def test_handle_failure_transaction_not_found(self):
        """Test handle_failure with non-existent transaction"""
        data = {"transaction_uuid": "nonexistent_uuid", "status": "ERROR"}
        encoded_data = base64.b64encode(json.dumps(data).encode()).decode()

        template, context = EsewaStrategy.handle_failure(encoded_data)

        self.assertEqual(template, "payment_failed.html")
        self.assertEqual(context["error"], "Transaction not found")

    def test_handle_failure_success(self):
        """Test handle_failure successfully marks transaction as failed"""
        transaction = SupportTransaction.objects.create(
            creator=self.creator_profile,
            supporter_name="Test Supporter",
            amount=100,
            message="Test message",
            payment_method=PaymentMethods.ESEWA,
            payment_status=SupportTransactionStatus.PENDING,
            transaction_id="test_txn_failure",
        )

        data = {
            "transaction_uuid": transaction.transaction_id,
            "status": "ERROR",
            "message": "Payment failed",
        }
        encoded_data = base64.b64encode(json.dumps(data).encode()).decode()

        template, context = EsewaStrategy.handle_failure(encoded_data)

        self.assertEqual(template, "payment_failed.html")
        self.assertEqual(context["transaction"], transaction)
        self.assertIn("Payment verification failed", context["error"])

        transaction.refresh_from_db()
        self.assertEqual(transaction.payment_status, SupportTransactionStatus.FAILED)

        log = PaymentLog.objects.get(transaction=transaction)
        self.assertEqual(log.status, PaymentLogStatus.FAILED)
