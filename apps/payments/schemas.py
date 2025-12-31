from pydantic import BaseModel, Field


class WithdrawalSchema(BaseModel):
    amount: int = Field(gt=0)
    payment_method: str
    account_details: str = Field(max_length=255, default="")
