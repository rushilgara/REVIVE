from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.utils.enums import PaymentStatus


class TransactionBase(BaseModel):
    merchant_id: str
    customer_id: str
    amount_minor: int = Field(..., gt=0, description="Amount in minor units (paise)")
    currency: str = "INR"
    payment_method: Optional[str] = "card"
    external_transaction_id: Optional[str] = None
    failure_code: Optional[str] = None
    failure_reason: Optional[str] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    id: str
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
