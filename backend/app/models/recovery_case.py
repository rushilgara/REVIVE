from sqlalchemy import Column, String, BigInteger, Integer, Enum, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base, TimestampMixin, generate_uuid
from app.utils.enums import RiskType, CaseStatus, RootCauseCategory, InterventionType, StoppingReason


class RecoveryCase(Base, TimestampMixin):
    __tablename__ = "recovery_cases"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    merchant_id = Column(String(36), ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_id = Column(String(36), ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True, index=True)

    risk_type = Column(Enum(RiskType), nullable=False, index=True)
    status = Column(Enum(CaseStatus), default=CaseStatus.OPEN, nullable=False, index=True)
    
    # Financial state: STRICTLY integer minor units (paise)
    revenue_at_risk_minor = Column(BigInteger, nullable=False)
    recovered_amount_minor = Column(BigInteger, default=0, nullable=False)
    
    # AI Diagnosis & Explainable Recoverability
    recoverability_score = Column(Integer, default=0, nullable=False)
    recoverability_reasons = Column(JSON, default=list, nullable=False)
    root_cause = Column(String(500), nullable=True)
    root_cause_category = Column(Enum(RootCauseCategory), default=RootCauseCategory.UNKNOWN, nullable=False)
    recommended_action = Column(Enum(InterventionType), nullable=True)
    stopping_reason = Column(Enum(StoppingReason), nullable=True)
    
    # Bounded Execution Tracking
    retry_count = Column(Integer, default=0, nullable=False)
    contact_count = Column(Integer, default=0, nullable=False)
    last_action_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    merchant = relationship("Merchant", back_populates="recovery_cases")
    customer = relationship("Customer", back_populates="recovery_cases")
    transaction = relationship("Transaction", back_populates="recovery_case")
    interventions = relationship("Intervention", back_populates="recovery_case", cascade="all, delete-orphan")
    decisions = relationship("AgentDecision", back_populates="recovery_case", cascade="all, delete-orphan")
    outcomes = relationship("RecoveryOutcome", back_populates="recovery_case", cascade="all, delete-orphan")
    audit_events = relationship("AuditEvent", back_populates="recovery_case", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="recovery_case", cascade="all, delete-orphan")

    @property
    def gateway_error_code(self):
        if hasattr(self, "_gateway_error_code") and self._gateway_error_code is not None:
            return self._gateway_error_code
        if self.transaction and hasattr(self.transaction, "failure_code"):
            return self.transaction.failure_code
        return None

    @gateway_error_code.setter
    def gateway_error_code(self, value):
        self._gateway_error_code = value
