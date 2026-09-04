from typing import List, Tuple, Dict, Any, Optional
from app.utils.enums import RiskType, RootCauseCategory


class RiskEngine:
    """
    Deterministic risk scoring and recoverability estimation engine.
    Produces a 0-100 recoverability score accompanied by transparent, 
    explainable positive and negative contributors.
    """

    @staticmethod
    def calculate_recoverability(
        risk_type: RiskType,
        amount_minor: int,
        failure_code: Optional[str],
        failure_reason: Optional[str],
        customer_profile: Dict[str, Any],
        attempts_count: int = 0
    ) -> Tuple[int, List[str], RootCauseCategory]:
        """
        Computes score (0-100), explainable reasons, and standardized root cause category.
        """
        score = 50
        reasons: List[str] = []
        category = RootCauseCategory.UNKNOWN

        # 1. Evaluate failure code & reason
        fail_code_str = (failure_code or "").upper()
        fail_reason_str = (failure_reason or "").lower()

        is_temporary = any(term in fail_code_str or term in fail_reason_str for term in [
            "NETWORK", "TIMEOUT", "GATEWAY_TIMEOUT", "SYSTEM_ERROR", "TEMPORARY", "BANK_ERROR"
        ])
        is_insufficient_funds = any(term in fail_code_str or term in fail_reason_str for term in [
            "INSUFFICIENT", "LIMIT_EXCEEDED", "LOW_BALANCE"
        ])
        is_card_issue = any(term in fail_code_str or term in fail_reason_str for term in [
            "EXPIRED", "CARD_DECLINED", "INVALID_CARD", "PIN_INCORRECT", "AUTH_FAILED"
        ])

        if is_temporary:
            score += 25
            reasons.append("+ Temporary network/gateway disruption detected")
            category = RootCauseCategory.TEMPORARY_PAYMENT_FAILURE
        elif is_insufficient_funds:
            score += 10
            reasons.append("+ Temporary liquidity issue; customer likely to pay with link or retry")
            category = RootCauseCategory.CUSTOMER_PAYMENT_ISSUE
        elif is_card_issue:
            score += 5
            reasons.append("~ Card/instrument issue requires alternate payment method")
            category = RootCauseCategory.CUSTOMER_PAYMENT_ISSUE
        elif risk_type == RiskType.CHECKOUT_ABANDONMENT:
            score += 15
            reasons.append("+ Intent is high; abandoned during checkout stage")
            category = RootCauseCategory.CHECKOUT_ABANDONMENT
        elif risk_type == RiskType.SUBSCRIPTION_FAILURE:
            score += 15
            reasons.append("+ Active recurring subscriber")
            category = RootCauseCategory.SUBSCRIPTION_FAILURE
        elif risk_type == RiskType.OVERDUE_RECEIVABLE:
            score += 5
            reasons.append("+ Commercial invoice pending payment")
            category = RootCauseCategory.OVERDUE_RECEIVABLE
        else:
            category = RootCauseCategory.UNKNOWN

        # 2. Customer payment history & recovery profile
        total_tx = customer_profile.get("total_transactions", 0)
        successful_recoveries = customer_profile.get("successful_recoveries", 0)
        preferred_channel = customer_profile.get("preferred_channel")
        historical_failures = customer_profile.get("failure_count", 0)

        if total_tx > 5:
            score += 15
            reasons.append("+ Established customer with strong transaction history")
        elif total_tx > 0:
            score += 8
            reasons.append("+ Customer has prior completed orders")
        else:
            reasons.append("~ First-time customer transaction")

        if successful_recoveries > 0:
            score += 15
            reasons.append(f"+ Customer previously recovered successfully ({successful_recoveries} times)")
            if preferred_channel:
                reasons.append(f"+ Known response affinity to {preferred_channel}")

        if historical_failures > 3:
            score -= 15
            reasons.append("- History of repeated past payment difficulties")
            category = RootCauseCategory.REPEATED_PAYMENT_FAILURE

        # 3. Penalties for prior failed recovery attempts in current case
        if attempts_count == 1:
            score -= 8
            reasons.append("- 1 previous recovery attempt failed")
        elif attempts_count == 2:
            score -= 18
            reasons.append("- 2 previous recovery attempts failed")
        elif attempts_count >= 3:
            score -= 30
            reasons.append(f"- Multiple ({attempts_count}) attempts have failed")

        # 4. Monetary magnitude calibration
        if amount_minor > 5000000:  # > ₹50,000
            score -= 5
            reasons.append("- High transaction value typically has lower impulsive recovery rate")

        # Clamp score between 5 and 98 (never claim 0% or 100% certainty)
        final_score = max(5, min(98, score))
        return final_score, reasons, category
