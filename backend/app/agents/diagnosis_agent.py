import json
from typing import Tuple, Dict, Any
from app.services.ai_service import ai_service
from app.schemas.agent import DiagnosisOutput


class DiagnosisAgent:
    """
    Analyzes telemetry, failure reasons, customer background, and transactional risk 
    to diagnose the root cause and assess recoverability.
    """

    SYSTEM_INSTRUCTION = (
        "You are the DiagnosisAgent in REVIVE, an autonomous revenue recovery system. "
        "Your task is to analyze payment/revenue failure signals and diagnose why the transaction failed. "
        "You must return structured, factual output adhering strictly to the schema. "
        "Allowed root cause categories: TEMPORARY_PAYMENT_FAILURE, CUSTOMER_PAYMENT_ISSUE, "
        "REPEATED_PAYMENT_FAILURE, CHECKOUT_ABANDONMENT, SUBSCRIPTION_FAILURE, OVERDUE_RECEIVABLE, UNKNOWN. "
        "Do not hallucinate details not provided in the context."
    )

    @classmethod
    async def run(
        cls,
        case,
        customer,
        transaction,
        recoverability_score: int
    ) -> Tuple[DiagnosisOutput, Dict[str, Any]]:
        context = {
            "case_id": case.id,
            "risk_type": case.risk_type.value,
            "amount_minor": case.revenue_at_risk_minor,
            "failure_code": transaction.failure_code if transaction else None,
            "failure_reason": transaction.failure_reason if transaction else None,
            "recoverability_score": recoverability_score,
            "customer_history": {
                "name": customer.name,
                "recovery_profile": customer.recovery_profile,
                "is_opted_out": customer.is_opted_out,
            },
            "attempts_count": case.retry_count + case.contact_count
        }

        prompt = json.dumps(context, indent=2)
        return await ai_service.generate_structured(
            prompt=prompt,
            system_instruction=cls.SYSTEM_INSTRUCTION,
            response_schema=DiagnosisOutput
        )
