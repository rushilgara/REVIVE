from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional

from app.database.session import get_db
from app.models.audit_event import AuditEvent
from app.schemas.audit import AuditEventResponse

router = APIRouter(prefix="/audit", tags=["Audit Trail"])


@router.get("", response_model=List[AuditEventResponse])
async def list_audit_events(
    case_id: Optional[str] = Query(None),
    correlation_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Queries the immutable audit ledger with case or correlation ID filtering."""
    query = select(AuditEvent).order_by(desc(AuditEvent.created_at))

    if case_id:
        query = query.where(AuditEvent.recovery_case_id == case_id)
    if correlation_id:
        query = query.where(AuditEvent.correlation_id == correlation_id)

    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    events = result.scalars().all()
    return [AuditEventResponse.model_validate(e) for e in events]
