from typing import Dict, Set
from app.utils.enums import CaseStatus
from app.core.exceptions import InvalidStateTransitionException
from app.core.logging import logger

LEGAL_TRANSITIONS: Dict[CaseStatus, Set[CaseStatus]] = {
    CaseStatus.OPEN: {
        CaseStatus.DIAGNOSING,
        CaseStatus.STOPPED,
        CaseStatus.FAILED,
    },
    CaseStatus.DIAGNOSING: {
        CaseStatus.READY_FOR_ACTION,
        CaseStatus.PENDING_APPROVAL,
        CaseStatus.STOPPED,
        CaseStatus.ESCALATED,
        CaseStatus.FAILED,
    },
    CaseStatus.READY_FOR_ACTION: {
        CaseStatus.EXECUTING,
        CaseStatus.PENDING_APPROVAL,
        CaseStatus.STOPPED,
        CaseStatus.ESCALATED,
        CaseStatus.FAILED,
    },
    CaseStatus.PENDING_APPROVAL: {
        CaseStatus.READY_FOR_ACTION, # When merchant approves
        CaseStatus.EXECUTING,        # Direct execution
        CaseStatus.STOPPED,          # When merchant rejects
        CaseStatus.ESCALATED,
        CaseStatus.FAILED,
    },
    CaseStatus.EXECUTING: {
        CaseStatus.RECOVERED,     # ONLY after authenticated outcome verification
        CaseStatus.READY_FOR_ACTION, # For next scheduled attempt if retryable
        CaseStatus.FAILED,
        CaseStatus.ESCALATED,
        CaseStatus.STOPPED,
    },
    CaseStatus.RECOVERED: set(),  # Terminal state: cannot be un-recovered
    CaseStatus.FAILED: {
        CaseStatus.ESCALATED,
    },
    CaseStatus.ESCALATED: {
        CaseStatus.READY_FOR_ACTION, # After human operator intervenes and resolves block
        CaseStatus.STOPPED,
    },
    CaseStatus.STOPPED: set(),    # Terminal state
    CaseStatus.EXPIRED: set(),    # Terminal state
}


class RecoveryStateMachine:
    """
    Deterministic state machine enforcing valid life-cycle transitions for RecoveryCase.
    Guarantees no arbitrary mutations or illegal skips.
    """

    @staticmethod
    def validate_transition(current_status: CaseStatus, next_status: CaseStatus) -> bool:
        if current_status == next_status:
            return True
            
        allowed = LEGAL_TRANSITIONS.get(current_status, set())
        if next_status not in allowed:
            logger.warning(
                f"State transition rejected: '{current_status.value}' -> '{next_status.value}'. "
                f"Allowed transitions: {[s.value for s in allowed]}"
            )
            raise InvalidStateTransitionException(current_status.value, next_status.value)
        return True

    @staticmethod
    def transition(case, next_status: CaseStatus):
        """Validates and applies the transition to the case model."""
        RecoveryStateMachine.validate_transition(case.status, next_status)
        case.status = next_status
