from pydantic import BaseModel, Field, HttpUrl, field_validator


class CreatorProfileSchema(BaseModel):
    display_name: str = Field(min_length=1, max_length=255)
    bio: str = Field(min_length=3, max_length=1000)
    avatar_url: HttpUrl | None = None
    coffee_price: int = Field(gt=0)


class BuyCoffeeSchema(BaseModel):
    amount: int = Field(gt=0)
    is_anonymous: bool = False
    supporter_name: str = Field(max_length=255, default="")
    message: str = Field(max_length=500, default="")
    payment_provider: str

    @field_validator("supporter_name")
    @classmethod
    def validate_supporter_name(cls, v, info):
        is_anonymous = info.data.get("is_anonymous", False)
        if not is_anonymous and not v.strip():
            raise ValueError("Name is required unless you choose to remain anonymous")
        return v
