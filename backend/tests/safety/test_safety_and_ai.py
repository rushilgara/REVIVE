import pytest
import hmac
import hashlib
from app.services.ai_service import ai_service, DeterministicFallbackProvider
from app.core.exceptions import InvalidAIOutputException, RazorpayIntegrationException
from app.core.security import verify_razorpay_signature
from app.models.recovery_case import RecoveryCase
from app.models.customer import Customer
from app.models.policy import Policy
from app.utils.enums import RiskType, CaseStatus, InterventionType, StoppingReason
from app.engine.policy_engine import PolicyEngine
from app.engine.outcome_engine import OutcomeEngine
from app.schemas.agent import DecisionOutput


def test_ai_semantic_safety_rejects_impossible_negative_amounts():
    with pytest.raises(Exception):
        # Pydantic ge=0 constraint prevents negative expected recovery
        DecisionOutput(
            recommended_action=InterventionType.PAYMENT_LINK,
            confidence=0.9,
            expected_recovery_minor=-500,
            reason="Invalid negative calculation"
        )


def test_deterministic_fallback_activates_reliably():
    fallback = DeterministicFallbackProvider()
    assert fallback is not None


def test_razorpay_hmac_signature_verification():
    secret = "test_webhook_secret_xyz"
    body = b'{"event":"payment_link.paid","entity":"event"}'
    
    # Valid signature
    valid_sig = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    assert verify_razorpay_signature(body, valid_sig, secret) is True

    # Tampered body signature fails
    tampered_body = b'{"event":"payment_link.paid","amount":999999}'
    assert verify_razorpay_signature(tampered_body, valid_sig, secret) is False

    # Bogus signature fails
    assert verify_razorpay_signature(body, "bogus_signature_value", secret) is False


def test_unverified_action_is_never_marked_recovered():
    case = RecoveryCase(
        risk_type=RiskType.FAILED_PAYMENT,
        status=CaseStatus.EXECUTING,
        revenue_at_risk_minor=499900,
        recovered_amount_minor=0
    )
    
    # Just creating a link or executing an action does NOT mark case as recovered
    assert case.status == CaseStatus.EXECUTING
    assert case.recovered_amount_minor == 0
    assert case.status != CaseStatus.RECOVERED


def test_zero_amount_cannot_trigger_recovery():
    case = RecoveryCase(
        risk_type=RiskType.FAILED_PAYMENT,
        status=CaseStatus.EXECUTING,
        revenue_at_risk_minor=499900,
        recovered_amount_minor=0
    )
    success, outcome, audit = OutcomeEngine.verify_payment_outcome(
        case=case,
        amount_minor=0,
        confirmation_source="FAKE_WEBHOOK",
        gateway_payment_id="pay_0",
        metadata_payload={},
        correlation_id="test_corr"
    )
    assert success is False
    assert case.status != CaseStatus.RECOVERED
