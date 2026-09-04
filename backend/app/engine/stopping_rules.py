from typing import Optional, Tuple
from app.utils.enums import StoppingReason, CaseStatus


class StoppingRulesEngine:
    """
    Deterministic safety cutoffs.
    Monitors case state and evaluates whether safety thresholds mandate 
    halting all autonomous recovery attempts.
    """

    HARD_DECLINE_CODES = {
        "do_not_honor",
        "stolen_card",
        "lost_card",
        "pickup_card",
        "card_blacklisted",
        "blacklisted_card",
        "account_closed",
        "closed_account",
        "fraudulent",
        "suspected_fraud",
        "hard_decline",
        "terminal_failure",
        "restricted_card",
    }

    @classmethod
    def is_hard_decline(cls, case) -> Tuple[bool, Optional[str]]:
        error_code = getattr(case, "gateway_error_code", None)
        if not error_code and hasattr(case, "transaction") and case.transaction:
            error_code = getattr(case.transaction, "failure_code", None)
        if error_code:
            code_norm = str(error_code).strip().lower()
            if code_norm in cls.HARD_DECLINE_CODES or any(
                term in code_norm for term in ("do_not_honor", "stolen", "lost_card", "pickup_card", "blacklisted", "fraud")
            ):
                return True, str(error_code)
        return False, None

    @classmethod
    def should_stop(cls, case, policy, customer) -> Tuple[bool, Optional[StoppingReason], str]:
        # 1. Terminal / hard bank decline
        is_hard, decline_code = cls.is_hard_decline(case)
        if is_hard:
            return True, StoppingReason.HARD_FAILURE_PERMANENT, f"Terminal bank decline detected ({decline_code}). Recovery permanently halted."

        # 2. Revenue already recovered
        recovered = case.recovered_amount_minor or 0
        if case.status == CaseStatus.RECOVERED or recovered >= case.revenue_at_risk_minor:
            return True, StoppingReason.REVENUE_RECOVERED, "Revenue has been fully recovered."

        # 3. Customer opt out
        if customer.is_opted_out:
            return True, StoppingReason.CUSTOMER_OPT_OUT, "Customer has explicitly opted out of communications."

        # 3. Maximum retries reached
        if case.retry_count >= policy.max_retry_attempts:
            return True, StoppingReason.MAX_RETRY_ATTEMPTS, f"Hit ceiling of {policy.max_retry_attempts} retry attempts."

        # 4. Maximum contacts reached
        if case.contact_count >= policy.max_contact_attempts:
            return True, StoppingReason.MAX_CONTACT_ATTEMPTS, f"Hit ceiling of {policy.max_contact_attempts} contact attempts."

        # 5. Total interventions ceiling
        total_interventions = case.retry_count + case.contact_count
        if total_interventions >= policy.max_recovery_attempts:
            return True, StoppingReason.MAX_RETRY_ATTEMPTS, f"Hit ceiling of {policy.max_recovery_attempts} total interventions."

        # 6. Case expiration
        if case.expires_at and case.expires_at < case.updated_at:
            return True, StoppingReason.CASE_EXPIRED, "Recovery case has expired past its SLA window."

        return False, None, ""
