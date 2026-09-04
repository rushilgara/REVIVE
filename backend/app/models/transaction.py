from sqlalchemy import Column, String, BigInteger, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base, TimestampMixin, generate_uuid
from app.utils.enums import PaymentStatus


class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    merchant_id = Column(String(36), ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    external_transaction_id = Column(String(100), nullable=True, index=True)
    
    # Financial representation: STRICTLY integer minor units (paise)
    amount_minor = Column(BigInteger, nullable=False)
    currency = Column(String(3), default="INR", nullable=False)
    payment_method = Column(String(50), nullable=True)  # e.g., 'card', 'upi', 'netbanking'
    status = Column(Enum(PaymentStatus), default=PaymentStatus.CREATED, nullable=False, index=True)
    
    failure_code = Column(String(100), nullable=True)
    failure_reason = Column(String(500), nullable=True)

    merchant = relationship("Merchant", back_populates="transactions")
    customer = relationship("Customer", back_populates="transactions")
    attempts = relationship("PaymentAttempt", back_populates="transaction", cascade="all, delete-orphan")
    recovery_case = relationship("RecoveryCase", back_populates="transaction", uselist=False)
