from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.session import get_db
from app.models.policy import Policy
from app.models.merchant import Merchant
from app.schemas.policy import PolicyResponse, PolicyUpdate
from app.engine.recovery_engine import recovery_engine

router = APIRouter(prefix="/policies", tags=["Policies"])


@router.get("", response_model=PolicyResponse)
async def get_merchant_policy(db: AsyncSession = Depends(get_db)):
    """Fetches the active merchant recovery policy guardrails."""
    # Default to first merchant or create default
    stmt = select(Merchant)
    merchant = (await db.execute(stmt)).scalars().first()
    merchant_id = merchant.id if merchant else "merchant_default"
    
    policy = await recovery_engine.get_or_create_policy(db, merchant_id)
    return PolicyResponse.model_validate(policy)


@router.put("", response_model=PolicyResponse)
async def update_merchant_policy(
    policy_update: PolicyUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Updates merchant policy guardrails directly in the database."""
    stmt = select(Merchant)
    merchant = (await db.execute(stmt)).scalars().first()
    merchant_id = merchant.id if merchant else "merchant_default"

    policy = await recovery_engine.get_or_create_policy(db, merchant_id)
    
    policy.max_retry_attempts = policy_update.max_retry_attempts
    policy.max_contact_attempts = policy_update.max_contact_attempts
    policy.cooldown_hours = policy_update.cooldown_hours
    policy.approval_threshold_minor = policy_update.approval_threshold_minor
    policy.max_discount_minor = policy_update.max_discount_minor
    policy.max_recovery_attempts = policy_update.max_recovery_attempts
    policy.allow_whatsapp = policy_update.allow_whatsapp
    policy.allow_sms = policy_update.allow_sms
    policy.allow_email = policy_update.allow_email
    policy.allow_payment_links = policy_update.allow_payment_links
    policy.auto_escalate_repeated_failures = policy_update.auto_escalate_repeated_failures

    await db.commit()
    await db.refresh(policy)
    return PolicyResponse.model_validate(policy)
