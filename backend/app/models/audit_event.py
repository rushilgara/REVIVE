from sqlalchemy import Column, String, Enum, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base, generate_uuid
from app.utils.enums import AuditEventType, ActorType
from app.utils.timestamps import utc_now


class AuditEvent(Base):
    """
    Immutable audit log entry recording all state transitions, AI decisions, 
    policy enforcements, executions, and outcome verifications.
    """
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    correlation_id = Column(String(64), nullable=False, index=True)
    recovery_case_id = Column(String(36), ForeignKey("recovery_cases.id", ondelete="CASCADE"), nullable=True, index=True)
    
    event_type = Column(Enum(AuditEventType), nullable=False, index=True)
    actor = Column(Enum(ActorType), nullable=False)
    actor_id = Column(String(100), nullable=True)
    
    description = Column(String(500), nullable=False)
    metadata_payload = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    recovery_case = relationship("RecoveryCase", back_populates="audit_events")
