from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.utils.enums import RiskType, CaseStatus, RootCauseCategory, InterventionType, StoppingReason


class CustomerBrief(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    recovery_profile: Dict[str, Any] = Field(default_factory=dict)
    is_opted_out: bool = False

    model_config = ConfigDict(from_attributes=True)


class RecoveryCaseBase(BaseModel):
    merchant_id: str
    customer_id: str
    transaction_id: Optional[str] = None
    risk_type: RiskType
    revenue_at_risk_minor: int = Field(..., gt=0)


class RecoveryCaseCreate(RecoveryCaseBase):
    pass


class RecoveryCaseUpdate(BaseModel):
    status: Optional[CaseStatus] = None
    stopping_reason: Optional[StoppingReason] = None
    recommended_action: Optional[InterventionType] = None


class RecoveryCaseResponse(BaseModel):
    id: str
    merchant_id: str
    customer_id: str
    transaction_id: Optional[str] = None
    risk_type: RiskType
    status: CaseStatus
    revenue_at_risk_minor: int
    recovered_amount_minor: int
    recoverability_score: int
    recoverability_reasons: List[str]
    root_cause: Optional[str] = None
    root_cause_category: RootCauseCategory
    recommended_action: Optional[InterventionType] = None
    stopping_reason: Optional[StoppingReason] = None
    retry_count: int
    contact_count: int
    last_action_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Optional relationships
    customer: Optional[CustomerBrief] = None

    model_config = ConfigDict(from_attributes=True)


class RecoveryCaseDetailResponse(RecoveryCaseResponse):
    transaction: Optional[Dict[str, Any]] = None
    interventions: List[Dict[str, Any]] = Field(default_factory=list)
    decisions: List[Dict[str, Any]] = Field(default_factory=list)
    outcomes: List[Dict[str, Any]] = Field(default_factory=list)
    audit_events: List[Dict[str, Any]] = Field(default_factory=list)
    policy_authorization: Optional[Dict[str, Any]] = None
