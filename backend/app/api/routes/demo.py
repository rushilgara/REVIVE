import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.session import get_db
from app.models.merchant import Merchant
from app.models.customer import Customer
from app.models.transaction import Transaction
from app.models.recovery_case import RecoveryCase
from app.utils.enums import RiskType, PaymentStatus, CaseStatus, InterventionType, AuditEventType, ActorType
from app.engine.recovery_engine import recovery_engine
from app.engine.state_machine import RecoveryStateMachine
from app.engine.outcome_engine import OutcomeEngine
from app.models.audit_event import AuditEvent
from app.models.intervention import Intervention
from app.services.customer_service import customer_service

router = APIRouter(prefix="/demo", tags=["Demo Mode"])


async def get_or_create_demo_merchant(db: AsyncSession) -> Merchant:
    stmt = select(Merchant).where(Merchant.email == "demo@acroretail.in")
    merchant = (await db.execute(stmt)).scalar_one_or_none()
    if not merchant:
        merchant = Merchant(
            id="demo_merchant_1",
            name="Acro Retail India",
            business_name="Acro Retail Pvt Ltd",
            email="demo@acroretail.in",
            default_currency="INR"
        )
        db.add(merchant)
        await db.flush()
    return merchant


@router.post("/case-a")
async def run_demo_case_a(db: AsyncSession = Depends(get_db)):
    """
    Demo Case A: ₹4,999 Standard Retail Transaction
    Workflow:
    Payment Failed -> Detect Risk (87/100) -> Diagnose (Temporary Failure)
    -> Recommend Payment Link -> Policy Check (Allowed) -> Execute Link
    -> Simulate Customer Payment -> Verify Payment -> State: RECOVERED.
    """
    merchant = await get_or_create_demo_merchant(db)
    corr_id = str(uuid.uuid4())

    customer = await customer_service.get_or_create_customer(
        db=db,
        merchant_id=merchant.id,
        name="Rohan Verma",
        email="rohan.verma@example.com",
        phone="+919876500001"
    )
    customer.recovery_profile = {
        "total_transactions": 4,
        "successful_recoveries": 2,
        "failure_count": 1,
        "preferred_channel": "payment_link"
    }
    await db.flush()

    # Create failed transaction
    tx = Transaction(
        merchant_id=merchant.id,
        customer_id=customer.id,
        amount_minor=499900,  # ₹4,999
        currency="INR",
        payment_method="card",
        status=PaymentStatus.FAILED,
        failure_code="BANK_GATEWAY_TIMEOUT",
        failure_reason="Issuer switch timed out during processing"
    )
    db.add(tx)
    await db.flush()

    # Detect & create case
    case = await recovery_engine.detect_and_create_case(
        db=db,
        merchant_id=merchant.id,
        customer=customer,
        risk_type=RiskType.FAILED_PAYMENT,
        revenue_at_risk_minor=499900,
        transaction=tx,
        correlation_id=corr_id
    )

    # Run workflow with simulated payment
    case, intervention = await recovery_engine.run_autonomous_workflow(
        db=db,
        case_id=case.id,
        correlation_id=corr_id,
        simulate_payment=True
    )

    return {
        "scenario": "Case A (₹4,999 Standard Payment Recovery)",
        "case_id": case.id,
        "amount_minor": case.revenue_at_risk_minor,
        "recoverability_score": case.recoverability_score,
        "status": case.status.value,
        "recovered": case.status == CaseStatus.RECOVERED,
        "recommended_action": case.recommended_action.value if case.recommended_action else None,
        "payment_link_url": intervention.payload.get("short_url") if intervention else None,
        "message": "Full recovery loop completed: Detected -> Diagnosed -> Executed -> Verified -> RECOVERED."
    }


