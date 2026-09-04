import pytest
from app.models.recovery_case import RecoveryCase
from app.models.policy import Policy
from app.models.customer import Customer
from app.utils.enums import RiskType, CaseStatus, InterventionType, StoppingReason
from app.engine.policy_engine import PolicyEngine
from app.engine.stopping_rules import StoppingRulesEngine


def test_policy_approval_threshold_guard():
    # ₹87,000 exceeds default ₹50,000 threshold
    case = RecoveryCase(
        risk_type=RiskType.FAILED_PAYMENT,
        status=CaseStatus.READY_FOR_ACTION,
        revenue_at_risk_minor=8700000,
        retry_count=0,
        contact_count=0
    )
    policy = Policy(approval_threshold_minor=5000000)
    customer = Customer(name="Test", email="test@example.com", is_opted_out=False)

    check = PolicyEngine.evaluate(case, InterventionType.PAYMENT_LINK, policy, customer)
    assert check.authorized is False
    assert check.requires_approval is True
    assert check.stopping_reason == StoppingReason.HUMAN_ESCALATION_REQUIRED


def test_policy_retry_limit_guard():
    case = RecoveryCase(
        risk_type=RiskType.FAILED_PAYMENT,
        status=CaseStatus.READY_FOR_ACTION,
        revenue_at_risk_minor=499900,
        retry_count=3,
        contact_count=0
    )
    policy = Policy(max_retry_attempts=3)
    customer = Customer(name="Test", email="test@example.com", is_opted_out=False)

    check = PolicyEngine.evaluate(case, InterventionType.RETRY, policy, customer)
    assert check.authorized is False
    assert check.blocked is True
    assert check.stopping_reason == StoppingReason.MAX_RETRY_ATTEMPTS


def test_customer_opt_out_stopping_rule():
    case = RecoveryCase(
        risk_type=RiskType.FAILED_PAYMENT,
        status=CaseStatus.READY_FOR_ACTION,
        revenue_at_risk_minor=499900,
        retry_count=0,
        contact_count=0
    )
    policy = Policy()
    customer = Customer(name="Opted Out", email="optout@example.com", is_opted_out=True)

    should_stop, reason, msg = StoppingRulesEngine.should_stop(case, policy, customer)
    assert should_stop is True
    assert reason == StoppingReason.CUSTOMER_OPT_OUT
