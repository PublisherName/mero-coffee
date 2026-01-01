from decimal import Decimal
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import KYC
from apps.creators.models import CreatorProfile
from apps.payments.models import SupportTransaction, Withdrawal

User = get_user_model()


class BasePaymentsTestCase(TestCase):
    user_password = "testpass123"

    def create_user(
        self, username="testuser", email="test@example.com", verified=True, role=User.Roles.CREATOR
    ):
        user = User.objects.create_user(
            username=username, email=email, password=self.user_password
        )
        user.role = role
        user.verified = verified
        user.save()
        if verified:
            KYC.objects.create(user=user, status="approved")
        return user

    def create_creator_profile(self, user=None, **kwargs):
        if user is None:
            user = self.create_user()
        profile, created = CreatorProfile.objects.by_username(
            username=user.username
        ).get_or_create()
        if not created:
            for key, value in kwargs.items():
                setattr(profile, key, value)
            profile.save()
        return profile

    @classmethod
    def create_support_transaction(
        cls, creator_profile, amount=Decimal("100"), payment_status="completed"
    ):
        txn = SupportTransaction.objects.create(
            creator=creator_profile,
            supporter_name="Test Supporter",
            amount=amount,
            message="Test message",
            payment_method="esewa",
            payment_status=payment_status,
            transaction_id=f"test_txn_{uuid4().hex[:8]}",
        )
        return txn

    @classmethod
    def create_withdrawal(
        cls, creator_profile, amount=Decimal("100"), status="pending", payment_method="bank"
    ):
        """Create test withdrawal with Decimal precision"""
        withdrawal = Withdrawal.objects.create(
            creator=creator_profile,
            amount=amount,
            payment_method=payment_method,
            account_details=f"Test {payment_method}: {uuid4().hex[:8]}",
            status=status,
        )
        if status == "processed":
            withdrawal.processed_at = timezone.now()
            withdrawal.save(update_fields=["processed_at"])
        return withdrawal
