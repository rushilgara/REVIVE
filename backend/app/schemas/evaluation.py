from typing import List, Dict, Any
from pydantic import BaseModel


class StrategyMetrics(BaseModel):
    strategy_name: str
    total_cases: int
    revenue_at_risk_minor: int
    revenue_recovered_minor: int
    recovery_rate_pct: float
    total_retries: int
    total_customer_contacts: int
    total_interventions: int
    policy_violations: int
    unauthorized_attempts: int
    escalated_cases: int
    stopped_cases: int
    recovered_cases: int
    average_recovery_time_hours: float
    average_recovery_amount_minor: int


class EvaluationRunResponse(BaseModel):
    evaluation_id: str
    dataset_size: int
    random_seed: int
    revive: StrategyMetrics
    baseline: StrategyMetrics
    lift_recovered_revenue_pct: float
    contact_reduction_pct: float
    policy_compliance_improvement_pct: float
    key_findings: List[str]
