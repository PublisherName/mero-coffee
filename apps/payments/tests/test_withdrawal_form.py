from decimal import Decimal

from django.test import override_settings

from apps.payments.forms import WithdrawalForm
from apps.payments.models import Withdrawal

from .base import BasePaymentsTestCase


class WithdrawalFormTests(BasePaymentsTestCase):
    def setUp(self):
        self.creator_profile = self.create_creator_profile()
        self.create_support_transaction(self.creator_profile, amount=500)

    def test_form_initialization_with_creator_profile(self):
        """Test form initializes correctly with creator profile"""
        form = WithdrawalForm(creator_profile=self.creator_profile)

        self.assertEqual(form.creator_profile, self.creator_profile)
        self.assertEqual(form._available_balance, 500)
        self.assertEqual(form._total_earnings, 500)
        self.assertEqual(form._min_withdrawal, 100)

    def test_form_valid_data(self):
        """Test form accepts valid withdrawal data"""
        form_data = {
            "amount": 200,
            "payment_method": Withdrawal.Methods.BANK,
            "account_details": "Bank account: 1234567890",
        }
        form = WithdrawalForm(data=form_data, creator_profile=self.creator_profile)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["amount"], 200)
        self.assertEqual(form.cleaned_data["payment_method"], Withdrawal.Methods.BANK)
        self.assertEqual(form.cleaned_data["account_details"], "Bank account: 1234567890")

    def test_form_amount_exceeds_available_balance(self):
        """Test form rejects amount exceeding available balance"""
        form_data = {
            "amount": 600,
            "payment_method": Withdrawal.Methods.BANK,
            "account_details": "Bank account: 1234567890",
        }
        form = WithdrawalForm(data=form_data, creator_profile=self.creator_profile)

        self.assertFalse(form.is_valid())
        self.assertIn("amount", form.errors)
        self.assertIn("exceeds available balance", str(form.errors["amount"]))

    def test_form_amount_below_minimum(self):
        """Test form rejects amount below minimum withdrawal"""
        form_data = {
            "amount": 50,
            "payment_method": Withdrawal.Methods.BANK,
            "account_details": "Bank account: 1234567890",
        }
        form = WithdrawalForm(data=form_data, creator_profile=self.creator_profile)

        self.assertFalse(form.is_valid())
        self.assertIn("amount", form.errors)
        self.assertIn("Minimum withdrawal amount", str(form.errors["amount"]))

    def test_form_empty_account_details(self):
        """Test form rejects empty account details"""
        form_data = {
            "amount": 200,
            "payment_method": Withdrawal.Methods.BANK,
            "account_details": "",
        }
        form = WithdrawalForm(data=form_data, creator_profile=self.creator_profile)

        self.assertFalse(form.is_valid())
        self.assertIn("account_details", form.errors)
        self.assertIn("can not be empty", str(form.errors["account_details"]))

    def test_form_kyc_not_verified(self):
        """Test form rejects withdrawal when KYC is not verified"""
        unverified_user = self.create_user("unverified", "unverified@test.com", is_verified=False)
        unverified_profile = self.create_creator_profile(unverified_user)
        self.create_support_transaction(unverified_profile, amount=500)

        form_data = {
            "amount": 200,
            "payment_method": Withdrawal.Methods.BANK,
            "account_details": "Bank account: 1234567890",
        }
        form = WithdrawalForm(data=form_data, creator_profile=unverified_profile)

        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)
        self.assertIn("KYC verification is required", str(form.errors["__all__"]))

    def test_form_pending_withdrawal_exists(self):
        """Test form blocks new withdrawal when pending withdrawal exists"""
        self.create_withdrawal(self.creator_profile, amount=100, status="pending")

        form_data = {
            "amount": 200,
            "payment_method": Withdrawal.Methods.BANK,
            "account_details": "Bank account: 1234567890",
        }
        form = WithdrawalForm(data=form_data, creator_profile=self.creator_profile)

        self.assertFalse(form.is_valid())
        self.assertIn("pending", form.errors["__all__"][0].lower())

    def test_form_save_creates_withdrawal(self):
        """Test form save method creates withdrawal instance"""
        form_data = {
            "amount": 200,
            "payment_method": Withdrawal.Methods.ESEWA,
            "account_details": "eSewa ID: 1234567890",
        }
        form = WithdrawalForm(data=form_data, creator_profile=self.creator_profile)
        self.assertTrue(form.is_valid())

        withdrawal = form.save()

        self.assertIsInstance(withdrawal, Withdrawal)
        self.assertEqual(withdrawal.creator, self.creator_profile)
        self.assertEqual(withdrawal.amount, 200)
        self.assertEqual(withdrawal.payment_method, Withdrawal.Methods.ESEWA)
        self.assertEqual(withdrawal.account_details, "eSewa ID: 1234567890")
        self.assertEqual(withdrawal.status, Withdrawal.Status.PENDING)

    @override_settings(MIN_WITHDRAWAL_AMOUNT=200)
    def test_form_uses_custom_min_withdrawal_setting(self):
        """Test form uses custom minimum withdrawal amount from settings"""
        form = WithdrawalForm(creator_profile=self.creator_profile)
        self.assertEqual(form._min_withdrawal, 200)

        form_data = {
            "amount": 150,
            "payment_method": Withdrawal.Methods.BANK,
            "account_details": "Bank account: 1234567890",
        }
        form = WithdrawalForm(data=form_data, creator_profile=self.creator_profile)

        self.assertFalse(form.is_valid())
        self.assertIn("amount", form.errors)

    def test_form_with_pending_and_processed_withdrawals(self):
        """Test available balance calculation with pending and processed withdrawals"""

        self.create_withdrawal(
            self.creator_profile, amount=Decimal("100"), status=Withdrawal.Status.PENDING
        )
        self.create_withdrawal(
            self.creator_profile, amount=Decimal("200"), status=Withdrawal.Status.PROCESSED
        )

        form = WithdrawalForm(creator_profile=self.creator_profile)
        self.assertEqual(form._available_balance, Decimal("200"))  # 500 - 100 -200

        form_data = {
            "amount": "200",
            "payment_method": Withdrawal.Methods.BANK,
            "account_details": "Bank account: 1234567890",
        }
        form = WithdrawalForm(data=form_data, creator_profile=self.creator_profile)
        # Form is invalid as there is a pending transaction
        self.assertFalse(form.is_valid())
