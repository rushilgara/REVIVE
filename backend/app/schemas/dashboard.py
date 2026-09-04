from typing import List, Dict, Any
from pydantic import BaseModel


class TimeSeriesPoint(BaseModel):
    date: str
    revenue_at_risk_minor: int
    revenue_recovered_minor: int
    cases_count: int


class BreakdownItem(BaseModel):
    name: str
    count: int
    recovered_count: int
    revenue_minor: int


class DashboardMetrics(BaseModel):
    revenue_at_risk_minor: int
    revenue_recovered_minor: int
    recovery_rate_pct: float
    active_cases_count: int
    pending_approvals_count: int
    recovered_cases_count: int
    failed_cases_count: int
    stopped_cases_count: int
    escalated_cases_count: int
    
    # Visual breakdowns
    recovery_timeline: List[TimeSeriesPoint]
    intervention_performance: List[BreakdownItem]
    root_cause_breakdown: List[BreakdownItem]
    recent_activity: List[Dict[str, Any]]
