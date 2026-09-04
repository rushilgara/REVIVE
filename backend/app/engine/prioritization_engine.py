from typing import List, Tuple, Dict
from app.utils.enums import InterventionType
from app.utils.money import calculate_erv

INTERVENTION_COSTS_MINOR: Dict[InterventionType, int] = {
    InterventionType.RETRY: 50,              # ₹0.50 gateway attempt
    InterventionType.SUBSCRIPTION_RETRY: 50, # ₹0.50
    InterventionType.EMAIL: 10,              # ₹0.10 dispatch
    InterventionType.SMS: 25,                # ₹0.25 telco SMS
    InterventionType.WHATSAPP: 80,           # ₹0.80 meta business API
    InterventionType.PAYMENT_LINK: 200,      # ₹2.00 link generation & SMS/Email
    InterventionType.HUMAN_ESCALATION: 5000, # ₹50.00 ops time
    InterventionType.STOP: 0
}


class PrioritizationEngine:
    """
    Ranks viable interventions based on Expected Recovery Value (ERV)
    and historical customer channel memory.
    """

    @staticmethod
    def calculate_erv_for_action(
        action: InterventionType,
        base_probability_pct: int,
        revenue_at_risk_minor: int,
        customer_profile: Dict
    ) -> int:
        # Channel affinity modifier
        prob = base_probability_pct
        preferred = customer_profile.get("preferred_channel")
        
        if action == InterventionType.PAYMENT_LINK and preferred == "payment_link":
            prob = min(98, prob + 15)
        elif action == InterventionType.WHATSAPP and preferred == "whatsapp":
            prob = min(98, prob + 12)
        elif action == InterventionType.RETRY and preferred == "retry":
            prob = min(98, prob + 10)

        cost = INTERVENTION_COSTS_MINOR.get(action, 100)
        return calculate_erv(prob, revenue_at_risk_minor, cost)

    @staticmethod
    def rank_actions(
        base_probability_pct: int,
        revenue_at_risk_minor: int,
        customer_profile: Dict,
        allowed_actions: List[InterventionType]
    ) -> List[Tuple[InterventionType, int]]:
        scored = []
        for action in allowed_actions:
            erv = PrioritizationEngine.calculate_erv_for_action(
                action, base_probability_pct, revenue_at_risk_minor, customer_profile
            )
            scored.append((action, erv))
            
        # Sort descending by ERV
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored
