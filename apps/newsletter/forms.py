from django import forms
from pydantic import ValidationError as PydanticValidationError

from .models import NewsletterSubscriber
from .schemas import NewsletterSubscribeSchema


class NewsletterSubscribeForm(forms.ModelForm):
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

    def clean(self):
        cleaned_data = super().clean()
        try:
            NewsletterSubscribeSchema(**cleaned_data)
        except PydanticValidationError as e:
            for error in e.errors():
                field = error["loc"][0]
                self.add_error(field, error["msg"])
        return cleaned_data
