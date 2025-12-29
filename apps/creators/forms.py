from django import forms

from apps.creators.models import CreatorProfile
from apps.payments.models import PaymentGateway
from root.forms.pydantic_mixins import PydanticValidationMixin

from .schemas import BuyCoffeeSchema, CreatorProfileSchema


class CreatorProfileForm(PydanticValidationMixin, forms.ModelForm):
    pydantic_schema = CreatorProfileSchema

    class Meta:
        model = CreatorProfile
        fields = ["display_name", "bio", "avatar_url", "coffee_price"]
        widgets = {
            "display_name": forms.TextInput(
                attrs={
                    "id": "display_name",
                    "placeholder": "Enter your display name",
                    "minlength": "3",
                    "maxlength": "255",
                }
            ),
            "bio": forms.Textarea(
                attrs={
                    "rows": 4,
                    "id": "bio",
                    "placeholder": "Write something about yourself",
                    "minlength": "3",
                    "maxlength": "255",
                }
            ),
            "avatar_url": forms.URLInput(
                attrs={
                    "id": "avatar_url",
                    "placeholder": "https://example.com/avatar.jpg",
                }
            ),
            "coffee_price": forms.NumberInput(
                attrs={
                    "id": "coffee_price",
                    "placeholder": "Enter coffee price in Rs.",
                    "min": "1",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        self.validate_with_pydantic()
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["display_name"].required = True
        self.fields["bio"].required = True
        self.fields["avatar_url"].required = True
        self.fields["coffee_price"].required = True


class BuyCoffeeForm(PydanticValidationMixin, forms.Form):
    pydantic_schema = BuyCoffeeSchema
    """Form for buying coffee for a creator"""

    amount = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                "class": (
                    "w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg "
                    "text-white placeholder-slate-500 focus:outline-none focus:border-red-500 "
                    "focus:ring-2 focus:ring-red-500/50 transition-all duration-300"
                ),
                "id": "custom_amount",
                "placeholder": "Enter custom amount",
                "min_value": "100",
            }
        ),
    )

    supporter_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": (
                    "w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg "
                    "text-white placeholder-slate-500 focus:outline-none focus:border-red-500 "
                    "focus:ring-2 focus:ring-red-500/50 transition-all duration-300"
                ),
                "id": "supporter_name",
                "placeholder": "Your name",
            }
        ),
    )

    is_anonymous = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "w-4 h-4 text-red-600 bg-slate-900"
                "border-slate-700 rounded focus:ring-red-500",
                "id": "is_anonymous",
            }
        ),
    )

    message = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "class": (
                    "w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg "
                    "text-white placeholder-slate-500 focus:outline-none focus:border-red-500 "
                    "focus:ring-2 focus:ring-red-500/50 transition-all duration-300 resize-none"
                ),
                "id": "message",
                "placeholder": "Write a supportive message...",
                "maxlength": "500",
            }
        ),
    )

    payment_provider = forms.ChoiceField(
        choices=[],
        widget=forms.RadioSelect(
            attrs={
                "class": "payment-provider-radio",
            }
        ),
    )

    def __init__(self, *args, creator=None, payment_gateway=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.creator = creator
        self.coffee_price = creator.coffee_price
        self.fields["amount"].widget.attrs["min_value"] = str(self.coffee_price)
        self.fields["amount"].widget.attrs["placeholder"] = str(self.coffee_price)

        if payment_gateway:
            self.fields["payment_provider"].choices = [
                (gateway.slug, gateway.name) for gateway in payment_gateway
            ]
        else:
            gateways = PaymentGateway.objects.filter(is_active=True)
            self.fields["payment_provider"].choices = [
                (gateway.slug, gateway.name) for gateway in gateways
            ]

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount and amount < self.coffee_price:
            raise forms.ValidationError(
                f"Amount must be at least Rs. {self.coffee_price} (creator's coffee price)"
            )
        return amount

    def clean(self):
        cleaned_data = super().clean()

        if self.creator and not self.creator.can_receive_payment:
            self.add_error(
                None, "This profile cannot receive support until KYC verification is completed."
            )

        schema_data = {**cleaned_data, "amount": cleaned_data.get("amount", self.coffee_price)}
        self.validate_with_pydantic(schema_data)

        is_anonymous = cleaned_data.get("is_anonymous")
        if is_anonymous:
            cleaned_data["supporter_name"] = "Anonymous Supporter"

        return cleaned_data
