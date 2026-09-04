from sqlalchemy import Column, String, BigInteger, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base, generate_uuid
from app.utils.timestamps import utc_now


class RecoveryOutcome(Base):
    """
    Stores verified financial recovery outcomes.
    Revenue is NEVER counted as recovered unless verified is True through
    authenticated webhook or verified payment fetch.
    """
    __tablename__ = "recovery_outcomes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    recovery_case_id = Column(String(36), ForeignKey("recovery_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    
    verified = Column(Boolean, default=False, nullable=False, index=True)
    amount_recovered_minor = Column(BigInteger, default=0, nullable=False)
    confirmation_source = Column(String(100), nullable=False)  # 'RAZORPAY_WEBHOOK', 'PAYMENT_FETCH_VERIFIED', etc.
    gateway_payment_id = Column(String(100), nullable=True, index=True)
    verification_metadata = Column(JSON, default=dict, nullable=False)
    
    verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    recovery_case = relationship("RecoveryCase", back_populates="outcomes")
