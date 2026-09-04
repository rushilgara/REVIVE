from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class SimulationRunRequest(BaseModel):
    scenario_preset: str = Field(default="all", description="'all', 'network_glitch', 'high_value', 'customer_issues', 'limits'")
    transaction_count: int = Field(default=1000, ge=50, le=10000, description="Number of transactions to simulate")
    random_seed: int = Field(default=42, description="Deterministic random seed")


class SimulationRunResponse(BaseModel):
    simulation_id: str
    scenario_preset: str
    transaction_count: int
    random_seed: int
    duration_ms: int
    total_cases_created: int
    recovered_cases: int
    pending_approval_cases: int
    stopped_cases: int
    escalated_cases: int
    revenue_at_risk_minor: int
    revenue_recovered_minor: int
    recovery_rate_pct: float
    scenarios_tested: List[str]
    summary_message: str
