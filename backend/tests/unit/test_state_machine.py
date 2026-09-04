import pytest
from app.utils.enums import CaseStatus
from app.engine.state_machine import RecoveryStateMachine
from app.core.exceptions import InvalidStateTransitionException


def test_legal_state_transitions():
    assert RecoveryStateMachine.validate_transition(CaseStatus.OPEN, CaseStatus.DIAGNOSING) is True
    assert RecoveryStateMachine.validate_transition(CaseStatus.DIAGNOSING, CaseStatus.READY_FOR_ACTION) is True
    assert RecoveryStateMachine.validate_transition(CaseStatus.DIAGNOSING, CaseStatus.PENDING_APPROVAL) is True
    assert RecoveryStateMachine.validate_transition(CaseStatus.READY_FOR_ACTION, CaseStatus.EXECUTING) is True
    assert RecoveryStateMachine.validate_transition(CaseStatus.PENDING_APPROVAL, CaseStatus.EXECUTING) is True
    assert RecoveryStateMachine.validate_transition(CaseStatus.PENDING_APPROVAL, CaseStatus.STOPPED) is True
    assert RecoveryStateMachine.validate_transition(CaseStatus.EXECUTING, CaseStatus.RECOVERED) is True
    assert RecoveryStateMachine.validate_transition(CaseStatus.EXECUTING, CaseStatus.ESCALATED) is True


def test_illegal_state_transitions_rejected():
    # Terminal state cannot transition back to executing
    with pytest.raises(InvalidStateTransitionException):
        RecoveryStateMachine.validate_transition(CaseStatus.RECOVERED, CaseStatus.EXECUTING)

    # Stopped state cannot transition to executing
    with pytest.raises(InvalidStateTransitionException):
        RecoveryStateMachine.validate_transition(CaseStatus.STOPPED, CaseStatus.EXECUTING)

    # Cannot skip from OPEN directly to EXECUTING
    with pytest.raises(InvalidStateTransitionException):
        RecoveryStateMachine.validate_transition(CaseStatus.OPEN, CaseStatus.EXECUTING)

    # Cannot skip from OPEN directly to RECOVERED without diagnosis and execution
    with pytest.raises(InvalidStateTransitionException):
        RecoveryStateMachine.validate_transition(CaseStatus.OPEN, CaseStatus.RECOVERED)