@router.post("/case-b")
async def run_demo_case_b(db: AsyncSession = Depends(get_db)):
    """
    Demo Case B: ₹87,000 High-Value Enterprise Transaction
    Workflow:
    Payment Failed -> Detect Risk -> Recommend Recovery -> Policy Check
    -> Triggers Human Approval Requirement (> ₹50,000 threshold)
    -> State: PENDING_APPROVAL. Halts execution safely until merchant approves!
    """
    merchant = await get_or_create_demo_merchant(db)
    corr_id = str(uuid.uuid4())

    customer = await customer_service.get_or_create_customer(
        db=db,
        merchant_id=merchant.id,
        name="Vikramaditya Enterprises",
        email="procurement@vikramaditya.com",
        phone="+919876500002"
    )

    tx = Transaction(
        merchant_id=merchant.id,
        customer_id=customer.id,
        amount_minor=8700000,  # ₹87,000
        currency="INR",
        payment_method="netbanking",
        status=PaymentStatus.FAILED,
        failure_code="LIMIT_EXCEEDED",
        failure_reason="Corporate banking daily limit exceeded"
    )
    db.add(tx)
    await db.flush()

    case = await recovery_engine.detect_and_create_case(
        db=db,
        merchant_id=merchant.id,
        customer=customer,
        risk_type=RiskType.FAILED_PAYMENT,
        revenue_at_risk_minor=8700000,
        transaction=tx,
        correlation_id=corr_id
    )

    case, _ = await recovery_engine.run_autonomous_workflow(
        db=db,
        case_id=case.id,
        correlation_id=corr_id
    )

    return {
        "scenario": "Case B (₹87,000 High-Value Approval Guard)",
        "case_id": case.id,
        "amount_minor": case.revenue_at_risk_minor,
        "status": case.status.value,
        "pending_approval": case.status == CaseStatus.PENDING_APPROVAL,
        "message": "Safety policy enforced: Transaction exceeds approval threshold. Case queued in Approval Center."
    }


@router.post("/case-c")
async def run_demo_case_c(db: AsyncSession = Depends(get_db)):
    """
    Demo Case C: Executor Gateway Outage
    Workflow:
    Payment Failed -> AI recommends action -> Executor gateway fails / connection refused.
    REVIVE MUST NOT claim recovery.
    Outcome: Execution Failed -> Recovery NOT confirmed -> Case ESCALATED.
    """
    merchant = await get_or_create_demo_merchant(db)
    corr_id = str(uuid.uuid4())

    customer = await customer_service.get_or_create_customer(
        db=db,
        merchant_id=merchant.id,
        name="Ananya Sharma",
        email="ananya.sharma@example.com",
        phone="+919876500003"
    )

    tx = Transaction(
        merchant_id=merchant.id,
        customer_id=customer.id,
        amount_minor=1299900,  # ₹12,999
        currency="INR",
        payment_method="card",
        status=PaymentStatus.FAILED,
        failure_code="CARD_DECLINED",
        failure_reason="Card declined by issuing bank"
    )
    db.add(tx)
    await db.flush()

    case = await recovery_engine.detect_and_create_case(
        db=db,
        merchant_id=merchant.id,
        customer=customer,
        risk_type=RiskType.FAILED_PAYMENT,
        revenue_at_risk_minor=1299900,
        transaction=tx,
        correlation_id=corr_id
    )

    # Legally progress state machine: OPEN -> DIAGNOSING -> READY_FOR_ACTION
    RecoveryStateMachine.transition(case, CaseStatus.DIAGNOSING)
    case.root_cause = "Transient gateway reject"
    RecoveryStateMachine.transition(case, CaseStatus.READY_FOR_ACTION)
    await db.flush()

    # Execute with simulated executor failure
    intervention = await recovery_engine.execute_intervention(
        db=db,
        case=case,
        customer=customer,
        action=InterventionType.PAYMENT_LINK,
        correlation_id=corr_id,
        simulate_executor_failure=True
    )
    await db.commit()

    return {
        "scenario": "Case C (Executor Failure Safety Stop)",
        "case_id": case.id,
        "amount_minor": case.revenue_at_risk_minor,
        "status": case.status.value,
        "recovered": False,
        "execution_failed": True,
        "error_message": intervention.error_message,
        "message": "Safety proven: Gateway executor failed. Case escalated without falsely claiming recovery."
    }
