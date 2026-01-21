from unittest.mock import MagicMock, patch

from apps.emails.models import EmailTemplate
from apps.payments.enums import PaymentLogStatus, PaymentMethods, SupportTransactionStatus
from apps.payments.models import PaymentGateway, PaymentLog, SupportTransaction
from apps.payments.services.stripe import StripeStrategy
from apps.payments.tests.base import BasePaymentsTestCase


class StripePaymentTestCase(BasePaymentsTestCase):
    def setUp(self):
        super().setUp()
        self.creator_profile = self.create_creator_profile()
        self.gateway = PaymentGateway.objects.create(
            name="Stripe",
            slug="stripe",
            secret_key="sk_test_123",
            is_active=True,
            is_sandbox=True,
        )

    @patch("apps.payments.services.stripe.stripe.checkout.Session.retrieve")
    @patch("apps.payments.services.stripe.stripe.PaymentIntent.retrieve")
    @patch("apps.emails.services.EmailService.send_template_email")
    def test_handle_success_sends_emails_to_creator_and_supporter(
        self, mock_send_email, mock_payment_intent, mock_session_retrieve
    ):
        """Test that handle_success sends emails to both creator and supporter"""
        transaction = SupportTransaction.objects.create(
            creator=self.creator_profile,
            supporter_name="Test Supporter",
            amount=100,
            message="Test message",
            payment_method=PaymentMethods.STRIPE,
            payment_status=SupportTransactionStatus.PENDING,
            transaction_id="test_txn_stripe_123",
        )

        mock_session = MagicMock()
        mock_session.id = "cs_test_123"
        mock_session.payment_status = "paid"
        mock_session.amount_total = 10000
        mock_session.metadata = {"transaction_id": transaction.transaction_id}
        mock_session.customer_details.email = "supporter@example.com"

        mock_payment_intent_instance = MagicMock()
        mock_payment_intent_instance.status = "succeeded"
        mock_payment_intent.return_value = mock_payment_intent_instance

        mock_session_retrieve.return_value = mock_session

        _result = StripeStrategy.handle_success("cs_test_123")

        transaction.refresh_from_db()
        self.assertEqual(transaction.payment_status, SupportTransactionStatus.COMPLETED)

        payment_log = PaymentLog.objects.filter(
            transaction=transaction,
            payment_method=PaymentMethods.STRIPE,
            status=PaymentLogStatus.COMPLETED,
        ).exists()
        self.assertTrue(payment_log)

        self.assertEqual(mock_send_email.call_count, 2)

        creator_call = None
        supporter_call = None
        for call in mock_send_email.call_args_list:
            _args, kwargs = call
            if kwargs.get("template_name") == EmailTemplate.Type.PAYMENT_SUCCESS_CREATOR:
                creator_call = call
            elif kwargs.get("template_name") == EmailTemplate.Type.PAYMENT_SUCCESS_SUPPORTER:
                supporter_call = call

        self.assertIsNotNone(creator_call)
        self.assertIsNotNone(supporter_call)

        _, creator_kwargs = creator_call
        self.assertEqual(creator_kwargs["recipient"], self.creator_profile.user.email)
        self.assertEqual(
            creator_kwargs["context"]["creator_name"],
            self.creator_profile.display_name or self.creator_profile.user.username,
        )
        self.assertEqual(creator_kwargs["context"]["supporter_name"], transaction.supporter_name)
        self.assertEqual(creator_kwargs["context"]["amount"], transaction.amount)

        _, supporter_kwargs = supporter_call
        self.assertEqual(supporter_kwargs["recipient"], "supporter@example.com")
        self.assertEqual(
            supporter_kwargs["context"]["creator_name"],
            self.creator_profile.display_name or self.creator_profile.user.username,
        )
        self.assertEqual(supporter_kwargs["context"]["amount"], transaction.amount)

    @patch("apps.payments.services.stripe.stripe.checkout.Session.retrieve")
    @patch("apps.payments.services.stripe.stripe.PaymentIntent.retrieve")
    @patch("apps.emails.services.EmailService.send_template_email")
    def test_handle_success_no_supporter_email_skips_supporter_email(
        self, mock_send_email, mock_payment_intent, mock_session_retrieve
    ):
        """Test that handle_success skips supporter email if no email provided"""
        transaction = SupportTransaction.objects.create(
            creator=self.creator_profile,
            supporter_name="Test Supporter",
            amount=100,
            message="Test message",
            payment_method=PaymentMethods.STRIPE,
            payment_status=SupportTransactionStatus.PENDING,
            transaction_id="test_txn_stripe_456",
        )

        mock_session = MagicMock()
        mock_session.id = "cs_test_123"
        mock_session.payment_status = "paid"
        mock_session.amount_total = 10000
        mock_session.metadata = {"transaction_id": transaction.transaction_id}
        mock_session.customer_details = None  # No email

        mock_payment_intent_instance = MagicMock()
        mock_payment_intent_instance.status = "succeeded"
        mock_payment_intent.return_value = mock_payment_intent_instance

        mock_session_retrieve.return_value = mock_session

        _result = StripeStrategy.handle_success("cs_test_123")

        self.assertEqual(mock_send_email.call_count, 1)

        _, kwargs = mock_send_email.call_args
        self.assertEqual(kwargs["template_name"], EmailTemplate.Type.PAYMENT_SUCCESS_CREATOR)
        self.assertEqual(kwargs["recipient"], self.creator_profile.user.email)
