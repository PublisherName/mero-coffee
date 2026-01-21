import uuid
from unittest.mock import MagicMock, patch

from django.test import RequestFactory

from apps.emails.models import EmailTemplate
from apps.payments.models import PaymentGateway, PaymentLog, SupportTransaction
from apps.payments.services.exceptions import (
    PayPalCaptureError,
    PayPalOrderFetchError,
    PayPalTransactionNotFoundError,
)
from apps.payments.services.paypal import PayPalStrategy
from apps.payments.tests.base import BasePaymentsTestCase

PAYPAL_CLIENT_PATH = "apps.payments.services.paypal.PaypalServersdkClient"
EMAIL_SERVICE_PATH = "apps.emails.services.EmailService.send_template_email"
PAYPAL_STRATEGY_BASE = "apps.payments.services.paypal.PayPalStrategy"


class PayPalPaymentTestCase(BasePaymentsTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.gateway = PaymentGateway.objects.create(
            name="PayPal",
            slug="paypal",
            merchant_id="test_client_id",
            secret_key="test_client_secret",
            is_active=True,
            is_sandbox=True,
        )

    @classmethod
    def tearDownClass(cls):
        cls.gateway.delete()
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.creator_profile = self.create_creator_profile()
        self.factory = RequestFactory()

    def create_test_transaction(self, **overrides):
        defaults = {
            "creator": self.creator_profile,
            "supporter_name": "Test Supporter",
            "amount": 100,
            "message": "Test message",
            "payment_method": SupportTransaction.Methods.PAYPAL,
            "payment_status": SupportTransaction.Status.PENDING,
            "transaction_id": f"test_txn_{uuid.uuid4().hex[:8]}",
        }
        defaults.update(overrides)
        return SupportTransaction.objects.create(**defaults)

    @classmethod
    def create_mock_paypal_order(cls, order_id="order_123", status="APPROVED", reference_id=None):
        mock_order = MagicMock()
        mock_order.id = order_id
        mock_order.status = status

        if reference_id:
            mock_unit = MagicMock()
            mock_unit.reference_id = reference_id
            mock_order.purchase_units = [mock_unit]
        else:
            mock_order.purchase_units = None

        return mock_order

    @classmethod
    def create_mock_capture(cls, capture_id="capture_123", amount="10.00"):
        mock_capture = MagicMock()
        mock_capture.id = capture_id
        mock_capture.amount.value = amount
        return mock_capture

    def create_mock_capture_result(self, capture_id="capture_123", amount="10.00"):
        mock_capture = self.create_mock_capture(capture_id, amount)

        mock_payments = MagicMock()
        mock_payments.captures = [mock_capture]

        mock_unit = MagicMock()
        mock_unit.payments = mock_payments

        mock_result = MagicMock()
        mock_result.purchase_units = [mock_unit]
        mock_result.status = "COMPLETED"

        return mock_result

    @classmethod
    def create_mock_paypal_response(cls, is_error=False, body=None, status_code=200):
        mock_response = MagicMock()
        mock_response.is_error.return_value = is_error
        mock_response.is_success.return_value = not is_error
        mock_response.status_code = status_code
        mock_response.body = body or {"id": "test_id", "status": "CREATED"}
        return mock_response

    def test_get_client_environment(self):
        test_cases = [
            ("sandbox", True, "Environment.SANDBOX"),
            ("production", False, "Environment.PRODUCTION"),
        ]

        for name, is_sandbox, expected_env in test_cases:
            with self.subTest(name=name, is_sandbox=is_sandbox):
                self.gateway.is_sandbox = is_sandbox
                self.gateway.save()

                client = PayPalStrategy._get_client(self.gateway)

                self.assertEqual(
                    str(client.config.environment),
                    expected_env,
                    f"Expected {expected_env} environment for is_sandbox={is_sandbox}",
                )

    @patch(PAYPAL_CLIENT_PATH)
    def test_fetch_paypal_order_success(self, mock_client_class):
        mock_client = MagicMock()
        mock_response = self.create_mock_paypal_response(
            is_error=False, body={"id": "test_order_id", "status": "COMPLETED"}
        )
        mock_client.orders.get_order.return_value = mock_response
        mock_client_class.return_value = mock_client

        result = PayPalStrategy._fetch_paypal_order(mock_client, "test_token")

        self.assertEqual(result, mock_response.body)
        mock_client.orders.get_order.assert_called_once_with({"id": "test_token"})

    @patch(PAYPAL_CLIENT_PATH)
    def test_fetch_paypal_order_error(self, mock_client_class):
        mock_client = MagicMock()
        mock_response = self.create_mock_paypal_response(
            is_error=True, body="Error response", status_code=400
        )
        mock_client.orders.get_order.return_value = mock_response
        mock_client_class.return_value = mock_client

        with self.assertRaises(PayPalOrderFetchError):
            PayPalStrategy._fetch_paypal_order(mock_client, "test_token")

    def test_extract_transaction_id(self):
        test_cases = [
            ("with_reference_id", "test_txn_id", "test_txn_id"),
            ("no_units", None, None),
            ("no_reference_id", "missing", None),
        ]

        for name, reference_id, expected in test_cases:
            with self.subTest(name=name):
                mock_order = MagicMock()

                if reference_id is None:
                    mock_order.purchase_units = None
                elif reference_id == "missing":
                    mock_unit = MagicMock(spec=[])
                    mock_order.purchase_units = [mock_unit]
                else:
                    mock_unit = MagicMock()
                    mock_unit.reference_id = reference_id
                    mock_order.purchase_units = [mock_unit]

                result = PayPalStrategy._extract_transaction_id(mock_order)

                self.assertEqual(result, expected, f"Expected {expected} for scenario: {name}")

    def test_get_transaction_from_order_success(self):
        transaction = self.create_test_transaction()
        mock_order = self.create_mock_paypal_order(reference_id=transaction.transaction_id)

        result = PayPalStrategy._get_transaction_from_order(mock_order)

        self.assertEqual(result, transaction)

    def test_get_transaction_from_order_not_found(self):
        mock_order = self.create_mock_paypal_order(reference_id="nonexistent_txn")

        with self.assertRaises(PayPalTransactionNotFoundError):
            PayPalStrategy._get_transaction_from_order(mock_order)

    def test_get_transaction_from_order_no_transaction_id(self):
        mock_order = self.create_mock_paypal_order()

        with self.assertRaises(PayPalTransactionNotFoundError):
            PayPalStrategy._get_transaction_from_order(mock_order)

    def test_extract_capture_details_success(self):
        mock_capture_result = self.create_mock_capture_result(
            capture_id="capture_123", amount="10.00"
        )

        capture_id, captured_amount = PayPalStrategy._extract_capture_details(mock_capture_result)

        self.assertEqual(capture_id, "capture_123")
        self.assertEqual(captured_amount, "10.00")

    def test_extract_capture_details_no_captures(self):
        mock_capture_result = MagicMock()
        mock_unit = MagicMock()
        mock_unit.payments = None
        mock_capture_result.purchase_units = [mock_unit]

        capture_id, captured_amount = PayPalStrategy._extract_capture_details(mock_capture_result)

        self.assertIsNone(capture_id)
        self.assertIsNone(captured_amount)

    def test_create_payment_log(self):
        transaction = self.create_test_transaction()
        request_payload = {"test": "request"}
        response_payload = {"test": "response"}

        log = PayPalStrategy._create_payment_log(
            transaction=transaction,
            status=PaymentLog.Status.PAYPAL_ORDER_CREATED,
            request_payload=request_payload,
            response_payload=response_payload,
        )

        self.assertEqual(log.transaction, transaction)
        self.assertEqual(log.gateway, PaymentLog.Gateways.PAYPAL)
        self.assertEqual(log.status, PaymentLog.Status.PAYPAL_ORDER_CREATED)
        self.assertEqual(log.request_payload, request_payload)
        self.assertEqual(log.response_payload, response_payload)

    @patch(EMAIL_SERVICE_PATH)
    def test_send_success_email(self, mock_send_email):
        transaction = self.create_test_transaction()

        PayPalStrategy._send_success_email(transaction)

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

    def test_mark_transaction_completed_already_completed(self):
        transaction = self.create_test_transaction(
            payment_status=SupportTransaction.Status.COMPLETED
        )
        mock_order = self.create_mock_paypal_order()
        mock_capture_result = self.create_mock_capture_result()

        PayPalStrategy._mark_transaction_completed(
            transaction, "token", mock_order, mock_capture_result
        )

        transaction.refresh_from_db()
        self.assertEqual(transaction.payment_status, SupportTransaction.Status.COMPLETED)

        logs_count = PaymentLog.objects.filter(
            transaction=transaction, status=PaymentLog.Status.PAYPAL_PAYMENT_CAPTURED
        ).count()
        self.assertEqual(logs_count, 0, "Should not create duplicate payment log")

    @patch(EMAIL_SERVICE_PATH)
    @patch(f"{PAYPAL_STRATEGY_BASE}._create_payment_log")
    def test_mark_transaction_completed_success(self, mock_create_log, mock_send_email):
        transaction = self.create_test_transaction()
        mock_order = self.create_mock_paypal_order()
        mock_capture_result = self.create_mock_capture_result(
            capture_id="capture_123", amount="10.00"
        )

        PayPalStrategy._mark_transaction_completed(
            transaction, "token", mock_order, mock_capture_result
        )

        transaction.refresh_from_db()
        self.assertEqual(transaction.payment_status, SupportTransaction.Status.COMPLETED)

        mock_create_log.assert_called_once()
        call_args = mock_create_log.call_args
        self.assertEqual(call_args[1]["status"], PaymentLog.Status.PAYPAL_PAYMENT_CAPTURED)
        self.assertEqual(call_args[1]["request_payload"], {"token": "token"})

        response_payload = call_args[1]["response_payload"]
        self.assertEqual(response_payload["order_id"], "order_123")
        self.assertEqual(response_payload["capture_id"], "capture_123")
        self.assertEqual(response_payload["amount"], "10.00")

        mock_send_email.assert_called_once()

    def test_mark_transaction_failed_scenarios(self):
        test_cases = [
            ("already_failed", SupportTransaction.Status.FAILED, "FAILED", None, 0),
            ("capture_failed", SupportTransaction.Status.PENDING, "FAILED", "capture_failed", 1),
            ("cancelled", SupportTransaction.Status.PENDING, "CANCELLED", "cancelled", 1),
        ]

        for name, initial_status, order_status, reason, expected_log_count in test_cases:
            with self.subTest(name=name):
                transaction = self.create_test_transaction(payment_status=initial_status)
                mock_order = self.create_mock_paypal_order(status=order_status)
                mock_error_response = MagicMock()
                mock_error_response.body = f"{name} error"

                PayPalStrategy._mark_transaction_failed(
                    transaction, "token", mock_order, mock_error_response, reason
                )

                transaction.refresh_from_db()
                self.assertEqual(
                    transaction.payment_status,
                    SupportTransaction.Status.FAILED,
                    f"Transaction should be marked as FAILED for scenario: {name}",
                )

                logs_count = PaymentLog.objects.filter(transaction=transaction).count()
                self.assertEqual(
                    logs_count,
                    expected_log_count,
                    f"Expected {expected_log_count} logs for scenario: {name}",
                )

                if expected_log_count > 0:
                    log = PaymentLog.objects.get(transaction=transaction)
                    if reason == "cancelled":
                        self.assertEqual(log.status, PaymentLog.Status.CANCELLED)
                    elif reason == "capture_failed":
                        self.assertEqual(log.status, PaymentLog.Status.PAYPAL_PAYMENT_NOT_CAPTURED)

    @patch(f"{PAYPAL_STRATEGY_BASE}._mark_transaction_completed")
    def test_capture_payment_already_completed(self, mock_mark_completed):
        transaction = self.create_test_transaction(
            payment_status=SupportTransaction.Status.COMPLETED
        )
        mock_client = MagicMock()
        mock_order = self.create_mock_paypal_order()

        result_template, context = PayPalStrategy._capture_payment(
            mock_client, "token", mock_order, transaction, self.gateway
        )

        self.assertEqual(result_template, "payment_success.html")
        self.assertEqual(context["transaction"], transaction)
        self.assertEqual(context["gateway"], self.gateway)
        mock_mark_completed.assert_not_called()

    @patch(f"{PAYPAL_STRATEGY_BASE}._mark_transaction_completed")
    def test_capture_payment_order_already_completed(self, mock_mark_completed):
        transaction = self.create_test_transaction()
        mock_client = MagicMock()
        mock_order = self.create_mock_paypal_order(status="COMPLETED")

        result_template, _context = PayPalStrategy._capture_payment(
            mock_client, "token", mock_order, transaction, self.gateway
        )

        self.assertEqual(result_template, "payment_success.html")
        mock_mark_completed.assert_called_once_with(transaction, "token", mock_order, mock_order)

    @patch(f"{PAYPAL_STRATEGY_BASE}._mark_transaction_failed")
    @patch(f"{PAYPAL_STRATEGY_BASE}._mark_transaction_completed")
    def test_capture_payment_capture_success(self, mock_mark_completed, mock_mark_failed):
        transaction = self.create_test_transaction()
        mock_client = MagicMock()
        mock_order = self.create_mock_paypal_order()

        mock_capture_response = self.create_mock_paypal_response(
            is_error=False, body={"id": "capture_123", "status": "COMPLETED"}, status_code=201
        )
        mock_client.orders.capture_order.return_value = mock_capture_response

        result_template, _context = PayPalStrategy._capture_payment(
            mock_client, "token", mock_order, transaction, self.gateway
        )

        self.assertEqual(result_template, "payment_success.html")
        mock_mark_completed.assert_called_once_with(
            transaction, "token", mock_order, mock_capture_response.body
        )
        mock_mark_failed.assert_not_called()

    @patch(f"{PAYPAL_STRATEGY_BASE}._mark_transaction_failed")
    def test_capture_payment_capture_failed(self, mock_mark_failed):
        transaction = self.create_test_transaction()
        mock_client = MagicMock()
        mock_order = self.create_mock_paypal_order()

        mock_capture_response = self.create_mock_paypal_response(
            is_error=True, body="Capture failed", status_code=400
        )
        mock_client.orders.capture_order.return_value = mock_capture_response

        with self.assertRaises(PayPalCaptureError):
            PayPalStrategy._capture_payment(
                mock_client, "token", mock_order, transaction, self.gateway
            )

        mock_mark_failed.assert_called_once()

    @patch(f"{PAYPAL_STRATEGY_BASE}._mark_transaction_completed")
    @patch(f"{PAYPAL_STRATEGY_BASE}._fetch_paypal_order")
    def test_capture_payment_already_captured_error_handling(
        self, mock_fetch_order, mock_mark_completed
    ):
        transaction = self.create_test_transaction()
        mock_client = MagicMock()
        mock_order = self.create_mock_paypal_order()

        mock_client.orders.capture_order.side_effect = Exception("Order already captured")

        mock_updated_order = self.create_mock_paypal_order(status="COMPLETED")
        mock_fetch_order.return_value = mock_updated_order

        result_template, _context = PayPalStrategy._capture_payment(
            mock_client, "token", mock_order, transaction, self.gateway
        )

        self.assertEqual(result_template, "payment_success.html")
        mock_mark_completed.assert_called_once_with(
            transaction, "token", mock_updated_order, mock_updated_order
        )

    @patch(f"{PAYPAL_STRATEGY_BASE}._get_client")
    @patch(f"{PAYPAL_STRATEGY_BASE}._create_payment_log")
    def test_get_payment_context_gateway_not_found(self, mock_create_log, mock_get_client):
        transaction = self.create_test_transaction()

        PaymentGateway.objects.filter(slug="paypal").delete()

        result = PayPalStrategy.get_payment_context(transaction)

        self.assertIn("error", result)
        self.assertEqual(result["transaction"], transaction)

        self.gateway = PaymentGateway.objects.create(
            name="PayPal",
            slug="paypal",
            merchant_id="test_client_id",
            secret_key="test_client_secret",
            is_active=True,
            is_sandbox=True,
        )

    @patch(f"{PAYPAL_STRATEGY_BASE}._get_client")
    @patch(f"{PAYPAL_STRATEGY_BASE}._create_payment_log")
    def test_get_payment_context_success(self, mock_create_log, mock_get_client):
        transaction = self.create_test_transaction()

        mock_client = MagicMock()
        mock_link = MagicMock()
        mock_link.rel = "approve"
        mock_link.href = "https://paypal.com/approve"

        mock_body = MagicMock()
        mock_body.id = "order_123"
        mock_body.status = "CREATED"
        mock_body.links = [mock_link]

        mock_response = MagicMock()
        mock_response.is_success.return_value = True
        mock_response.body = mock_body

        mock_client.orders.create_order.return_value = mock_response
        mock_get_client.return_value = mock_client

        request = self.factory.get("/payments/paypal/")
        result = PayPalStrategy.get_payment_context(transaction, request)

        self.assertIn("payment_url", result)
        self.assertIn("payment_params", result)
        self.assertEqual(result["payment_params"]["token"], "order_123")
        self.assertEqual(result["method"], "GET")

        mock_create_log.assert_called_once()
        call_args = mock_create_log.call_args
        self.assertEqual(call_args[1]["status"], PaymentLog.Status.PAYPAL_ORDER_CREATED)

    @patch(f"{PAYPAL_STRATEGY_BASE}._get_client")
    @patch(f"{PAYPAL_STRATEGY_BASE}._create_payment_log")
    def test_get_payment_context_order_creation_failed(self, mock_create_log, mock_get_client):
        transaction = self.create_test_transaction()

        mock_client = MagicMock()
        mock_response = self.create_mock_paypal_response(
            is_error=True, body="Order creation failed", status_code=400
        )
        mock_client.orders.create_order.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = PayPalStrategy.get_payment_context(transaction)

        self.assertIn("error", result)
        self.assertEqual(result["transaction"], transaction)

        self.assertEqual(mock_create_log.call_count, 1)

    @patch(f"{PAYPAL_STRATEGY_BASE}._get_client")
    def test_handle_success_gateway_not_found(self, mock_get_client):
        PaymentGateway.objects.filter(slug="paypal").delete()

        result_template, context = PayPalStrategy.handle_success("test_token")

        self.assertEqual(result_template, "payment_failed.html")
        self.assertIn("error", context)

        self.gateway = PaymentGateway.objects.create(
            name="PayPal",
            slug="paypal",
            merchant_id="test_client_id",
            secret_key="test_client_secret",
            is_active=True,
            is_sandbox=True,
        )

    @patch(f"{PAYPAL_STRATEGY_BASE}._capture_payment")
    @patch(f"{PAYPAL_STRATEGY_BASE}._get_transaction_from_order")
    @patch(f"{PAYPAL_STRATEGY_BASE}._fetch_paypal_order")
    @patch(f"{PAYPAL_STRATEGY_BASE}._get_client")
    def test_handle_success_fetch_error(
        self, mock_get_client, mock_fetch_order, mock_get_txn, mock_capture
    ):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_fetch_order.side_effect = PayPalOrderFetchError("Fetch failed")

        result_template, context = PayPalStrategy.handle_success("test_token")

        self.assertEqual(result_template, "payment_failed.html")
        self.assertEqual(context["error"], "Failed to retrieve order details")

    @patch(f"{PAYPAL_STRATEGY_BASE}._capture_payment")
    @patch(f"{PAYPAL_STRATEGY_BASE}._get_transaction_from_order")
    @patch(f"{PAYPAL_STRATEGY_BASE}._fetch_paypal_order")
    @patch(f"{PAYPAL_STRATEGY_BASE}._get_client")
    def test_handle_success_transaction_not_found(
        self, mock_get_client, mock_fetch_order, mock_get_txn, mock_capture
    ):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_order = self.create_mock_paypal_order()
        mock_fetch_order.return_value = mock_order
        mock_get_txn.side_effect = PayPalTransactionNotFoundError("Transaction not found")

        result_template, context = PayPalStrategy.handle_success("test_token")

        self.assertEqual(result_template, "payment_failed.html")
        self.assertEqual(context["error"], "No pending transaction found")

    @patch(f"{PAYPAL_STRATEGY_BASE}._capture_payment")
    @patch(f"{PAYPAL_STRATEGY_BASE}._get_transaction_from_order")
    @patch(f"{PAYPAL_STRATEGY_BASE}._fetch_paypal_order")
    @patch(f"{PAYPAL_STRATEGY_BASE}._get_client")
    def test_handle_success_capture_error(
        self, mock_get_client, mock_fetch_order, mock_get_txn, mock_capture
    ):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_order = self.create_mock_paypal_order()
        mock_fetch_order.return_value = mock_order
        mock_transaction = MagicMock()
        mock_get_txn.return_value = mock_transaction
        mock_capture.side_effect = PayPalCaptureError("Capture failed")

        result_template, context = PayPalStrategy.handle_success("test_token")

        self.assertEqual(result_template, "payment_failed.html")
        self.assertEqual(context["error"], "Payment capture failed")

    @patch(f"{PAYPAL_STRATEGY_BASE}._capture_payment")
    @patch(f"{PAYPAL_STRATEGY_BASE}._get_transaction_from_order")
    @patch(f"{PAYPAL_STRATEGY_BASE}._fetch_paypal_order")
    @patch(f"{PAYPAL_STRATEGY_BASE}._get_client")
    def test_handle_success_complete_flow(
        self, mock_get_client, mock_fetch_order, mock_get_txn, mock_capture
    ):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_order = self.create_mock_paypal_order()
        mock_fetch_order.return_value = mock_order
        mock_transaction = MagicMock()
        mock_get_txn.return_value = mock_transaction
        mock_capture.return_value = ("payment_success.html", {"success": True})

        result_template, context = PayPalStrategy.handle_success("test_token")

        self.assertEqual(result_template, "payment_success.html")
        self.assertEqual(context["success"], True)

    @patch(f"{PAYPAL_STRATEGY_BASE}._get_client")
    def test_handle_cancel_gateway_not_found(self, mock_get_client):
        PaymentGateway.objects.filter(slug="paypal").delete()

        result_template, context = PayPalStrategy.handle_cancel("test_token")

        self.assertEqual(result_template, "payment_failed.html")
        self.assertEqual(context["error"], "Payment was cancelled")

        self.gateway = PaymentGateway.objects.create(
            name="PayPal",
            slug="paypal",
            merchant_id="test_client_id",
            secret_key="test_client_secret",
            is_active=True,
            is_sandbox=True,
        )

    @patch(f"{PAYPAL_STRATEGY_BASE}._mark_transaction_failed")
    @patch(f"{PAYPAL_STRATEGY_BASE}._get_transaction_from_order")
    @patch(f"{PAYPAL_STRATEGY_BASE}._fetch_paypal_order")
    @patch(f"{PAYPAL_STRATEGY_BASE}._get_client")
    def test_handle_cancel_success(
        self, mock_get_client, mock_fetch_order, mock_get_txn, mock_mark_failed
    ):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_order = self.create_mock_paypal_order()
        mock_fetch_order.return_value = mock_order
        mock_transaction = MagicMock()
        mock_get_txn.return_value = mock_transaction

        result_template, context = PayPalStrategy.handle_cancel("test_token")

        self.assertEqual(result_template, "payment_failed.html")
        self.assertEqual(context["error"], "Payment was cancelled")
        self.assertEqual(context["transaction"], mock_transaction)
        mock_mark_failed.assert_called_once_with(
            mock_transaction, "test_token", mock_order, mock_order, reason="cancelled"
        )

    @patch(f"{PAYPAL_STRATEGY_BASE}._mark_transaction_failed")
    @patch(f"{PAYPAL_STRATEGY_BASE}._get_transaction_from_order")
    @patch(f"{PAYPAL_STRATEGY_BASE}._fetch_paypal_order")
    @patch(f"{PAYPAL_STRATEGY_BASE}._get_client")
    def test_handle_cancel_fetch_error(
        self, mock_get_client, mock_fetch_order, mock_get_txn, mock_mark_failed
    ):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_fetch_order.side_effect = PayPalOrderFetchError("Fetch failed")

        result_template, context = PayPalStrategy.handle_cancel("test_token")

        self.assertEqual(result_template, "payment_failed.html")
        self.assertEqual(context["error"], "Payment was cancelled")
        mock_mark_failed.assert_not_called()
