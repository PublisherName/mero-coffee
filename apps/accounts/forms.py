from django import forms
from django.contrib.auth import get_user_model
from turnstile.fields import TurnstileField

from root.forms.pydantic_mixins import PydanticValidationMixin

from .models import KYC
from .schemas import KYCSchema, LoginSchema, SignUpSchema

User = get_user_model()


class LoginForm(PydanticValidationMixin, forms.Form):
    pydantic_schema = LoginSchema

    username = forms.CharField(
        max_length=150,
        label="Username or Email",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username or Email",
                "minlength": 1,
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "minlength": 1,
            }
        ),
    )
    turnstile = TurnstileField()

    def clean_username(self):
        username = self.cleaned_data.get("username")
        return username.lower() if username else username

    def clean(self):
        cleaned_data = super().clean()
        self.validate_with_pydantic()
        return cleaned_data


class SignUpForm(PydanticValidationMixin, forms.ModelForm):
    pydantic_schema = SignUpSchema
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "minlength": 8,
            }
        ),
        strip=False,
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm Password",
                "minlength": 8,
            }
        ),
        strip=False,
    )
    turnstile = TurnstileField()

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "placeholder": "Username",
                    "minlength": 3,
                    "maxlength": 150,
                },
            ),
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "Email",
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "placeholder": "First Name",
                    "minlength": 1,
                    "maxlength": 150,
                },
            ),
            "last_name": forms.TextInput(
                attrs={
                    "placeholder": "Last Name",
                    "minlength": 1,
                    "maxlength": 150,
                }
            ),
        }

    def clean_username(self):
        username = self.cleaned_data.get("username")
        return username.lower() if username else username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        return email.lower() if email else email

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        return first_name.strip().title() if first_name else first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        return last_name.strip().title() if last_name else last_name

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def clean(self):
        cleaned_data = super().clean()
        self.validate_with_pydantic()
        return cleaned_data

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


class KYCForm(PydanticValidationMixin, forms.ModelForm):
    pydantic_schema = KYCSchema

    email = forms.EmailField(
        disabled=True,
        required=False,
        widget=forms.EmailInput(
            attrs={
                "id": "email",
                "placeholder": "Your email address",
            }
        ),
    )

    class Meta:
        model = KYC
        fields = (
            "full_name",
            "phone",
            "address",
            "country",
            "region",
            "subregion",
            "city",
            "id_type",
            "id_number",
            "front_image",
            "back_image",
            "selfie_with_document",
        )
        widgets = {
            "full_name": forms.TextInput(
                attrs={"placeholder": "Full Name"},
            ),
            "phone": forms.TextInput(
                attrs={"placeholder": "Phone Number"},
            ),
            "address": forms.Textarea(
                attrs={"placeholder": "Address", "rows": 3},
            ),
            "country": forms.Select(
                attrs={"placeholder": "Select Country"},
            ),
            "region": forms.Select(
                attrs={"placeholder": "Select Region"},
            ),
            "subregion": forms.Select(
                attrs={"placeholder": "Select Sub Region"},
            ),
            "city": forms.Select(
                attrs={"placeholder": "Select City"},
            ),
            "id_number": forms.TextInput(
                attrs={"placeholder": "ID Number"},
            ),
            "front_image": forms.FileInput(
                attrs={"class": "hidden"},
            ),
            "back_image": forms.FileInput(
                attrs={"class": "hidden"},
            ),
            "selfie_with_document": forms.FileInput(
                attrs={"class": "hidden"},
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields["email"].initial = self.instance.user.email
        self.fields["region"].label_from_instance = lambda obj: obj.name
        self.fields["subregion"].label_from_instance = lambda obj: obj.name
        self.fields["city"].label_from_instance = lambda obj: obj.name
        self.fields["front_image"].required = True
        self.fields["back_image"].required = True
        self.fields["selfie_with_document"].required = True

    def clean_full_name(self):
        full_name = self.cleaned_data.get("full_name")
        return full_name.strip().title() if full_name else full_name

    def clean_address(self):
        address = self.cleaned_data.get("address")
        if address:
            segments = [seg.strip().title() for seg in address.split(",")]
            return ", ".join(segments)
        return address

    def clean_id_number(self):
        id_number = self.cleaned_data.get("id_number")
        return id_number.strip().upper() if id_number else id_number

    def clean(self):
        cleaned_data = super().clean()
        data = {}
        for k, v in cleaned_data.items():
            if k in ["front_image", "back_image", "selfie_with_document"]:
                continue

            if k in ["country", "region", "subregion", "city"] and v:
                data[k] = v.id
            else:
                data[k] = v

        self.validate_with_pydantic(data)
        return cleaned_data
