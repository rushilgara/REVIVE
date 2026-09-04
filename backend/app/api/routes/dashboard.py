from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, case
from datetime import datetime, timezone, timedelta
from typing import Optional

from app.database.session import get_db
from app.models.recovery_case import RecoveryCase
from app.models.audit_event import AuditEvent
from app.models.intervention import Intervention
from app.utils.enums import CaseStatus
from app.schemas.dashboard import DashboardMetrics, TimeSeriesPoint, BreakdownItem

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    merchant_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Computes real, aggregated financial metrics and operational distributions 
    directly from stored database records.
    """
    # Base query filter
    case_filter = []
    if merchant_id:
        case_filter.append(RecoveryCase.merchant_id == merchant_id)

    # 1. Financial aggregates
    stmt_financial = select(
        func.coalesce(func.sum(RecoveryCase.revenue_at_risk_minor), 0),
        func.coalesce(func.sum(RecoveryCase.recovered_amount_minor), 0),
        func.count(RecoveryCase.id)
    ).where(*case_filter)
    res_fin = await db.execute(stmt_financial)
    risk_minor, recovered_minor, total_cases = res_fin.one()

    # 2. Status counts
    stmt_status = select(
        RecoveryCase.status,
        func.count(RecoveryCase.id)
    ).where(*case_filter).group_by(RecoveryCase.status)
    res_status = await db.execute(stmt_status)
    status_map = {row[0]: row[1] for row in res_status.all()}

    active_cases = (
        status_map.get(CaseStatus.OPEN, 0) +
        status_map.get(CaseStatus.DIAGNOSING, 0) +
        status_map.get(CaseStatus.READY_FOR_ACTION, 0) +
        status_map.get(CaseStatus.EXECUTING, 0)
    )
    pending_approval = status_map.get(CaseStatus.PENDING_APPROVAL, 0)
    recovered_cases = status_map.get(CaseStatus.RECOVERED, 0)
    failed_cases = status_map.get(CaseStatus.FAILED, 0)
    stopped_cases = status_map.get(CaseStatus.STOPPED, 0)
    escalated_cases = status_map.get(CaseStatus.ESCALATED, 0)

    recovery_rate = 0.0
    if risk_minor > 0:
        recovery_rate = round((recovered_minor / risk_minor) * 100, 2)

    # 3. Root Cause Breakdown
    stmt_causes = select(
        RecoveryCase.root_cause_category,
        func.count(RecoveryCase.id),
        func.sum(case((RecoveryCase.status == CaseStatus.RECOVERED, 1), else_=0)),
        func.coalesce(func.sum(RecoveryCase.recovered_amount_minor), 0)
    ).where(*case_filter).group_by(RecoveryCase.root_cause_category)
    res_causes = await db.execute(stmt_causes)
    root_cause_breakdown = [
        BreakdownItem(
            name=row[0].value if hasattr(row[0], "value") else str(row[0]),
            count=row[1],
            recovered_count=row[2],
            revenue_minor=row[3]
        ) for row in res_causes.all()
    ]

    # 4. Intervention Performance Breakdown
    stmt_interventions = select(
        Intervention.intervention_type,
        func.count(Intervention.id)
    ).group_by(Intervention.intervention_type)
    res_interventions = await db.execute(stmt_interventions)
    intervention_performance = [
        BreakdownItem(
            name=row[0].value if hasattr(row[0], "value") else str(row[0]),
            count=row[1],
            recovered_count=0,
            revenue_minor=0
        ) for row in res_interventions.all()
    ]

    # 5. Time series (last 7 days)
    now = datetime.now(timezone.utc)
    time_series = []
    for d in range(6, -1, -1):
        day_date = (now - timedelta(days=d)).date()
        date_str = day_date.strftime("%b %d")
        
        # Calculate daily aggregates
        day_start = datetime.combine(day_date, datetime.min.time(), tzinfo=timezone.utc)
        day_end = datetime.combine(day_date, datetime.max.time(), tzinfo=timezone.utc)
        
        stmt_day = select(
            func.coalesce(func.sum(RecoveryCase.revenue_at_risk_minor), 0),
            func.coalesce(func.sum(RecoveryCase.recovered_amount_minor), 0),
            func.count(RecoveryCase.id)
        ).where(
            RecoveryCase.created_at >= day_start,
            RecoveryCase.created_at <= day_end,
            *case_filter
        )
        res_day = await db.execute(stmt_day)
        day_risk, day_rec, day_count = res_day.one()
        time_series.append(TimeSeriesPoint(
            date=date_str,
            revenue_at_risk_minor=day_risk,
            revenue_recovered_minor=day_rec,
            cases_count=day_count
        ))

    # 6. Recent Audit Activity
    stmt_audit = select(AuditEvent).order_by(desc(AuditEvent.created_at)).limit(10)
    res_audit = await db.execute(stmt_audit)
    recent_activity = [
        {
            "id": a.id,
            "correlation_id": a.correlation_id,
            "case_id": a.recovery_case_id,
            "event_type": a.event_type.value,
            "actor": a.actor.value,
            "description": a.description,
            "created_at": a.created_at.isoformat()
        } for a in res_audit.scalars().all()
    ]

    return DashboardMetrics(
        revenue_at_risk_minor=risk_minor,
        revenue_recovered_minor=recovered_minor,
        recovery_rate_pct=recovery_rate,
        active_cases_count=active_cases,
        pending_approvals_count=pending_approval,
        recovered_cases_count=recovered_cases,
        failed_cases_count=failed_cases,
        stopped_cases_count=stopped_cases,
        escalated_cases_count=escalated_cases,
        recovery_timeline=time_series,
        intervention_performance=intervention_performance,
        root_cause_breakdown=root_cause_breakdown,
        recent_activity=recent_activity
    )
