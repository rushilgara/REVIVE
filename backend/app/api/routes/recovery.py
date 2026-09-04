from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.database.session import get_db
from app.models.recovery_case import RecoveryCase
from app.models.customer import Customer
from app.models.transaction import Transaction
from app.models.policy import Policy
from app.utils.enums import CaseStatus, RiskType
from app.schemas.recovery import RecoveryCaseResponse, RecoveryCaseDetailResponse
from app.engine.recovery_engine import recovery_engine
from app.engine.policy_engine import PolicyEngine

router = APIRouter(prefix="/recovery", tags=["Recovery Cases"])


@router.get("/cases")
async def list_recovery_cases(
    status: Optional[CaseStatus] = Query(None),
    risk_type: Optional[RiskType] = Query(None),
    search: Optional[str] = Query(None),
    min_score: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Lists recovery cases with enterprise filtering, search, and pagination."""
    query = select(RecoveryCase).options(
        selectinload(RecoveryCase.customer)
    ).order_by(desc(RecoveryCase.created_at))

    if status:
        query = query.where(RecoveryCase.status == status)
    if risk_type:
        query = query.where(RecoveryCase.risk_type == risk_type)
    if min_score is not None:
        query = query.where(RecoveryCase.recoverability_score >= min_score)

    if search:
        search_pattern = f"%{search}%"
        query = query.join(RecoveryCase.customer).where(
            or_(
                RecoveryCase.id.ilike(search_pattern),
                Customer.name.ilike(search_pattern),
                Customer.email.ilike(search_pattern),
                RecoveryCase.transaction_id.ilike(search_pattern)
            )
        )

    # Get total count
    count_stmt = select(RecoveryCase.id)
    # Simple pagination
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    cases = result.scalars().all()

    return {
        "items": [RecoveryCaseResponse.model_validate(c) for c in cases],
        "limit": limit,
        "offset": offset
    }


@router.get("/cases/{case_id}", response_model=RecoveryCaseDetailResponse)
async def get_case_detail(case_id: str, db: AsyncSession = Depends(get_db)):
    """Fetches comprehensive case details, timeline, decisions, and audit history."""
    stmt = select(RecoveryCase).options(
        selectinload(RecoveryCase.customer),
        selectinload(RecoveryCase.transaction),
        selectinload(RecoveryCase.interventions),
        selectinload(RecoveryCase.decisions),
        selectinload(RecoveryCase.outcomes),
        selectinload(RecoveryCase.audit_events)
    ).where(RecoveryCase.id == case_id)
    result = await db.execute(stmt)
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(status_code=404, detail="Recovery case not found.")

    # Evaluate current policy status
    policy = await recovery_engine.get_or_create_policy(db, case.merchant_id)
    policy_check = None
    if case.recommended_action:
        check = PolicyEngine.evaluate(case, case.recommended_action, policy, case.customer)
        policy_check = {
            "authorized": check.authorized,
            "requires_approval": check.requires_approval,
            "blocked": check.blocked,
            "stopping_reason": check.stopping_reason.value if check.stopping_reason else None,
            "reason": check.reason
        }

    detail = RecoveryCaseDetailResponse.model_validate(case)
    if case.transaction:
        detail.transaction = {
            "id": case.transaction.id,
            "amount_minor": case.transaction.amount_minor,
            "currency": case.transaction.currency,
            "payment_method": case.transaction.payment_method,
            "failure_code": case.transaction.failure_code,
            "failure_reason": case.transaction.failure_reason,
            "created_at": case.transaction.created_at.isoformat()
        }
    detail.interventions = [
        {
            "id": i.id,
            "type": i.intervention_type.value,
            "status": i.status,
            "idempotency_key": i.idempotency_key,
            "payload": i.payload,
            "execution_result": i.execution_result,
            "error_message": i.error_message,
            "created_at": i.created_at.isoformat()
        } for i in case.interventions
    ]
    detail.decisions = [
        {
            "id": d.id,
            "agent_name": d.agent_name,
            "provider": d.provider,
            "proposed_action": d.proposed_action,
            "confidence_score": d.confidence_score,
            "expected_recovery_minor": d.expected_recovery_minor,
            "reasoning_summary": d.reasoning_summary,
            "is_fallback": d.is_fallback,
            "created_at": d.created_at.isoformat()
        } for d in case.decisions
    ]
    detail.outcomes = [
        {
            "id": o.id,
            "verified": o.verified,
            "amount_recovered_minor": o.amount_recovered_minor,
            "confirmation_source": o.confirmation_source,
            "gateway_payment_id": o.gateway_payment_id,
            "verified_at": o.verified_at.isoformat() if o.verified_at else None,
            "created_at": o.created_at.isoformat()
        } for o in case.outcomes
    ]
    detail.audit_events = [
        {
            "id": a.id,
            "correlation_id": a.correlation_id,
            "event_type": a.event_type.value,
            "actor": a.actor.value,
            "description": a.description,
            "metadata_payload": a.metadata_payload,
            "created_at": a.created_at.isoformat()
        } for a in case.audit_events
    ]
    detail.policy_authorization = policy_check
    return detail


@router.post("/cases/{case_id}/run")
async def run_recovery_flow(
    case_id: str,
    simulate_payment: bool = Query(False),
    db: AsyncSession = Depends(get_db)
):
    """Triggers the autonomous recovery pipeline for a specific case."""
    try:
        case, intervention = await recovery_engine.run_autonomous_workflow(
            db=db,
            case_id=case_id,
            simulate_payment=simulate_payment
        )
        return {
            "success": True,
            "case_id": case.id,
            "status": case.status.value,
            "intervention_dispatched": intervention is not None,
            "intervention_id": intervention.id if intervention else None,
            "recovered": case.status == CaseStatus.RECOVERED
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
