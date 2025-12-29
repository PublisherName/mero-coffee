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
                        "flex-1 px-4 py-3 rounded-lg bg-slate-900 border border-slate-700 "
                        "text-white placeholder-slate-500 focus:outline-none "
                        "focus:ring-2 focus:ring-slate-500/50 transition-all duration-300"
                        "focus:border-slate-500",
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
