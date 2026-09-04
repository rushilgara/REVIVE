from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.database.session import get_db
from app.models.recovery_case import RecoveryCase
from app.utils.enums import CaseStatus
from app.schemas.recovery import RecoveryCaseResponse
from app.engine.recovery_engine import recovery_engine

router = APIRouter(prefix="/approvals", tags=["Approval Center"])


@router.get("", response_model=List[RecoveryCaseResponse])
async def list_pending_approvals(db: AsyncSession = Depends(get_db)):
    """Lists all cases waiting in PENDING_APPROVAL state."""
    stmt = select(RecoveryCase).options(
        selectinload(RecoveryCase.customer),
        selectinload(RecoveryCase.transaction)
    ).where(
        RecoveryCase.status == CaseStatus.PENDING_APPROVAL
    ).order_by(desc(RecoveryCase.revenue_at_risk_minor))
    
    result = await db.execute(stmt)
    cases = result.scalars().all()
    return [RecoveryCaseResponse.model_validate(c) for c in cases]


@router.post("/{case_id}/approve")
async def approve_case_action(
    case_id: str,
    simulate_payment: bool = Query(True, description="Whether to simulate customer payment for demo flow"),
    db: AsyncSession = Depends(get_db)
):
    """
    Approves a high-value or restricted recovery case, audits the human approval,
    and dispatches the authorized intervention.
    """
    try:
        case = await recovery_engine.approve_case(
            db=db,
            case_id=case_id,
            user_id="merchant_operator_demo",
            simulate_payment=simulate_payment
        )
        return {
            "success": True,
            "case_id": case.id,
            "status": case.status.value,
            "message": "Action approved by operator and dispatched successfully.",
            "recovered": case.status == CaseStatus.RECOVERED
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{case_id}/reject")
async def reject_case_action(
    case_id: str,
    reason: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db)
):
    """
    Rejects a recovery case, auditing the decision and transitioning state to STOPPED.
    """
    try:
        case = await recovery_engine.reject_case(
            db=db,
            case_id=case_id,
            reason=reason,
            user_id="merchant_operator_demo"
        )
        return {
            "success": True,
            "case_id": case.id,
            "status": case.status.value,
            "message": "Case rejected and stopped by operator."
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
