from django import forms
from django.conf import settings

from apps.payments.enums import WithdrawalStatus
from apps.payments.models import Withdrawal
from apps.payments.schemas import WithdrawalSchema
from root.forms.pydantic_mixins import PydanticValidationMixin


class WithdrawalForm(PydanticValidationMixin, forms.ModelForm):
    pydantic_schema = WithdrawalSchema

    class Meta:
        model = Withdrawal
        fields = ["amount", "payment_method", "account_details"]
        widgets = {
            "amount": forms.NumberInput(
                attrs={
                    "id": "amount",
                    "placeholder": "Enter amount",
                    "class": "w-full px-4 py-3 bg-page/50 border border-surface "
                    "rounded-lg text-white placeholder-subtle "
                    "focus:outline-none focus:border-accent",
                    "step": "1",
                }
            ),
            "payment_method": forms.Select(
                attrs={
                    "class": "w-full px-4 py-3 bg-page/50 border rounded-lg",
                }
            ),
            "account_details": forms.Textarea(
                attrs={
                    "rows": 4,
                    "id": "account_details",
                    "placeholder": "Enter your bank / eSewa / Khalti details",
                    "minlength": "10",
                    "maxlength": "255",
                }
            ),
        }

    def __init__(self, *args, creator_profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.creator_profile = creator_profile

        self._available_balance = None
        self._total_earnings = None
        self._min_withdrawal = getattr(settings, "MIN_WITHDRAWAL_AMOUNT")

        if self.creator_profile:
            self._available_balance = self.creator_profile.available_balance
            self._total_earnings = self.creator_profile.total_earnings

        self.fields["amount"].widget.attrs["min_value"] = str(self._min_withdrawal)
        self.fields["amount"].widget.attrs["max_value"] = str(self._available_balance)

    def _is_kyc_verified(self):
        if not self.creator_profile.can_receive_payment:
            raise forms.ValidationError(
                "KYC verification is required before requesting withdrawals. "
                "Please complete your KYC verification first."
            )

    def _has_pending_transaction(self):
        pending_count = self.creator_profile.withdrawals.filter(
            status=WithdrawalStatus.PENDING
        ).count()
        if pending_count > 0:
            raise forms.ValidationError(
                "You already have pending withdrawal request(s). Please wait for processing."
            )

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount > self._available_balance:
            raise forms.ValidationError(
                f"Amount exceeds available balance of NPR {self._available_balance}"
            )
        if amount < self._min_withdrawal:
            raise forms.ValidationError(f"Minimum withdrawal amount is NPR {self._min_withdrawal}")
        return amount

    def clean_account_details(self):
        account_details = self.cleaned_data.get("account_details")
        if not account_details:
            raise forms.ValidationError("Account details can not be empty")
        return account_details

    def clean(self):
        cleaned_data = super().clean()
        self._is_kyc_verified()
        self._has_pending_transaction()
        self.validate_with_pydantic()
        return cleaned_data

    def save(self):
        withdrawal = Withdrawal.objects.create(
            creator=self.creator_profile,
            amount=self.cleaned_data["amount"],
            account_details=self.cleaned_data["account_details"],
            payment_method=self.cleaned_data["payment_method"],
            status=WithdrawalStatus.PENDING,
        )
        return withdrawal
