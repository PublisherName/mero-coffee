from django import forms

from root.forms.pydantic_mixins import PydanticValidationMixin

from .models import NewsletterSubscriber
from .schemas import NewsletterSubscribeSchema


class NewsletterSubscribeForm(PydanticValidationMixin, forms.ModelForm):
    pydantic_schema = NewsletterSubscribeSchema

    class Meta:
        model = NewsletterSubscriber
        fields = ("email",)
        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "Enter your email",
                    "class": (
                        "flex-1 px-4 py-3 rounded-lg bg-page border border-surface "
                        "text-white placeholder-subtle focus:outline-none "
                        "focus:ring-2 focus:ring-surface/50 transition-all duration-300"
                        "focus:border-surface",
                    ),
                }
            ),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        return email.strip().lower() if email else email

    def clean(self):
        cleaned_data = super().clean()
        self.validate_with_pydantic()
        return cleaned_data
