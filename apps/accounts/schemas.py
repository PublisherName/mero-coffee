from django.contrib.auth import get_user_model
from pydantic import BaseModel, EmailStr, Field, field_validator

User = get_user_model()


class LoginSchema(BaseModel):
    username: str = Field(min_length=1, max_length=150)
    password: str = Field(min_length=1)


class SignUpSchema(BaseModel):
    username: str = Field(min_length=3, max_length=150)
    email: EmailStr
    first_name: str = Field(min_length=1, max_length=150)
    last_name: str = Field(min_length=1, max_length=150)
    password1: str = Field(min_length=8)
    password2: str = Field(min_length=8)

    @field_validator("password1")
    @classmethod
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v

    @field_validator("email")
    @classmethod
    def validate_email_is_unique(cls, v):
        if User.objects.filter(email=v).exists():
            raise ValueError("A user with that email already exists.")
        return v


class KYCSchema(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)
    phone: str = Field(min_length=10, max_length=20)
    address: str = Field(min_length=5, max_length=500)
    country: int
    region: int
    subregion: int
    city: int
    id_type: str
    id_number: str = Field(min_length=1, max_length=100)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if not v.replace("+", "").replace("-", "").replace(" ", "").isdigit():
            raise ValueError("Phone number must contain only digits, +, -, and spaces")
        return v
