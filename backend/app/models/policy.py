from sqlalchemy import Column, String, Integer, BigInteger, Boolean, ForeignKey
from sqlalchemy.orm import relationship, synonym
from app.database.base import Base, TimestampMixin, generate_uuid


class Policy(Base, TimestampMixin):
    __tablename__ = "policies"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    merchant_id = Column(String(36), ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Core Guardrails
    max_retry_attempts = Column(Integer, default=3, nullable=False)
    max_contact_attempts = Column(Integer, default=4, nullable=False)
    max_customer_contacts = synonym("max_contact_attempts")
    cooldown_hours = Column(Integer, default=12, nullable=False)
    approval_threshold_minor = Column(BigInteger, default=5000000, nullable=False)  # ₹50,000 in paise
    max_discount_minor = Column(BigInteger, default=0, nullable=False)
    max_recovery_attempts = Column(Integer, default=5, nullable=False)
    
    # Channel permissions
    allow_whatsapp = Column(Boolean, default=True, nullable=False)
    allow_sms = Column(Boolean, default=True, nullable=False)
    allow_email = Column(Boolean, default=True, nullable=False)
    allow_payment_links = Column(Boolean, default=True, nullable=False)
    auto_escalate_repeated_failures = Column(Boolean, default=True, nullable=False)

    merchant = relationship("Merchant", back_populates="policies")
