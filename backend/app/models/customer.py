from sqlalchemy import Column, String, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base, TimestampMixin, generate_uuid


class Customer(Base, TimestampMixin):
    __tablename__ = "customers"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    merchant_id = Column(String(36), ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True)
    external_id = Column(String(100), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    
    # Customer recovery profile & memory stored deterministically in DB
    recovery_profile = Column(JSON, default=dict, nullable=False)
    is_opted_out = Column(Boolean, default=False, nullable=False)

    merchant = relationship("Merchant", back_populates="customers")
    transactions = relationship("Transaction", back_populates="customer")
    recovery_cases = relationship("RecoveryCase", back_populates="customer")
