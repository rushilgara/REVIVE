from sqlalchemy import Column, String, Enum, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base, TimestampMixin, generate_uuid
from app.utils.enums import InterventionType


class Intervention(Base, TimestampMixin):
    __tablename__ = "interventions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    recovery_case_id = Column(String(36), ForeignKey("recovery_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    intervention_type = Column(Enum(InterventionType), nullable=False, index=True)
    status = Column(String(50), default="DISPATCHED", nullable=False, index=True)
    
    # Idempotency constraint ensures no duplicate execution
    idempotency_key = Column(String(100), unique=True, nullable=False, index=True)
    channel = Column(String(50), nullable=True)
    payload = Column(JSON, default=dict, nullable=False)
    execution_result = Column(JSON, default=dict, nullable=False)
    error_message = Column(String(500), nullable=True)
    
    dispatched_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    recovery_case = relationship("RecoveryCase", back_populates="interventions")
