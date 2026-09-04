from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Dict, Any

from app.database.session import get_db
from app.models.recovery_case import RecoveryCase
from app.schemas.action import ExecuteActionRequest, ActionExecutionResult
from app.engine.recovery_engine import recovery_engine
from app.engine.outcome_engine import OutcomeEngine
from app.utils.enums import CaseStatus, InterventionType

router = APIRouter(prefix="/actions", tags=["Actions & Executions"])


@router.post("/{case_id}/execute", response_model=ActionExecutionResult)
async def execute_case_intervention(
    case_id: str,
    req: ExecuteActionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Executes an authorized intervention for a recovery case.
    Strictly validates idempotency, stopping rules, and policies.
    """
    stmt = select(RecoveryCase).options(
        selectinload(RecoveryCase.customer),
        selectinload(RecoveryCase.transaction)
    ).where(RecoveryCase.id == case_id)
    result = await db.execute(stmt)
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    action_to_run = req.intervention_type or case.recommended_action or InterventionType.PAYMENT_LINK

    try:
        intervention = await recovery_engine.execute_intervention(
            db=db,
            case=case,
            customer=case.customer,
            action=action_to_run,
            correlation_id=f"act_{case.id[:8]}",
            idempotency_key=req.idempotency_key,
            simulate_payment=req.simulate_payment
        )
        await db.commit()

        link_url = intervention.payload.get("short_url") if isinstance(intervention.payload, dict) else None

        return ActionExecutionResult(
            success=True,
            intervention_id=intervention.id,
            intervention_type=action_to_run,
            status=intervention.status,
            idempotency_key=intervention.idempotency_key,
            message=f"Intervention {action_to_run.value} executed successfully.",
            payment_link_url=link_url,
            details=intervention.payload or {}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{case_id}/simulate-payment")
async def simulate_customer_payment(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Simulates customer completing payment via payment link or external checkout.
    Triggers OutcomeEngine verification, transitioning case to RECOVERED.
    """
    stmt = select(RecoveryCase).options(
        selectinload(RecoveryCase.customer)
    ).where(RecoveryCase.id == case_id)
    case = (await db.execute(stmt)).scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    if case.status == CaseStatus.RECOVERED:
        return {"success": True, "message": "Case already recovered.", "amount_recovered_minor": case.recovered_amount_minor}

    verified, outcome, audit = OutcomeEngine.verify_payment_outcome(
        case=case,
        amount_minor=case.revenue_at_risk_minor,
        confirmation_source="SIMULATED_CUSTOMER_PAYMENT",
        gateway_payment_id=f"pay_sim_{case.id[:10]}",
        metadata_payload={"simulated_by": "operator_action"},
        correlation_id=f"sim_pay_{case.id[:8]}"
    )
    db.add(outcome)
    db.add(audit)
    await db.commit()

    return {
        "success": True,
        "status": case.status.value,
        "amount_recovered_minor": case.recovered_amount_minor,
        "confirmation_source": outcome.confirmation_source,
        "message": f"Payment of ₹{case.recovered_amount_minor / 100:,.2f} verified. Case marked RECOVERED."
    }
