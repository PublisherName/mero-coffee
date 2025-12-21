from pydantic import BaseModel, EmailStr


class NewsletterSubscribeSchema(BaseModel):
    email: EmailStr
