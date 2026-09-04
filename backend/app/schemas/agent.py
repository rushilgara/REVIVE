from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from app.utils.enums import RootCauseCategory, InterventionType


class DiagnosisOutput(BaseModel):
    """Structured output schema for DiagnosisAgent."""
    root_cause: str = Field(..., description="Concise explanation of the payment or recovery failure")
    cause_category: RootCauseCategory = Field(..., description="Standardized root cause category")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    recoverability: int = Field(..., ge=0, le=100, description="Recoverability score from 0 to 100")
    reasoning_summary: str = Field(..., description="Brief factual summary of diagnostic reasoning")
    recommended_next_step: str = Field(..., description="Suggested next step")

    @field_validator("recoverability")
    @classmethod
    def validate_recoverability(cls, v):
        if not (0 <= v <= 100):
            raise ValueError("Recoverability must be an integer between 0 and 100")
        return v


class DecisionOutput(BaseModel):
    """Structured output schema for DecisionAgent."""
    recommended_action: InterventionType = Field(..., description="Recommended recovery intervention")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Decision confidence between 0.0 and 1.0")
    expected_recovery_minor: int = Field(..., ge=0, description="Expected recovery value in minor currency units (paise)")
    reason: str = Field(..., description="Factual justification for this action")
    alternative_actions: List[InterventionType] = Field(default_factory=list, description="Ranked viable alternative interventions")


class ExplanationSection(BaseModel):
    title: str
    headline: str
    details: str
    positive_factors: List[str] = Field(default_factory=list)
    risk_factors: List[str] = Field(default_factory=list)


class ExplanationOutput(BaseModel):
    """Structured human-readable explanation designed for merchant operators."""
    summary: str
    recoverability_explanation: ExplanationSection
    root_cause_explanation: ExplanationSection
    action_recommendation_explanation: ExplanationSection
