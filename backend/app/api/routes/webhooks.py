import json
from fastapi import APIRouter, Request, Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.database.session import get_db
from app.models.recovery_case import RecoveryCase
from app.models.audit_event import AuditEvent
from app.utils.enums import AuditEventType, ActorType, CaseStatus
from app.services.razorpay_service import razorpay_service
from app.engine.outcome_engine import OutcomeEngine
from app.core.logging import logger

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

# In-memory deduplication set for processed webhook event IDs
PROCESSED_EVENT_IDS = set()


@router.post("/razorpay")
async def handle_razorpay_webhook(
    request: Request,
    x_razorpay_signature: Optional[str] = Header(None),
    x_razorpay_event_id: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticates and processes Razorpay webhook events.
    Enforces HMAC-SHA256 signature verification over raw request body bytes,
    deduplicates event IDs, and triggers verified financial outcome determination.
    """
    raw_body = await request.body()
    
    # 1. Signature Verification
    if not x_razorpay_signature:
        logger.warning("Webhook rejected: missing X-Razorpay-Signature header.")
        raise HTTPException(status_code=400, detail="Missing X-Razorpay-Signature header.")

    is_valid = razorpay_service.verify_webhook_signature(raw_body, x_razorpay_signature)
    if not is_valid:
        logger.warning("Webhook rejected: invalid HMAC signature.")
        raise HTTPException(status_code=401, detail="Invalid webhook signature.")

    # 2. Parse payload safely
    try:
        data = json.loads(raw_body.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Malformed JSON payload.")

    event_id = x_razorpay_event_id or data.get("event_id") or data.get("id")
    event_type = data.get("event", "unknown")
    logger.info(f"Authenticated Razorpay webhook received: event={event_type}, id={event_id}")

    # 3. Idempotency & Deduplication
    if event_id and event_id in PROCESSED_EVENT_IDS:
        logger.info(f"Duplicate webhook event ignored: {event_id}")
        return {"status": "ignored", "reason": "duplicate_event", "event_id": event_id}

    if event_id:
        PROCESSED_EVENT_IDS.add(event_id)

    # 4. Handle Payment Capture & Payment Link Events
    # Supported events: payment_link.paid, payment.captured
    if event_type in ("payment_link.paid", "payment.captured"):
        payload_entity = data.get("payload", {})
        payment_entity = payload_entity.get("payment", {}).get("entity", {})
        link_entity = payload_entity.get("payment_link", {}).get("entity", {})
        
        # Extract case ID from notes
        notes = payment_entity.get("notes", {}) or link_entity.get("notes", {})
        case_id = notes.get("recovery_case_id")
        
        amount_minor = payment_entity.get("amount") or link_entity.get("amount", 0)
        payment_id = payment_entity.get("id") or link_entity.get("id")

        if case_id:
            stmt = select(RecoveryCase).where(RecoveryCase.id == case_id)
            case = (await db.execute(stmt)).scalar_one_or_none()
            if case:
                # Outcome determination
                verified, outcome, audit = OutcomeEngine.verify_payment_outcome(
                    case=case,
                    amount_minor=amount_minor,
                    confirmation_source="RAZORPAY_WEBHOOK",
                    gateway_payment_id=payment_id,
                    metadata_payload={
                        "event_type": event_type,
                        "event_id": event_id,
                        "raw_event": data
                    },
                    correlation_id=f"wbk_{event_id or case_id[:8]}"
                )
                db.add(outcome)
                db.add(audit)
                await db.commit()
                logger.info(f"Case {case_id} marked RECOVERED via verified Razorpay webhook.")

    return {"status": "processed", "event": event_type, "event_id": event_id}
