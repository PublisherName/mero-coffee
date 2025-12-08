from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .models import KYC

User = get_user_model()


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label="Username or Email",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username or Email",
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
            }
        ),
    )


class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
            }
        ),
        strip=False,
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm Password",
            }
        ),
        strip=False,
    )

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "placeholder": "Username",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "Email",
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "placeholder": "First Name",
                },
            ),
            "last_name": forms.TextInput(
                attrs={
                    "placeholder": "Last Name",
                }
            ),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("The two password fields didn’t match.")
        return password2

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with that email already exists.")
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["username"].help_text = ""

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False
        user.is_verified = False
        if commit:
            user.save()
        return user


class KYCForm(forms.ModelForm):
    class Meta:
        model = KYC
        fields = ("full_name", "phone", "address", "city", "country", "id_type", "id_number")
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Full Name"}),
            "phone": forms.TextInput(attrs={"placeholder": "Phone Number"}),
            "address": forms.Textarea(attrs={"placeholder": "Address", "rows": 3}),
            "city": forms.TextInput(attrs={"placeholder": "City"}),
            "country": forms.TextInput(attrs={"placeholder": "Country"}),
            "id_type": forms.TextInput(attrs={"placeholder": "ID Type (e.g., Passport, License)"}),
            "id_number": forms.TextInput(attrs={"placeholder": "ID Number"}),
        }
