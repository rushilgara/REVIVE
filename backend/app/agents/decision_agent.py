import json
from typing import Tuple, Dict, Any, List
from app.services.ai_service import ai_service
from app.schemas.agent import DecisionOutput
from app.utils.enums import InterventionType


class DecisionAgent:
    """
    Evaluates diagnosed root cause, customer recovery memory, and Expected Recovery Value (ERV)
    to propose the highest-ranking recovery intervention.
    """

    SYSTEM_INSTRUCTION = (
        "You are the DecisionAgent in REVIVE, an autonomous revenue recovery system. "
        "Your task is to recommend the optimal revenue recovery intervention. "
        "Allowed actions: RETRY, PAYMENT_LINK, EMAIL, SMS, WHATSAPP, SUBSCRIPTION_RETRY, "
        "HUMAN_ESCALATION, STOP. "
        "Calculate Expected Recovery Value (ERV = Probability * Amount - Cost). "
        "Respect customer channel memory and choose the intervention with highest utility."
    )

    @classmethod
    async def run(
        cls,
        case,
        customer,
        diagnosis,
        allowed_actions: List[InterventionType]
    ) -> Tuple[DecisionOutput, Dict[str, Any]]:
        context = {
            "case_id": case.id,
            "risk_type": case.risk_type.value,
            "amount_minor": case.revenue_at_risk_minor,
            "root_cause": diagnosis.root_cause,
            "cause_category": diagnosis.cause_category.value,
            "recoverability_score": diagnosis.recoverability,
            "customer_profile": customer.recovery_profile,
            "allowed_actions": [a.value for a in allowed_actions],
            "retry_count": case.retry_count,
            "contact_count": case.contact_count
        }

        prompt = json.dumps(context, indent=2)
        return await ai_service.generate_structured(
            prompt=prompt,
            system_instruction=cls.SYSTEM_INSTRUCTION,
            response_schema=DecisionOutput
        )
