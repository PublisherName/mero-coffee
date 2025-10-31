from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label="Username or Email",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username or Email",
                "class": (
                    "w-full px-4 py-3 bg-slate-900/50 border border-slate-700 "
                    "rounded-lg text-white placeholder-slate-500 focus:outline-none "
                    "focus:border-red-500 focus:ring-2 focus:ring-red-500/50"
                    "transition-all duration-300"
                ),
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": (
                    "w-full px-4 py-3 bg-slate-900/50 border border-slate-700 "
                    "rounded-lg text-white placeholder-slate-500 focus:outline-none "
                    "focus:border-red-500 focus:ring-2 focus:ring-red-500/50"
                    "transition-all duration-300"
                ),
            }
        ),
    )


class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": (
                    "w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg "
                    "text-white placeholder-slate-500 focus:outline-none focus:border-red-500 "
                    "focus:ring-2 focus:ring-red-500/50 transition-all duration-300"
                ),
            }
        ),
        strip=False,
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm Password",
                "class": (
                    "w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg "
                    "text-white placeholder-slate-500 focus:outline-none focus:border-red-500 "
                    "focus:ring-2 focus:ring-red-500/50 transition-all duration-300"
                ),
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
                    "class": (
                        "w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg "
                        "text-white placeholder-slate-500 focus:outline-none focus:border-red-500 "
                        "focus:ring-2 focus:ring-red-500/50 transition-all duration-300"
                    ),
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "Email",
                    "class": (
                        "w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg "
                        "text-white placeholder-slate-500 focus:outline-none focus:border-red-500 "
                        "focus:ring-2 focus:ring-red-500/50 transition-all duration-300"
                    ),
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "placeholder": "First Name",
                    "class": (
                        "w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg "
                        "text-white placeholder-slate-500 focus:outline-none focus:border-red-500 "
                        "focus:ring-2 focus:ring-red-500/50 transition-all duration-300"
                    ),
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "placeholder": "Last Name",
                    "class": (
                        "w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg "
                        "text-white placeholder-slate-500 focus:outline-none focus:border-red-500 "
                        "focus:ring-2 focus:ring-red-500/50 transition-all duration-300"
                    ),
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

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False
        user.is_verified = False
        if commit:
            user.save()
        return user
