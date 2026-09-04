from sqlalchemy import Column, String, BigInteger, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base, TimestampMixin, generate_uuid


class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    merchant_id = Column(String(36), ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    external_subscription_id = Column(String(100), nullable=True, index=True)
    
    plan_name = Column(String(255), nullable=False)
    amount_minor = Column(BigInteger, nullable=False)
    billing_cycle = Column(String(50), default="monthly", nullable=False)
    status = Column(String(50), default="active", nullable=False, index=True)
    
    failed_cycles_count = Column(Integer, default=0, nullable=False)
    next_billing_at = Column(DateTime(timezone=True), nullable=True)

    merchant = relationship("Merchant")
    customer = relationship("Customer")
