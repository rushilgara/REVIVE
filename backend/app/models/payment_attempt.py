from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base, generate_uuid
from app.utils.timestamps import utc_now


class PaymentAttempt(Base):
    __tablename__ = "payment_attempts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    transaction_id = Column(String(36), ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    attempt_number = Column(Integer, nullable=False, default=1)
    gateway = Column(String(50), default="razorpay", nullable=False)
    status = Column(String(50), nullable=False)
    error_code = Column(String(100), nullable=True)
    error_description = Column(String(500), nullable=True)
    latency_ms = Column(Integer, nullable=True)
    gateway_payment_id = Column(String(100), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    transaction = relationship("Transaction", back_populates="attempts")
