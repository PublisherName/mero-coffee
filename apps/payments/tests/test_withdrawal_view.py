from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse

from apps.payments.models import Withdrawal

from .base import BasePaymentsTestCase

User = get_user_model()


class WithdrawalViewTests(BasePaymentsTestCase):
    def setUp(self):
        self.creator_profile = self.create_creator_profile()
        self.create_support_transaction(self.creator_profile, amount=500)
        self.withdrawal_url = reverse("dashboard:withdrawal")
        self.client.force_login(self.creator_profile.user)

    def test_get_withdrawal_page(self):
        """Test GET request to withdrawal page"""
        response = self.client.get(self.withdrawal_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "withdrawal.html")

        self.assertIn("form", response.context)
        self.assertIn("withdrawals", response.context)
        self.assertIn("available_balance", response.context)
        self.assertIn("pending_balance", response.context)
        self.assertIn("withdrawn_balance", response.context)
        self.assertIn("min_withdrawal", response.context)

        self.assertEqual(response.context["available_balance"], 500)
        self.assertEqual(response.context["pending_balance"], 0)
        self.assertEqual(response.context["withdrawn_balance"], 0)
        self.assertEqual(response.context["min_withdrawal"], 100)

    def test_get_withdrawal_page_with_existing_withdrawals(self):
        """Test GET request shows existing withdrawals"""
        self.create_withdrawal(self.creator_profile, amount=100, status=Withdrawal.Status.PENDING)
        self.create_withdrawal(
            self.creator_profile, amount=200, status=Withdrawal.Status.PROCESSED
        )

        response = self.client.get(self.withdrawal_url)

        self.assertEqual(response.status_code, 200)
        withdrawals = response.context["withdrawals"]
        self.assertEqual(len(withdrawals), 2)

        self.assertEqual(response.context["available_balance"], 200)
        self.assertEqual(response.context["pending_balance"], 100)
        self.assertEqual(response.context["withdrawn_balance"], 200)

    def test_post_withdrawal_success(self):
        """Test successful withdrawal submission"""
        form_data = {
            "amount": 200,
            "payment_method": Withdrawal.Methods.BANK,
            "account_details": "Bank account: 1234567890",
        }

        response = self.client.post(self.withdrawal_url, data=form_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "withdrawal.html")
        self.assertContains(response, "Withdrawal request submitted successfully")

        withdrawal = Withdrawal.objects.get(creator=self.creator_profile)
        self.assertEqual(withdrawal.amount, 200)
        self.assertEqual(withdrawal.payment_method, Withdrawal.Methods.BANK)
        self.assertEqual(withdrawal.account_details, "Bank account: 1234567890")
        self.assertEqual(withdrawal.status, Withdrawal.Status.PENDING)

    def test_post_withdrawal_form_invalid(self):
        """Test withdrawal submission with invalid form data"""
        form_data = {
            "amount": 600,
            "payment_method": Withdrawal.Methods.BANK,
            "account_details": "Bank account: 1234567890",
        }

        response = self.client.post(self.withdrawal_url, data=form_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "withdrawal.html")
        self.assertContains(response, "Amount exceeds available balance of NPR")
        self.assertEqual(Withdrawal.objects.count(), 0)

    def test_post_withdrawal_kyc_not_verified(self):
        """Test withdrawal submission when KYC is not verified"""
        unverified_user = self.create_user("unverified", "unverified@test.com", verified=False)
        unverified_profile = self.create_creator_profile(unverified_user)
        self.create_support_transaction(unverified_profile, amount=500)

        self.client.force_login(unverified_user)

        form_data = {
            "amount": 200,
            "payment_method": Withdrawal.Methods.BANK,
            "account_details": "Bank account: 1234567890",
        }

        response = self.client.post(self.withdrawal_url, data=form_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "withdrawal.html")
        self.assertContains(
            response, "KYC verification is required before requesting withdrawals."
        )
        self.assertEqual(Withdrawal.objects.count(), 0)

    def test_post_withdrawal_pending_exists(self):
        """Test withdrawal submission when pending withdrawal exists"""
        self.create_withdrawal(self.creator_profile, amount=100, status="pending")

        form_data = {
            "amount": 200,
            "payment_method": Withdrawal.Methods.BANK,
            "account_details": "Bank account: 1234567890",
        }

        response = self.client.post(self.withdrawal_url, data=form_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "withdrawal.html")
        self.assertContains(response, "You already have pending withdrawal request(s).")
        self.assertEqual(Withdrawal.objects.count(), 1)

    def test_withdrawal_requires_creator_role(self):
        """Test withdrawal view requires creator role"""
        regular_user = self.create_user("regular", "regular@test.com", role=User.Roles.SUPPORTER)
        self.client.force_login(regular_user)

        response = self.client.get(self.withdrawal_url)

        self.assertEqual(response.status_code, 302)

    def test_withdrawal_requires_login(self):
        """Test withdrawal view requires login"""
        self.client.logout()

        response = self.client.get(self.withdrawal_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    @override_settings(MIN_WITHDRAWAL_AMOUNT=200)
    def test_withdrawal_uses_custom_min_withdrawal_setting(self):
        """Test withdrawal view uses custom minimum withdrawal amount"""
        response = self.client.get(self.withdrawal_url)

        self.assertEqual(response.context["min_withdrawal"], 200)

    def test_withdrawal_form_initialization_on_get(self):
        """Test withdrawal form is properly initialized on GET"""
        response = self.client.get(self.withdrawal_url)

        form = response.context["form"]
        self.assertIsInstance(form, type(form))
        self.assertEqual(form.creator_profile, self.creator_profile)

    def test_withdrawal_form_hidden_when_balance_below_minimum(self):
        """Test withdrawal form is hidden when available balance is below minimum"""
        low_balance_user = self.create_user("lowbalance", "lowbalance@test.com")
        low_balance_profile = self.create_creator_profile(low_balance_user)
        self.create_support_transaction(low_balance_profile, amount=50)
        self.client.force_login(low_balance_user)

        response = self.client.get(self.withdrawal_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "withdrawal.html")

        self.assertIn("form", response.context)
        self.assertEqual(response.context["available_balance"], 50)
        self.assertEqual(response.context["min_withdrawal"], 100)

        self.assertNotContains(response, '<form method="post" novalidate class="withdrawal-form">')
        self.assertContains(
            response, "You need a minimum balance of Rs. 100 to request a withdrawal."
        )

    def test_withdrawal_form_shown_when_balance_above_minimum(self):
        """Test withdrawal form is shown when available balance is above minimum"""
        response = self.client.get(self.withdrawal_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "withdrawal.html")

        self.assertContains(response, '<form method="post" novalidate class="withdrawal-form">')
        self.assertNotContains(response, "You need a minimum balance")
