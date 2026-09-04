import pytest
from app.models.recovery_case import RecoveryCase
from app.models.policy import Policy
from app.models.customer import Customer
from app.utils.enums import RiskType, CaseStatus, InterventionType, StoppingReason
from app.engine.policy_engine import PolicyEngine
from app.engine.stopping_rules import StoppingRulesEngine
from app.engine.state_machine import RecoveryStateMachine
from app.engine.outcome_engine import OutcomeEngine
from app.core.exceptions import InvalidStateTransitionException


def test_hard_decline_permanent_stopping_rule():
    """Verify that hard bank declines trigger immediate permanent stop, never retried."""
    case = RecoveryCase(
        risk_type=RiskType.FAILED_PAYMENT,
        status=CaseStatus.READY_FOR_ACTION,
        revenue_at_risk_minor=499900,
        retry_count=0,
        contact_count=0,
        gateway_error_code="do_not_honor"
    )
    policy = Policy()
    customer = Customer(name="Cardholder", email="ch@example.com", is_opted_out=False)

    should_stop, reason, msg = StoppingRulesEngine.should_stop(case, policy, customer)
    assert should_stop is True
    assert reason == StoppingReason.HARD_FAILURE_PERMANENT


def test_contact_frequency_cap_stopping_rule():
    """Verify that exceeding customer contact limit blocks further messaging."""
    case = RecoveryCase(
        risk_type=RiskType.FAILED_PAYMENT,
        status=CaseStatus.READY_FOR_ACTION,
        revenue_at_risk_minor=499900,
        retry_count=0,
        contact_count=2
    )
    policy = Policy(max_contact_attempts=2)
    customer = Customer(name="Contacted", email="cont@example.com", is_opted_out=False)

    check = PolicyEngine.evaluate(case, InterventionType.PAYMENT_LINK, policy, customer)
    assert check.authorized is False
    assert check.blocked is True
    assert check.stopping_reason == StoppingReason.MAX_CONTACT_ATTEMPTS


def test_state_machine_pending_approval_transitions():
    """Verify operator approval and rejection state transitions."""
    case = RecoveryCase(
        risk_type=RiskType.FAILED_PAYMENT,
        status=CaseStatus.PENDING_APPROVAL,
        revenue_at_risk_minor=8700000
    )

    # Approved -> READY_FOR_ACTION
    RecoveryStateMachine.transition(case, CaseStatus.READY_FOR_ACTION)
    assert case.status == CaseStatus.READY_FOR_ACTION

    # Direct illegal transition back to OPEN must fail
    with pytest.raises(InvalidStateTransitionException):
        RecoveryStateMachine.transition(case, CaseStatus.OPEN)


def test_state_machine_rejection_transition():
    """Verify operator rejection transitions PENDING_APPROVAL directly to STOPPED."""
    case = RecoveryCase(
        risk_type=RiskType.FAILED_PAYMENT,
        status=CaseStatus.PENDING_APPROVAL,
        revenue_at_risk_minor=8700000
    )
    RecoveryStateMachine.transition(case, CaseStatus.STOPPED)
    assert case.status == CaseStatus.STOPPED

    # Terminal state: cannot transition out of STOPPED
    with pytest.raises(InvalidStateTransitionException):
        RecoveryStateMachine.transition(case, CaseStatus.READY_FOR_ACTION)


def test_verified_payment_outcome_records_correct_paise():
    """Verify that verified outcome updates case to RECOVERED with exact minor units."""
    case = RecoveryCase(
        risk_type=RiskType.FAILED_PAYMENT,
        status=CaseStatus.EXECUTING,
        revenue_at_risk_minor=499900,
        recovered_amount_minor=0
    )
    success, outcome, audit = OutcomeEngine.verify_payment_outcome(
        case=case,
        amount_minor=499900,
        confirmation_source="RAZORPAY_WEBHOOK",
        gateway_payment_id="pay_test_12345",
        metadata_payload={"method": "upi"},
        correlation_id="corr_test_001"
    )
    assert success is True
    assert case.status == CaseStatus.RECOVERED
    assert case.recovered_amount_minor == 499900
    assert outcome.amount_recovered_minor == 499900
    assert outcome.verified is True
