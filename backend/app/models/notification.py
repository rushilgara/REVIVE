from sqlalchemy import Column, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base, generate_uuid
from app.utils.enums import NotificationChannel
from app.utils.timestamps import utc_now


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    recovery_case_id = Column(String(36), ForeignKey("recovery_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    channel = Column(Enum(NotificationChannel), nullable=False, index=True)
    recipient = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=True)
    body = Column(String(2000), nullable=False)
    status = Column(String(50), default="SENT", nullable=False)
    gateway_message_id = Column(String(100), nullable=True)
    
    sent_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    recovery_case = relationship("RecoveryCase", back_populates="notifications")
    customer = relationship("Customer")
