from django import forms

from apps.creators.models import CreatorProfile
from apps.payments.models import PaymentGateway


class CreatorProfileForm(forms.ModelForm):
    class Meta:
        model = CreatorProfile
        fields = ["display_name", "bio", "avatar_url", "coffee_price"]
        widgets = {
            "display_name": forms.TextInput(
                attrs={
                    "id": "display_name",
                    "placeholder": "Enter your display name",
                }
            ),
            "bio": forms.Textarea(
                attrs={
                    "rows": 4,
                    "id": "bio",
                    "placeholder": "Write something about yourself",
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
                }
            ),
        }


class BuyCoffeeForm(forms.Form):
    """Form for buying coffee for a creator"""

    amount = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                "class": (
                    "w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg "
                    "text-white placeholder-slate-500 focus:outline-none focus:border-red-500 "
                    "focus:ring-2 focus:ring-red-500/50 transition-all duration-300"
                ),
                "id": "custom_amount",
                "placeholder": "Enter custom amount",
                "min": "1",
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

    def __init__(self, *args, coffee_price=100, **kwargs):
        super().__init__(*args, **kwargs)
        self.coffee_price = coffee_price
        self.fields["amount"].widget.attrs["min"] = str(coffee_price)
        self.fields["amount"].widget.attrs["placeholder"] = str(coffee_price)

        # Populate payment providers dynamically
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
        is_anonymous = cleaned_data.get("is_anonymous")
        supporter_name = cleaned_data.get("supporter_name")

        if is_anonymous:
            cleaned_data["supporter_name"] = "Anonymous Supporter"
        elif not supporter_name:
            self.add_error(
                "supporter_name", "Name is required unless you choose to remain anonymous"
            )

        return cleaned_data
