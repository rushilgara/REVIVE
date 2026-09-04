import json
import httpx
from abc import ABC, abstractmethod
from typing import Dict, Any, Type, TypeVar, Optional, Tuple
from pydantic import BaseModel, ValidationError

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import InvalidAIOutputException
from app.schemas.agent import DiagnosisOutput, DecisionOutput, ExplanationOutput, ExplanationSection
from app.utils.enums import RootCauseCategory, InterventionType

T = TypeVar("T", bound=BaseModel)


class AIProvider(ABC):
    """Abstract interface for AI reasoning providers."""

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        system_instruction: str,
        response_schema: Type[T]
    ) -> Tuple[T, Dict[str, Any]]:
        """
        Generates structured output conforming to the response_schema Pydantic model.
        Returns: (parsed_pydantic_instance, metadata_dict)
        """
        pass


class OpenAIProvider(AIProvider):
    """OpenAI API implementation using structured JSON outputs."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model

    async def generate_structured(
        self,
        prompt: str,
        system_instruction: str,
        response_schema: Type[T]
    ) -> Tuple[T, Dict[str, Any]]:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.api_key)
            
            response = await client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                response_format=response_schema,
                temperature=0.1
            )
            
            parsed = response.choices[0].message.parsed
            metadata = {
                "provider": "openai",
                "model": self.model,
                "is_fallback": False,
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
            }
            return parsed, metadata
        except Exception as e:
            logger.error(f"OpenAI API structured generation failed: {e}")
            raise


class GeminiProvider(AIProvider):
    """Google Gemini API implementation using structured JSON responseSchema."""

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model

    async def generate_structured(
        self,
        prompt: str,
        system_instruction: str,
        response_schema: Type[T]
    ) -> Tuple[T, Dict[str, Any]]:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            payload = {
                "contents": [{"parts": [{"text": f"{system_instruction}\n\nContext:\n{prompt}"}]}],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "temperature": 0.1,
                }
            }
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(url, json=payload)
                res.raise_for_status()
                data = res.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = response_schema.model_validate_json(text)
                metadata = {
                    "provider": "gemini",
                    "model": self.model,
                    "is_fallback": False,
                }
                return parsed, metadata
        except Exception as e:
            logger.error(f"Gemini API generation failed: {e}")
            raise


class DeterministicFallbackProvider(AIProvider):
    """
    Guaranteed deterministic fallback reasoning engine.
    Used when external LLM providers are unconfigured, rate-limited, or offline.
    Explicitly labeled as 'deterministic_fallback' - NEVER falsely claimed as an LLM.
    """

    async def generate_structured(
        self,
        prompt: str,
        system_instruction: str,
        response_schema: Type[T]
    ) -> Tuple[T, Dict[str, Any]]:
        # Safely parse JSON context from prompt
        context = {}
        try:
            context = json.loads(prompt)
        except Exception:
            pass

        risk_type = context.get("risk_type", "FAILED_PAYMENT")
        amount_minor = context.get("amount_minor", 499900)
        failure_code = (context.get("failure_code") or "").upper()
        failure_reason = (context.get("failure_reason") or "").lower()
        customer_history = context.get("customer_history", {})
        recoverability_score = context.get("recoverability_score", 75)

        is_temporary = any(term in failure_code or term in failure_reason for term in [
            "NETWORK", "TIMEOUT", "GATEWAY", "SYSTEM", "TEMP", "BANK"
        ])
        is_insufficient = any(term in failure_code or term in failure_reason for term in [
            "INSUFFICIENT", "LIMIT", "BALANCE"
        ])

        if response_schema == DiagnosisOutput:
            if is_temporary:
                root_cause = "Transient bank gateway connectivity disruption during card processing."
                category = RootCauseCategory.TEMPORARY_PAYMENT_FAILURE
                recommended = "Dispatch automated payment link or scheduled retry after transient window."
            elif is_insufficient:
                root_cause = "Account balance insufficient for immediate authorization."
                category = RootCauseCategory.CUSTOMER_PAYMENT_ISSUE
                recommended = "Send smart payment link to allow customer to complete via alternate instrument."
            elif risk_type == "CHECKOUT_ABANDONMENT":
                root_cause = "Customer session expired prior to payment step completion."
                category = RootCauseCategory.CHECKOUT_ABANDONMENT
                recommended = "Send personalized checkout recovery link."
            elif risk_type == "SUBSCRIPTION_FAILURE":
                root_cause = "Recurring recurring billing cycle charge declined by issuer."
                category = RootCauseCategory.SUBSCRIPTION_FAILURE
                recommended = "Execute subscription smart retry with dunning email."
            else:
                root_cause = "Payment authorization rejected by issuing institution."
                category = RootCauseCategory.CUSTOMER_PAYMENT_ISSUE
                recommended = "Initiate omni-channel recovery via secure Razorpay payment link."

            obj = DiagnosisOutput(
                root_cause=root_cause,
                cause_category=category,
                confidence=0.88,
                recoverability=recoverability_score,
                reasoning_summary="Deterministic algorithmic analysis of failure telemetry and customer transaction memory.",
                recommended_next_step=recommended
            )

        elif response_schema == DecisionOutput:
            # Deterministic selection logic based on root cause and amount
            if is_temporary:
                action = InterventionType.PAYMENT_LINK
                reason = "Payment link provides immediate multi-rail fallback (UPI, Cards, NetBanking) bypassing temporary bank issue."
                alternatives = [InterventionType.RETRY, InterventionType.WHATSAPP]
            elif amount_minor > 5000000:  # > ₹50k
                action = InterventionType.PAYMENT_LINK
                reason = "High-value commercial transaction requires auditable, direct payment link authorization."
                alternatives = [InterventionType.HUMAN_ESCALATION, InterventionType.EMAIL]
            elif risk_type == "SUBSCRIPTION_FAILURE":
                action = InterventionType.SUBSCRIPTION_RETRY
                reason = "Subscription mandate retry aligned with scheduled card cycle."
                alternatives = [InterventionType.PAYMENT_LINK, InterventionType.EMAIL]
            else:
                action = InterventionType.PAYMENT_LINK
                reason = "Payment links historically yield the highest customer completion rate."
                alternatives = [InterventionType.WHATSAPP, InterventionType.EMAIL]

            expected_rec = (recoverability_score * amount_minor) // 100
            obj = DecisionOutput(
                recommended_action=action,
                confidence=0.89,
                expected_recovery_minor=expected_rec,
                reason=reason,
                alternative_actions=alternatives
            )

        elif response_schema == ExplanationOutput:
            obj = ExplanationOutput(
                summary=f"Recovery case evaluated: {recoverability_score}/100 recoverability probability.",
                recoverability_explanation=ExplanationSection(
                    title="Recoverability Assessment",
                    headline=f"{recoverability_score}/100 Estimated Probability",
                    details="Calculated from customer transaction history, failure code classification, and channel affinity.",
                    positive_factors=["Prior successful payment completions", "Standard retail transaction amount"],
                    risk_factors=["Initial payment attempt rejected"]
                ),
                root_cause_explanation=ExplanationSection(
                    title="Diagnostic Telemetry",
                    headline="Payment Processing Disruption",
                    details="Automated telemetry indicates non-fatal disruption at processing layer.",
                    positive_factors=[],
                    risk_factors=[]
                ),
                action_recommendation_explanation=ExplanationSection(
                    title="Intervention Proposal",
                    headline="Recommended Action: Payment Link",
                    details="Deploying a direct Razorpay payment link enables customer to self-heal across UPI or cards.",
                    positive_factors=["Supports immediate checkout", "Tracks click and payment events"],
                    risk_factors=[]
                )
            )
        else:
            raise ValueError(f"Unsupported schema for deterministic fallback: {response_schema}")

        metadata = {
            "provider": "deterministic_fallback",
            "model": "rule_based_engine_v1",
            "is_fallback": True,
            "prompt_tokens": 0,
            "completion_tokens": 0,
        }
        return obj, metadata


class AIService:
    """
    Central AI service orchestrator. Manages provider lifecycle, executes structured 
    generation, strictly validates outputs, and seamlessly activates deterministic fallback.
    """

    def __init__(self):
        self.provider: AIProvider = self._select_provider()

    def _select_provider(self) -> AIProvider:
        prov = settings.AI_PROVIDER.lower()
        if prov == "openai" and settings.OPENAI_API_KEY:
            logger.info("Configuring AI provider: OpenAI")
            return OpenAIProvider(settings.OPENAI_API_KEY, settings.OPENAI_MODEL)
        elif prov == "gemini" and settings.GEMINI_API_KEY:
            logger.info("Configuring AI provider: Google Gemini")
            return GeminiProvider(settings.GEMINI_API_KEY, settings.GEMINI_MODEL)
        else:
            logger.info("Configuring AI provider: Deterministic Fallback Engine")
            return DeterministicFallbackProvider()

    async def generate_structured(
        self,
        prompt: str,
        system_instruction: str,
        response_schema: Type[T]
    ) -> Tuple[T, Dict[str, Any]]:
        try:
            result, metadata = await self.provider.generate_structured(
                prompt, system_instruction, response_schema
            )
            self._validate_semantic_safety(result)
            return result, metadata
        except Exception as e:
            if not isinstance(self.provider, DeterministicFallbackProvider):
                logger.warning(f"Primary AI Provider failed ({e}). Activating deterministic fallback.")
                fallback = DeterministicFallbackProvider()
                result, metadata = await fallback.generate_structured(
                    prompt, system_instruction, response_schema
                )
                return result, metadata
            raise InvalidAIOutputException(f"AI generation failed: {e}")

    def _validate_semantic_safety(self, result: Any):
        """
        Enforces Directive 7:
        AI outputs must be checked for impossible monetary values and invalid actions.
        """
        if isinstance(result, DecisionOutput):
            if result.expected_recovery_minor < 0:
                raise InvalidAIOutputException("AI proposed impossible negative expected recovery.")
            if not isinstance(result.recommended_action, InterventionType):
                raise InvalidAIOutputException(f"AI proposed unsupported action: {result.recommended_action}")
        elif isinstance(result, DiagnosisOutput):
            if not (0 <= result.recoverability <= 100):
                raise InvalidAIOutputException("AI proposed recoverability score outside 0-100.")


ai_service = AIService()
