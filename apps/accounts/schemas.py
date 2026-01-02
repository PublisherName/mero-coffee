from django.contrib.auth import get_user_model
from pydantic import BaseModel, EmailStr, Field, field_validator

User = get_user_model()


class LoginSchema(BaseModel):
    username: str = Field(min_length=1, max_length=150)
    password: str = Field(min_length=1)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, v):
        return v.lower() if v else v


class SignUpSchema(BaseModel):
    username: str = Field(min_length=1, max_length=150)
    email: EmailStr
    first_name: str = Field(min_length=1, max_length=150)
    last_name: str = Field(min_length=1, max_length=150)
    password1: str = Field(min_length=1)
    password2: str = Field(min_length=1)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError("Username must be at least 3 character long")
        return v.lower() if v else v

    @field_validator("password1")
    @classmethod
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v

    @field_validator("email")
    @classmethod
    def normalize_and_validate_email(cls, v):
        email_lower = v.lower() if v else v
        if User.objects.filter(email__iexact=email_lower).exists():
            raise ValueError("A user with that email already exists.")
        return email_lower

    @field_validator("first_name", "last_name")
    @classmethod
    def normalize_names(cls, v):
        return v.strip().title() if v else v


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

    @field_validator("full_name")
    @classmethod
    def normalize_full_name(cls, v):
        return v.strip().title() if v else v

    @field_validator("address")
    @classmethod
    def normalize_address(cls, v):
        if v:
            segments = [seg.strip().title() for seg in v.split(",")]
            return ", ".join(segments)
        return v

    @field_validator("id_number")
    @classmethod
    def normalize_id_number(cls, v):
        return v.strip().upper() if v else v


class ActivateEmailSchema(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def normalize_and_validate_email(cls, v):
        email_lower = v.lower() if v else v
        return email_lower
