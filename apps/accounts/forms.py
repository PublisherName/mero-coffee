from django import forms
from django.contrib.auth import get_user_model
from pydantic import ValidationError as PydanticValidationError

from .models import KYC
from .schemas import KYCSchema, LoginSchema, SignUpSchema

User = get_user_model()


class LoginForm(forms.Form):
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

    def clean(self):
        cleaned_data = super().clean()
        try:
            LoginSchema(**cleaned_data)
        except PydanticValidationError as e:
            for error in e.errors():
                field = error["loc"][0]
                self.add_error(field, error["msg"])
        return cleaned_data


class SignUpForm(forms.ModelForm):
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

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def clean(self):
        cleaned_data = super().clean()
        try:
            SignUpSchema(**cleaned_data)
        except PydanticValidationError as e:
            for error in e.errors():
                field = error["loc"][0]
                self.add_error(field, error["msg"])
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


class KYCForm(forms.ModelForm):
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
        self.fields["region"].label_from_instance = lambda obj: obj.name
        self.fields["subregion"].label_from_instance = lambda obj: obj.name
        self.fields["city"].label_from_instance = lambda obj: obj.name
        self.fields["front_image"].required = True
        self.fields["back_image"].required = True
        self.fields["selfie_with_document"].required = True

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

        try:
            KYCSchema(**data)
        except PydanticValidationError as e:
            for error in e.errors():
                field = error["loc"][0]
                self.add_error(field, error["msg"])
        return cleaned_data
