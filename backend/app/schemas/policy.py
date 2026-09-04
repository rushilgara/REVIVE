from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class PolicyBase(BaseModel):
    max_retry_attempts: int = Field(default=3, ge=1, le=10)
    max_contact_attempts: int = Field(default=4, ge=1, le=20)
    cooldown_hours: int = Field(default=12, ge=0, le=168)
    approval_threshold_minor: int = Field(default=5000000, ge=0, description="Amount in minor units (paise)")
    max_discount_minor: int = Field(default=0, ge=0)
    max_recovery_attempts: int = Field(default=5, ge=1, le=20)
    allow_whatsapp: bool = True
    allow_sms: bool = True
    allow_email: bool = True
    allow_payment_links: bool = True
    auto_escalate_repeated_failures: bool = True


class PolicyUpdate(BaseModel):
    max_retry_attempts: int = Field(default=3, ge=1, le=10)
    max_contact_attempts: int = Field(default=4, ge=1, le=20)
    cooldown_hours: int = Field(default=12, ge=0, le=168)
    approval_threshold_minor: int = Field(default=5000000, ge=0)
    max_discount_minor: int = Field(default=0, ge=0)
    max_recovery_attempts: int = Field(default=5, ge=1, le=20)
    allow_whatsapp: bool = True
    allow_sms: bool = True
    allow_email: bool = True
    allow_payment_links: bool = True
    auto_escalate_repeated_failures: bool = True


class PolicyResponse(PolicyBase):
    id: str
    merchant_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
