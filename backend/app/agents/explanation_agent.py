import json
from typing import Tuple, Dict, Any
from app.services.ai_service import ai_service
from app.schemas.agent import ExplanationOutput


class ExplanationAgent:
    """
    Generates structured, executive-level explanations for merchant operators.
    Avoids long conversational paragraphs and produces crisp, scannable decision rationale.
    """

    SYSTEM_INSTRUCTION = (
        "You are the ExplanationAgent in REVIVE. "
        "Summarize why this case is recoverable, the root cause, and why the action was recommended. "
        "Produce concise, structured bullet points designed for a fintech dashboard. "
        "Do not output chatty language or conversational filler."
    )

    @classmethod
    async def run(
        cls,
        case,
        customer,
        diagnosis,
        decision
    ) -> Tuple[ExplanationOutput, Dict[str, Any]]:
        context = {
            "case_id": case.id,
            "amount_minor": case.revenue_at_risk_minor,
            "recoverability_score": diagnosis.recoverability,
            "root_cause": diagnosis.root_cause,
            "recommended_action": decision.recommended_action.value,
            "action_reason": decision.reason,
            "customer_name": customer.name,
            "customer_profile": customer.recovery_profile
        }

        prompt = json.dumps(context, indent=2)
        return await ai_service.generate_structured(
            prompt=prompt,
            system_instruction=cls.SYSTEM_INSTRUCTION,
            response_schema=ExplanationOutput
        )
