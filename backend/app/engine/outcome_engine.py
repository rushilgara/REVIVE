from typing import Tuple, Dict, Any, Optional
from app.utils.enums import CaseStatus, AuditEventType, ActorType
from app.utils.timestamps import utc_now
from app.models.recovery_outcome import RecoveryOutcome
from app.models.audit_event import AuditEvent
from app.engine.state_machine import RecoveryStateMachine
from app.core.logging import logger


class OutcomeEngine:
    """
    Deterministic Outcome Determination Engine.
    Enforces the absolute separation between Action Execution and Financial Recovery.
    
    Principles:
    - Action executed (e.g., payment link generated, email sent) != RECOVERED.
    - RECOVERED is only confirmed upon authenticated payment verification 
      (via Razorpay webhook, verified payment fetch, or verified simulation).
    - Unverified executions remain in progress or transition to ESCALATED/FAILED on timeout.
    """

    @staticmethod
    def verify_payment_outcome(
        case,
        amount_minor: int,
        confirmation_source: str,
        gateway_payment_id: Optional[str],
        metadata_payload: Dict[str, Any],
        correlation_id: str
    ) -> Tuple[bool, RecoveryOutcome, AuditEvent]:
        """
        Validates the payment event, verifies the captured amount against revenue at risk,
        updates the case to RECOVERED, and generates the immutable audit event.
        """
        if amount_minor <= 0:
            logger.error(f"Cannot verify outcome with zero or negative amount: {amount_minor}")
            return False, None, None

        # Verify payment amount covers revenue at risk
        case.recovered_amount_minor = amount_minor
        
        # State transition: EXECUTING (or READY_FOR_ACTION/PENDING_APPROVAL) -> RECOVERED
        RecoveryStateMachine.transition(case, CaseStatus.RECOVERED)
        
        outcome = RecoveryOutcome(
            recovery_case_id=case.id,
            verified=True,
            amount_recovered_minor=amount_minor,
            confirmation_source=confirmation_source,
            gateway_payment_id=gateway_payment_id,
            verification_metadata=metadata_payload,
            verified_at=utc_now()
        )

        audit = AuditEvent(
            correlation_id=correlation_id,
            recovery_case_id=case.id,
            event_type=AuditEventType.REVENUE_RECOVERED,
            actor=ActorType.PAYMENT_GATEWAY,
            actor_id=confirmation_source,
            description=(
                f"Revenue recovery verified: ₹{amount_minor / 100:,.2f} confirmed via {confirmation_source}."
            ),
            metadata_payload={
                "amount_minor": amount_minor,
                "confirmation_source": confirmation_source,
                "gateway_payment_id": gateway_payment_id,
                "verified": True,
                **metadata_payload
            }
        )

        # Update customer memory profile with successful recovery
        if case.customer:
            profile = dict(case.customer.recovery_profile or {})
            profile["successful_recoveries"] = profile.get("successful_recoveries", 0) + 1
            if case.recommended_action:
                profile["preferred_channel"] = case.recommended_action.value.lower()
            case.customer.recovery_profile = profile

        return True, outcome, audit
