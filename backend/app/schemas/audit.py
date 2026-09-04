from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.utils.enums import AuditEventType, ActorType


class AuditEventResponse(BaseModel):
    id: str
    correlation_id: str
    recovery_case_id: Optional[str] = None
    event_type: AuditEventType
    actor: ActorType
    actor_id: Optional[str] = None
    description: str
    metadata_payload: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
