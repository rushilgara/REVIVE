from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from app.database.base import Base, TimestampMixin, generate_uuid


class Merchant(Base, TimestampMixin):
    __tablename__ = "merchants"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    business_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    default_currency = Column(String(3), default="INR", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    customers = relationship("Customer", back_populates="merchant", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="merchant", cascade="all, delete-orphan")
    policies = relationship("Policy", back_populates="merchant", cascade="all, delete-orphan")
    recovery_cases = relationship("RecoveryCase", back_populates="merchant", cascade="all, delete-orphan")
