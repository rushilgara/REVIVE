from sqlalchemy import Column, String, Float, BigInteger, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base, generate_uuid
from app.utils.timestamps import utc_now


class AgentDecision(Base):
    __tablename__ = "agent_decisions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    recovery_case_id = Column(String(36), ForeignKey("recovery_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    
    agent_name = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=False)  # 'openai', 'gemini', or 'deterministic_fallback'
    model_name = Column(String(100), nullable=True)
    
    proposed_action = Column(String(50), nullable=False)
    confidence_score = Column(Float, nullable=False)
    expected_recovery_minor = Column(BigInteger, default=0, nullable=False)
    reasoning_summary = Column(String(1000), nullable=False)
    raw_response = Column(JSON, default=dict, nullable=False)
    is_fallback = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    recovery_case = relationship("RecoveryCase", back_populates="decisions")
