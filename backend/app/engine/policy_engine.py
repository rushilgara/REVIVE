from typing import Optional, NamedTuple
from datetime import datetime, timezone, timedelta
from app.utils.enums import InterventionType, StoppingReason
from app.utils.timestamps import utc_now
from app.engine.stopping_rules import StoppingRulesEngine


class PolicyCheckResult(NamedTuple):
    authorized: bool
    requires_approval: bool
    blocked: bool
    stopping_reason: Optional[StoppingReason]
    reason: str


class PolicyEngine:
    """
    Deterministic policy enforcement engine.
    Merchant policies strictly authorize, block, or route actions to human approval.
    AI recommendations can NEVER bypass this engine.
    """

    @staticmethod
    def evaluate(
        case,
        proposed_action: InterventionType,
        policy,
        customer,
        is_manual_approval: bool = False
    ) -> PolicyCheckResult:
        # 1. Terminal / hard bank decline is absolute
        is_hard, decline_code = StoppingRulesEngine.is_hard_decline(case)
        if is_hard:
            return PolicyCheckResult(
                authorized=False,
                requires_approval=False,
                blocked=True,
                stopping_reason=StoppingReason.HARD_FAILURE_PERMANENT,
                reason=f"Terminal bank decline detected ({decline_code}). All recovery attempts blocked."
            )

        # 2. Customer opt-out is absolute
        if customer.is_opted_out:
            return PolicyCheckResult(
                authorized=False,
                requires_approval=False,
                blocked=True,
                stopping_reason=StoppingReason.CUSTOMER_OPT_OUT,
                reason="Customer has opted out of communication."
            )

        # 2. Check channel permissions (explicitly disabled)
        if proposed_action == InterventionType.PAYMENT_LINK and policy.allow_payment_links is False:
            return PolicyCheckResult(
                authorized=False,
                requires_approval=False,
                blocked=True,
                stopping_reason=StoppingReason.POLICY_BLOCK,
                reason="Merchant policy disables payment link generation."
            )
        if proposed_action == InterventionType.WHATSAPP and policy.allow_whatsapp is False:
            return PolicyCheckResult(
                authorized=False,
                requires_approval=False,
                blocked=True,
                stopping_reason=StoppingReason.POLICY_BLOCK,
                reason="Merchant policy disables WhatsApp communication."
            )
        if proposed_action == InterventionType.SMS and policy.allow_sms is False:
            return PolicyCheckResult(
                authorized=False,
                requires_approval=False,
                blocked=True,
                stopping_reason=StoppingReason.POLICY_BLOCK,
                reason="Merchant policy disables SMS communication."
            )
        if proposed_action == InterventionType.EMAIL and policy.allow_email is False:
            return PolicyCheckResult(
                authorized=False,
                requires_approval=False,
                blocked=True,
                stopping_reason=StoppingReason.POLICY_BLOCK,
                reason="Merchant policy disables Email communication."
            )

        max_retries = policy.max_retry_attempts or 3
        max_contacts = policy.max_contact_attempts or 4
        cooldown_hours = policy.cooldown_hours if policy.cooldown_hours is not None else 12
        approval_threshold = policy.approval_threshold_minor if policy.approval_threshold_minor is not None else 5000000
        max_recovery = policy.max_recovery_attempts or 5

        # 3. Maximum retry attempts
        if proposed_action in (InterventionType.RETRY, InterventionType.SUBSCRIPTION_RETRY):
            if case.retry_count >= max_retries:
                return PolicyCheckResult(
                    authorized=False,
                    requires_approval=False,
                    blocked=True,
                    stopping_reason=StoppingReason.MAX_RETRY_ATTEMPTS,
                    reason=f"Maximum retry attempts reached ({case.retry_count}/{max_retries})."
                )

        # 4. Maximum contact attempts (outbound messages/links)
        if proposed_action in (InterventionType.EMAIL, InterventionType.SMS, InterventionType.WHATSAPP, InterventionType.PAYMENT_LINK):
            if case.contact_count >= max_contacts:
                return PolicyCheckResult(
                    authorized=False,
                    requires_approval=False,
                    blocked=True,
                    stopping_reason=StoppingReason.MAX_CONTACT_ATTEMPTS,
                    reason=f"Maximum contact attempts reached ({case.contact_count}/{max_contacts})."
                )

        # 5. Cooldown check
        if case.last_action_at and cooldown_hours > 0 and not is_manual_approval:
            cooldown_delta = timedelta(hours=cooldown_hours)
            elapsed = utc_now() - (case.last_action_at if case.last_action_at.tzinfo else case.last_action_at.replace(tzinfo=timezone.utc))
            if elapsed < cooldown_delta:
                remaining_mins = int((cooldown_delta - elapsed).total_seconds() // 60)
                return PolicyCheckResult(
                    authorized=False,
                    requires_approval=False,
                    blocked=True,
                    stopping_reason=StoppingReason.COOLDOWN_ACTIVE,
                    reason=f"Action deferred under policy cooldown ({remaining_mins} minutes remaining)."
                )

        # 6. High-value approval threshold requirement
        if not is_manual_approval and case.revenue_at_risk_minor >= approval_threshold:
            return PolicyCheckResult(
                authorized=False,
                requires_approval=True,
                blocked=False,
                stopping_reason=StoppingReason.HUMAN_ESCALATION_REQUIRED,
                reason=f"Revenue at risk exceeds merchant approval threshold."
            )

        # 7. Overall max recovery attempts
        total_attempts = case.retry_count + case.contact_count
        if total_attempts >= max_recovery:
            return PolicyCheckResult(
                authorized=False,
                requires_approval=False,
                blocked=True,
                stopping_reason=StoppingReason.MAX_RETRY_ATTEMPTS,
                reason=f"Maximum total recovery interventions reached ({total_attempts}/{max_recovery})."
            )

        return PolicyCheckResult(
            authorized=True,
            requires_approval=False,
            blocked=False,
            stopping_reason=None,
            reason="Action conforms to all active merchant policies."
        )
