from django import forms

from apps.creators.models import CreatorProfile


class CreatorProfileForm(forms.ModelForm):
    class Meta:
        model = CreatorProfile
        fields = ["display_name", "bio", "avatar_url", "coffee_price"]
        widgets = {
            "display_name": forms.TextInput(
                attrs={
                    "class": (
                        "w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg "
                        "text-white placeholder-slate-500 focus:outline-none focus:border-red-500 "
                        "focus:ring-2 focus:ring-red-500/50 transition-all duration-300"
                    ),
                    "id": "display_name",
                    "placeholder": "Enter your display name",
                }
            ),
            "bio": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": (
                        "w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg"
                        "text-white placeholder-slate-500 focus:outline-none focus:border-red-500"
                        "focus:ring-2 focus:ring-red-500/50 transition-all duration-300"
                        "resize-none"
                    ),
                    "id": "bio",
                    "placeholder": "Write something about yourself",
                }
            ),
            "avatar_url": forms.URLInput(
                attrs={
                    "class": (
                        "w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg "
                        "text-white placeholder-slate-500 focus:outline-none focus:border-red-500 "
                        "focus:ring-2 focus:ring-red-500/50 transition-all duration-300"
                    ),
                    "id": "avatar_url",
                    "placeholder": "https://example.com/avatar.jpg",
                }
            ),
            "coffee_price": forms.NumberInput(
                attrs={
                    "class": (
                        "w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg "
                        "text-white placeholder-slate-500 focus:outline-none focus:border-red-500 "
                        "focus:ring-2 focus:ring-red-500/50 transition-all duration-300"
                    ),
                    "id": "coffee_price",
                    "placeholder": "Enter coffee price in Rs.",
                }
            ),
        }
