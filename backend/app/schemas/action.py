from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.utils.enums import InterventionType


class ExecuteActionRequest(BaseModel):
    intervention_type: Optional[InterventionType] = None
    idempotency_key: Optional[str] = None
    override_reason: Optional[str] = None
    simulate_payment: bool = Field(default=False, description="Whether to simulate customer payment for demo/test flow")


class ActionExecutionResult(BaseModel):
    success: bool
    intervention_id: Optional[str] = None
    intervention_type: InterventionType
    status: str
    idempotency_key: str
    message: str
    payment_link_url: Optional[str] = None
    requires_approval: bool = False
    policy_blocked: bool = False
    stopping_rule_triggered: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
