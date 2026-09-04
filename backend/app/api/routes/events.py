import uuid
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, Optional

from app.database.session import get_db
from app.models.merchant import Merchant
from app.models.customer import Customer
from app.models.transaction import Transaction
from app.models.subscription import Subscription
from app.utils.enums import RiskType, PaymentStatus, AuditEventType, ActorType
from app.engine.recovery_engine import recovery_engine
from app.services.customer_service import customer_service

router = APIRouter(prefix="/events", tags=["Event Ingestion"])


@router.post("/payment")
async def ingest_payment_event(
    payload: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Ingests payment failure events, validates payload, normalizes risk,
    and initiates the autonomous recovery loop.
    """
    corr_id = payload.get("correlation_id") or str(uuid.uuid4())
    customer_email = payload.get("customer_email") or "buyer@example.com"
    customer_name = payload.get("customer_name") or "Retail Customer"
    amount_minor = payload.get("amount_minor", 499900)
    failure_code = payload.get("failure_code", "GATEWAY_TIMEOUT")
    failure_reason = payload.get("failure_reason", "Bank gateway did not respond in SLA window")

    stmt = select(Merchant)
    merchant = (await db.execute(stmt)).scalars().first()
    merchant_id = merchant.id if merchant else "merchant_default"

    # Identify or create customer
    customer = await customer_service.get_or_create_customer(
        db=db,
        merchant_id=merchant_id,
        name=customer_name,
        email=customer_email,
        phone=payload.get("customer_phone", "+919876543210")
    )

    # Persist transaction
    tx = Transaction(
        merchant_id=merchant_id,
        customer_id=customer.id,
        external_transaction_id=payload.get("external_transaction_id") or f"tx_{uuid.uuid4().hex[:10]}",
        amount_minor=amount_minor,
        currency="INR",
        payment_method=payload.get("payment_method", "card"),
        status=PaymentStatus.FAILED,
        failure_code=failure_code,
        failure_reason=failure_reason
    )
    db.add(tx)
    await db.flush()

    # Trigger recovery case detection
    case = await recovery_engine.detect_and_create_case(
        db=db,
        merchant_id=merchant_id,
        customer=customer,
        risk_type=RiskType.FAILED_PAYMENT,
        revenue_at_risk_minor=amount_minor,
        transaction=tx,
        correlation_id=corr_id
    )

    # Automatically progress workflow
    await recovery_engine.run_autonomous_workflow(
        db=db,
        case_id=case.id,
        correlation_id=corr_id,
        simulate_payment=payload.get("simulate_payment", False)
    )

    return {
        "success": True,
        "correlation_id": corr_id,
        "case_id": case.id,
        "status": case.status.value,
        "revenue_at_risk_minor": case.revenue_at_risk_minor,
        "recoverability_score": case.recoverability_score
    }


@router.post("/checkout")
async def ingest_checkout_event(
    payload: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """Ingests checkout abandonment events."""
    corr_id = payload.get("correlation_id") or str(uuid.uuid4())
    customer_email = payload.get("customer_email") or "cart_user@example.com"
    customer_name = payload.get("customer_name") or "Cart User"
    amount_minor = payload.get("amount_minor", 249900)

    stmt = select(Merchant)
    merchant = (await db.execute(stmt)).scalars().first()
    merchant_id = merchant.id if merchant else "merchant_default"

    customer = await customer_service.get_or_create_customer(
        db=db,
        merchant_id=merchant_id,
        name=customer_name,
        email=customer_email,
        phone=payload.get("customer_phone", "+919876543210")
    )

    case = await recovery_engine.detect_and_create_case(
        db=db,
        merchant_id=merchant_id,
        customer=customer,
        risk_type=RiskType.CHECKOUT_ABANDONMENT,
        revenue_at_risk_minor=amount_minor,
        transaction=None,
        correlation_id=corr_id
    )

    await recovery_engine.run_autonomous_workflow(
        db=db,
        case_id=case.id,
        correlation_id=corr_id
    )

    return {
        "success": True,
        "correlation_id": corr_id,
        "case_id": case.id,
        "status": case.status.value
    }


@router.post("/subscription")
async def ingest_subscription_event(
    payload: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """Ingests subscription mandate failure events."""
    corr_id = payload.get("correlation_id") or str(uuid.uuid4())
    customer_email = payload.get("customer_email") or "sub_user@example.com"
    customer_name = payload.get("customer_name") or "Subscriber"
    amount_minor = payload.get("amount_minor", 199900)

    stmt = select(Merchant)
    merchant = (await db.execute(stmt)).scalars().first()
    merchant_id = merchant.id if merchant else "merchant_default"

    customer = await customer_service.get_or_create_customer(
        db=db,
        merchant_id=merchant_id,
        name=customer_name,
        email=customer_email
    )

    case = await recovery_engine.detect_and_create_case(
        db=db,
        merchant_id=merchant_id,
        customer=customer,
        risk_type=RiskType.SUBSCRIPTION_FAILURE,
        revenue_at_risk_minor=amount_minor,
        transaction=None,
        correlation_id=corr_id
    )

    await recovery_engine.run_autonomous_workflow(
        db=db,
        case_id=case.id,
        correlation_id=corr_id
    )

    return {
        "success": True,
        "correlation_id": corr_id,
        "case_id": case.id,
        "status": case.status.value
    }


@router.post("/invoice")
async def ingest_invoice_event(
    payload: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """Ingests overdue commercial B2B receivable invoice events."""
    corr_id = payload.get("correlation_id") or str(uuid.uuid4())
    customer_email = payload.get("customer_email") or "finance@clientcorp.com"
    customer_name = payload.get("customer_name") or "Client Corp"
    amount_minor = payload.get("amount_minor", 4500000)

    stmt = select(Merchant)
    merchant = (await db.execute(stmt)).scalars().first()
    merchant_id = merchant.id if merchant else "merchant_default"

    customer = await customer_service.get_or_create_customer(
        db=db,
        merchant_id=merchant_id,
        name=customer_name,
        email=customer_email
    )

    case = await recovery_engine.detect_and_create_case(
        db=db,
        merchant_id=merchant_id,
        customer=customer,
        risk_type=RiskType.OVERDUE_RECEIVABLE,
        revenue_at_risk_minor=amount_minor,
        transaction=None,
        correlation_id=corr_id
    )

    await recovery_engine.run_autonomous_workflow(
        db=db,
        case_id=case.id,
        correlation_id=corr_id
    )

    return {
        "success": True,
        "correlation_id": corr_id,
        "case_id": case.id,
        "status": case.status.value
    }
