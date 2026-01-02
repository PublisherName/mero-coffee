from django import forms
from django.conf import settings

from apps.creators.models import CreatorProfile
from apps.payments.models import PaymentGateway
from root.forms.pydantic_mixins import PydanticValidationMixin

from .schemas import BuyCoffeeSchema, CreatorProfileSchema


class CreatorProfileForm(PydanticValidationMixin, forms.ModelForm):
    pydantic_schema = CreatorProfileSchema

    email = forms.EmailField(
        required=False,
        disabled=True,
        widget=forms.EmailInput(
            attrs={
                "id": "email",
                "placeholder": "Your email address",
            }
        ),
    )

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
                }
            ),
        }

    def clean_display_name(self):
        display_name = self.cleaned_data.get("display_name")
        return display_name.strip().title() if display_name else display_name

    def clean_bio(self):
        bio = self.cleaned_data.get("bio")
        return bio.strip().capitalize() if bio else bio

    def clean_avatar_url(self):
        avatar_url = self.cleaned_data.get("avatar_url")
        return avatar_url.strip().lower() if avatar_url else avatar_url

    def clean_coffee_price(self):
        coffee_price = self.cleaned_data.get("coffee_price")
        if coffee_price is None or coffee_price < settings.MINIMUM_DONATION_AMOUNT:
            raise forms.ValidationError(
                f"Coffee price must be at least {settings.MINIMUM_DONATION_AMOUNT}"
            )
        return coffee_price

    def clean(self):
        cleaned_data = super().clean()
        self.validate_with_pydantic()
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        profile = kwargs.get("instance")
        if profile:
            self.min_amount = max(profile.coffee_price or 0, settings.MINIMUM_DONATION_AMOUNT)
            if profile.user:
                self.fields["email"].initial = profile.user.email

        self.fields["coffee_price"].widget.attrs["min_value"] = str(self.min_amount)
        self.fields["coffee_price"].widget.attrs["placeholder"] = str(self.min_amount)
        self.fields["coffee_price"].required = True
        self.fields["display_name"].required = True
        self.fields["bio"].required = True
        self.fields["avatar_url"].required = True


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
        self.min_amount = max(self.coffee_price, settings.MINIMUM_DONATION_AMOUNT)
        self.fields["amount"].widget.attrs["min"] = str(self.min_amount)
        self.fields["amount"].widget.attrs["placeholder"] = str(self.min_amount)

        if payment_gateway:
            self.fields["payment_provider"].choices = [
                (gateway.slug, gateway.name) for gateway in payment_gateway
            ]
        else:
            gateways = PaymentGateway.objects.filter(is_active=True)
            self.fields["payment_provider"].choices = [
                (gateway.slug, gateway.name) for gateway in gateways
            ]

    def clean_supporter_name(self):
        supporter_name = self.cleaned_data.get("supporter_name")
        return supporter_name.strip().title() if supporter_name else supporter_name

    def clean_message(self):
        message = self.cleaned_data.get("message")
        return message.strip().capitalize() if message else message

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount and amount < self.min_amount:
            raise forms.ValidationError(f"Amount must be at least Rs. {self.min_amount}")
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
