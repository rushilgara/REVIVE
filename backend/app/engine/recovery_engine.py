import uuid
from typing import Dict, Any, Optional, Tuple, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.recovery_case import RecoveryCase
from app.models.customer import Customer
from app.models.transaction import Transaction
from app.models.policy import Policy
from app.models.intervention import Intervention
from app.models.agent_decision import AgentDecision
from app.models.audit_event import AuditEvent
from app.utils.enums import (
    RiskType, CaseStatus, InterventionType, RootCauseCategory,
    StoppingReason, AuditEventType, ActorType, NotificationChannel
)
from app.utils.timestamps import utc_now
from app.core.logging import logger
from app.core.exceptions import (
    PolicyViolationException, StoppingRuleException,
    IdempotencyConflictException, ExecutorUnavailableException
)
from app.engine.state_machine import RecoveryStateMachine
from app.engine.risk_engine import RiskEngine
from app.engine.policy_engine import PolicyEngine
from app.engine.stopping_rules import StoppingRulesEngine
from app.engine.prioritization_engine import PrioritizationEngine
from app.engine.outcome_engine import OutcomeEngine
from app.agents.diagnosis_agent import DiagnosisAgent
from app.agents.decision_agent import DecisionAgent
from app.agents.explanation_agent import ExplanationAgent
from app.services.razorpay_service import razorpay_service
from app.services.notification_service import notification_service


class RecoveryEngine:
    """
    Master autonomous revenue recovery orchestration engine.
    Orchestrates the entire product loop:
    DETECT -> DIAGNOSE -> DECIDE -> GUARD -> EXECUTE -> VERIFY -> LEARN -> MEASURE
    """

    @staticmethod
    async def get_or_create_policy(db: AsyncSession, merchant_id: str) -> Policy:
        stmt = select(Policy).where(Policy.merchant_id == merchant_id)
        result = await db.execute(stmt)
        policy = result.scalar_one_or_none()
        if not policy:
            policy = Policy(merchant_id=merchant_id)
            db.add(policy)
            await db.flush()
        return policy

    @staticmethod
    async def detect_and_create_case(
        db: AsyncSession,
        merchant_id: str,
        customer: Customer,
        risk_type: RiskType,
        revenue_at_risk_minor: int,
        transaction: Optional[Transaction] = None,
        correlation_id: Optional[str] = None
    ) -> RecoveryCase:
        corr_id = correlation_id or str(uuid.uuid4())

        # 1. Deterministic recoverability scoring
        score, reasons, category = RiskEngine.calculate_recoverability(
            risk_type=risk_type,
            amount_minor=revenue_at_risk_minor,
            failure_code=transaction.failure_code if transaction else None,
            failure_reason=transaction.failure_reason if transaction else None,
            customer_profile=customer.recovery_profile or {},
            attempts_count=0
        )

        case = RecoveryCase(
            merchant_id=merchant_id,
            customer_id=customer.id,
            transaction_id=transaction.id if transaction else None,
            risk_type=risk_type,
            status=CaseStatus.OPEN,
            revenue_at_risk_minor=revenue_at_risk_minor,
            recovered_amount_minor=0,
            recoverability_score=score,
            recoverability_reasons=reasons,
            root_cause_category=category,
            retry_count=0,
            contact_count=0
        )
        db.add(case)
        await db.flush()

        # Audit initial risk detection
        audit = AuditEvent(
            correlation_id=corr_id,
            recovery_case_id=case.id,
            event_type=AuditEventType.REVENUE_RISK_DETECTED,
            actor=ActorType.SYSTEM,
            actor_id="risk_engine",
            description=f"Revenue risk detected: {risk_type.value} of ₹{revenue_at_risk_minor / 100:,.2f}.",
            metadata_payload={
                "risk_type": risk_type.value,
                "amount_minor": revenue_at_risk_minor,
                "recoverability_score": score,
                "reasons": reasons
            }
        )
        db.add(audit)
        await db.flush()
        return case

    @staticmethod
    async def run_autonomous_workflow(
        db: AsyncSession,
        case_id: str,
        correlation_id: Optional[str] = None,
        simulate_payment: bool = False
    ) -> Tuple[RecoveryCase, Optional[Intervention]]:
        corr_id = correlation_id or str(uuid.uuid4())

        stmt = select(RecoveryCase).options(
            selectinload(RecoveryCase.customer),
            selectinload(RecoveryCase.transaction),
            selectinload(RecoveryCase.merchant)
        ).where(RecoveryCase.id == case_id)
        result = await db.execute(stmt)
        case = result.scalar_one_or_none()
        if not case:
            raise ValueError(f"Recovery case {case_id} not found.")

        customer = case.customer
        transaction = case.transaction
        policy = await RecoveryEngine.get_or_create_policy(db, case.merchant_id)

        # 1. State transition: OPEN -> DIAGNOSING
        if case.status == CaseStatus.OPEN:
            RecoveryStateMachine.transition(case, CaseStatus.DIAGNOSING)
            await db.flush()

        # 2. Check stopping rules before investing in agent reasoning
        should_stop, stop_reason, stop_msg = StoppingRulesEngine.should_stop(case, policy, customer)
        if should_stop:
            case.stopping_reason = stop_reason
            RecoveryStateMachine.transition(case, CaseStatus.STOPPED)
            audit = AuditEvent(
                correlation_id=corr_id,
                recovery_case_id=case.id,
                event_type=AuditEventType.CASE_STOPPED,
                actor=ActorType.POLICY_ENGINE,
                actor_id="stopping_rules",
                description=f"Case stopped by safety rules: {stop_msg}",
                metadata_payload={"stopping_reason": stop_reason.value, "detail": stop_msg}
            )
            db.add(audit)
            await db.commit()
            return case, None

        # 3. DIAGNOSIS AGENT
        diag_output, diag_meta = await DiagnosisAgent.run(
            case, customer, transaction, case.recoverability_score
        )
        case.root_cause = diag_output.root_cause
        case.root_cause_category = diag_output.cause_category

        diag_decision = AgentDecision(
            recovery_case_id=case.id,
            agent_name="DiagnosisAgent",
            provider=diag_meta.get("provider", "deterministic_fallback"),
            model_name=diag_meta.get("model", "default"),
            proposed_action="DIAGNOSE",
            confidence_score=diag_output.confidence,
            expected_recovery_minor=0,
            reasoning_summary=diag_output.reasoning_summary,
            raw_response=diag_output.model_dump(),
            is_fallback=diag_meta.get("is_fallback", False)
        )
        db.add(diag_decision)

        # Audit diagnosis
        audit_diag = AuditEvent(
            correlation_id=corr_id,
            recovery_case_id=case.id,
            event_type=AuditEventType.DIAGNOSIS_COMPLETED,
            actor=ActorType.AI_AGENT,
            actor_id="DiagnosisAgent",
            description=f"Diagnosis completed: {diag_output.cause_category.value}. {diag_output.root_cause}",
            metadata_payload=diag_output.model_dump()
        )
        db.add(audit_diag)

        # 4. DECISION AGENT
        allowed_actions = [InterventionType.PAYMENT_LINK, InterventionType.RETRY, InterventionType.WHATSAPP, InterventionType.EMAIL]
        dec_output, dec_meta = await DecisionAgent.run(
            case, customer, diag_output, allowed_actions
        )
        case.recommended_action = dec_output.recommended_action

        dec_decision = AgentDecision(
            recovery_case_id=case.id,
            agent_name="DecisionAgent",
            provider=dec_meta.get("provider", "deterministic_fallback"),
            model_name=dec_meta.get("model", "default"),
            proposed_action=dec_output.recommended_action.value,
            confidence_score=dec_output.confidence,
            expected_recovery_minor=dec_output.expected_recovery_minor,
            reasoning_summary=dec_output.reason,
            raw_response=dec_output.model_dump(),
            is_fallback=dec_meta.get("is_fallback", False)
        )
        db.add(dec_decision)

        # Audit decision proposal
        audit_prop = AuditEvent(
            correlation_id=corr_id,
            recovery_case_id=case.id,
            event_type=AuditEventType.ACTION_PROPOSED,
            actor=ActorType.AI_AGENT,
            actor_id="DecisionAgent",
            description=f"Recommended intervention: {dec_output.recommended_action.value}. Expected recovery: ₹{dec_output.expected_recovery_minor / 100:,.2f}.",
            metadata_payload=dec_output.model_dump()
        )
        db.add(audit_prop)

        # 5. DETERMINISTIC POLICY ENGINE GUARD
        policy_result = PolicyEngine.evaluate(
            case=case,
            proposed_action=dec_output.recommended_action,
            policy=policy,
            customer=customer
        )

        audit_policy = AuditEvent(
            correlation_id=corr_id,
            recovery_case_id=case.id,
            event_type=AuditEventType.POLICY_CHECK,
            actor=ActorType.POLICY_ENGINE,
            actor_id="policy_engine",
            description=f"Policy check: {policy_result.reason}",
            metadata_payload={
                "authorized": policy_result.authorized,
                "requires_approval": policy_result.requires_approval,
                "blocked": policy_result.blocked,
                "reason": policy_result.reason
            }
        )
        db.add(audit_policy)

        # If human approval is required
        if policy_result.requires_approval:
            RecoveryStateMachine.transition(case, CaseStatus.PENDING_APPROVAL)
            audit_esc = AuditEvent(
                correlation_id=corr_id,
                recovery_case_id=case.id,
                event_type=AuditEventType.HUMAN_ESCALATION,
                actor=ActorType.POLICY_ENGINE,
                actor_id="approval_guard",
                description=f"Transaction value (₹{case.revenue_at_risk_minor / 100:,.2f}) requires human approval.",
                metadata_payload={"threshold_minor": policy.approval_threshold_minor}
            )
            db.add(audit_esc)
            await db.commit()
            return case, None

        # If policy blocks action
        if policy_result.blocked:
            case.stopping_reason = policy_result.stopping_reason
            RecoveryStateMachine.transition(case, CaseStatus.STOPPED)
            audit_blk = AuditEvent(
                correlation_id=corr_id,
                recovery_case_id=case.id,
                event_type=AuditEventType.ACTION_BLOCKED,
                actor=ActorType.POLICY_ENGINE,
                actor_id="policy_block",
                description=f"Action blocked by policy: {policy_result.reason}",
                metadata_payload={"stopping_reason": policy_result.stopping_reason.value if policy_result.stopping_reason else None}
            )
            db.add(audit_blk)
            await db.commit()
            return case, None

        # Policy Authorized -> transition to READY_FOR_ACTION
        RecoveryStateMachine.transition(case, CaseStatus.READY_FOR_ACTION)
        await db.flush()

        # 6. ACTION EXECUTOR
        intervention = await RecoveryEngine.execute_intervention(
            db=db,
            case=case,
            customer=customer,
            action=dec_output.recommended_action,
            correlation_id=corr_id,
            simulate_payment=simulate_payment
        )
        await db.commit()
        return case, intervention

    @staticmethod
    async def execute_intervention(
        db: AsyncSession,
        case: RecoveryCase,
        customer: Customer,
        action: InterventionType,
        correlation_id: str,
        idempotency_key: Optional[str] = None,
        simulate_payment: bool = False,
        simulate_executor_failure: bool = False
    ) -> Intervention:
        """
        Deterministic Action Executor.
        Executes bounded actions, enforces idempotency, updates attempts counter,
        and triggers outcome verification.
        """
        idem_key = idempotency_key or f"idem_{case.id}_{action.value}_{case.retry_count}_{case.contact_count}"

        # 1. Idempotency check
        existing_stmt = select(Intervention).where(Intervention.idempotency_key == idem_key)
        existing = (await db.execute(existing_stmt)).scalar_one_or_none()
        if existing:
            logger.info(f"Duplicate intervention idempotency key '{idem_key}' returning existing.")
            return existing

        # 2. State transition -> EXECUTING
        RecoveryStateMachine.transition(case, CaseStatus.EXECUTING)
        case.last_action_at = utc_now()
        await db.flush()

        # 3. Simulate executor failure scenario (Testing & Demo Case C)
        if simulate_executor_failure:
            RecoveryStateMachine.transition(case, CaseStatus.ESCALATED)
            intervention = Intervention(
                recovery_case_id=case.id,
                intervention_type=action,
                status="FAILED",
                idempotency_key=idem_key,
                error_message="Gateway executor unavailable (connection refused).",
                execution_result={"executor_status": "UNAVAILABLE"}
            )
            db.add(intervention)
            audit_fail = AuditEvent(
                correlation_id=correlation_id,
                recovery_case_id=case.id,
                event_type=AuditEventType.EXECUTION_FAILED,
                actor=ActorType.SYSTEM,
                actor_id="action_executor",
                description="Action execution failed: Gateway connection refused. Case escalated.",
                metadata_payload={"error": "EXECUTOR_UNAVAILABLE"}
            )
            db.add(audit_fail)
            await db.flush()
            return intervention

        execution_payload: Dict[str, Any] = {}
        execution_result: Dict[str, Any] = {}

        # 4. Action Dispatch
        if action == InterventionType.PAYMENT_LINK:
            case.contact_count += 1
            plink = await razorpay_service.create_payment_link(
                amount_minor=case.revenue_at_risk_minor,
                currency="INR",
                description=f"Complete recovery for case {case.id[:8]}",
                customer_name=customer.name,
                customer_email=customer.email,
                customer_phone=customer.phone,
                notes={"recovery_case_id": case.id}
            )
            execution_result = plink
            execution_payload = {
                "link_id": plink["id"],
                "short_url": plink["short_url"]
            }

            # Also send notification
            await notification_service.send_notification(
                db=db,
                case_id=case.id,
                customer_id=customer.id,
                channel=NotificationChannel.EMAIL,
                recipient=customer.email,
                subject=f"Action Required: Complete your ₹{case.revenue_at_risk_minor / 100:,.2f} payment",
                body=f"Dear {customer.name}, please complete your pending payment using your secure link: {plink['short_url']}"
            )

            audit_act = AuditEvent(
                correlation_id=correlation_id,
                recovery_case_id=case.id,
                event_type=AuditEventType.PAYMENT_LINK_CREATED,
                actor=ActorType.SYSTEM,
                actor_id="payment_link_service",
                description=f"Generated secure payment link: {plink['short_url']}",
                metadata_payload=execution_payload
            )
            db.add(audit_act)

        elif action in (InterventionType.RETRY, InterventionType.SUBSCRIPTION_RETRY):
            case.retry_count += 1
            execution_payload = {"gateway": "razorpay", "method": "auto_retry"}
            execution_result = {"status": "retry_dispatched", "timestamp": utc_now().isoformat()}
            
            audit_act = AuditEvent(
                correlation_id=correlation_id,
                recovery_case_id=case.id,
                event_type=AuditEventType.ACTION_EXECUTED,
                actor=ActorType.SYSTEM,
                actor_id="gateway_retry",
                description=f"Dispatched payment retry #{case.retry_count}",
                metadata_payload=execution_payload
            )
            db.add(audit_act)

        elif action in (InterventionType.WHATSAPP, InterventionType.SMS, InterventionType.EMAIL):
            case.contact_count += 1
            channel_enum = NotificationChannel(action.value)
            await notification_service.send_notification(
                db=db,
                case_id=case.id,
                customer_id=customer.id,
                channel=channel_enum,
                recipient=customer.phone or customer.email,
                subject="Update on your pending transaction",
                body=f"Hello {customer.name}, we noticed an issue completing your transaction of ₹{case.revenue_at_risk_minor / 100:,.2f}. Let us help."
            )
            execution_payload = {"channel": action.value, "recipient": customer.email}
            execution_result = {"status": "dispatched"}
            
            audit_act = AuditEvent(
                correlation_id=correlation_id,
                recovery_case_id=case.id,
                event_type=AuditEventType.ACTION_EXECUTED,
                actor=ActorType.SYSTEM,
                actor_id="notification_service",
                description=f"Dispatched {action.value} notification.",
                metadata_payload=execution_payload
            )
            db.add(audit_act)

        intervention = Intervention(
            recovery_case_id=case.id,
            intervention_type=action,
            status="SUCCESS",
            idempotency_key=idem_key,
            channel=action.value,
            payload=execution_payload,
            execution_result=execution_result,
            dispatched_at=utc_now(),
            completed_at=utc_now()
        )
        db.add(intervention)
        await db.flush()

        # 5. OUTCOME VERIFICATION:
        # Action execution != Recovered.
        # Only simulate_payment or verified webhook causes RECOVERED.
        if simulate_payment:
            logger.info(f"Simulating customer payment verification for case {case.id}")
            verified, outcome, audit_outcome = OutcomeEngine.verify_payment_outcome(
                case=case,
                amount_minor=case.revenue_at_risk_minor,
                confirmation_source="SIMULATED_CUSTOMER_PAYMENT",
                gateway_payment_id=f"pay_sim_{uuid.uuid4().hex[:12]}",
                metadata_payload={"simulation": True, "intervention_id": intervention.id},
                correlation_id=correlation_id
            )
            db.add(outcome)
            db.add(audit_outcome)

        return intervention

    @staticmethod
    async def approve_case(
        db: AsyncSession,
        case_id: str,
        user_id: str = "merchant_admin",
        simulate_payment: bool = False
    ) -> RecoveryCase:
        stmt = select(RecoveryCase).options(
            selectinload(RecoveryCase.customer),
            selectinload(RecoveryCase.merchant)
        ).where(RecoveryCase.id == case_id)
        result = await db.execute(stmt)
        case = result.scalar_one_or_none()
        if not case:
            raise ValueError("Case not found.")

        if case.status != CaseStatus.PENDING_APPROVAL:
            raise ValueError(f"Case cannot be approved from state '{case.status.value}'. Must be PENDING_APPROVAL.")

        corr_id = str(uuid.uuid4())
        audit = AuditEvent(
            correlation_id=corr_id,
            recovery_case_id=case.id,
            event_type=AuditEventType.ACTION_APPROVED,
            actor=ActorType.MERCHANT_USER,
            actor_id=user_id,
            description=f"Merchant human operator approved recovery action for ₹{case.revenue_at_risk_minor / 100:,.2f}.",
            metadata_payload={"approved_by": user_id, "amount_minor": case.revenue_at_risk_minor}
        )
        db.add(audit)

        # Transition to READY_FOR_ACTION then execute
        RecoveryStateMachine.transition(case, CaseStatus.READY_FOR_ACTION)
        action_to_run = case.recommended_action or InterventionType.PAYMENT_LINK
        await RecoveryEngine.execute_intervention(
            db=db,
            case=case,
            customer=case.customer,
            action=action_to_run,
            correlation_id=corr_id,
            simulate_payment=simulate_payment
        )
        await db.commit()
        return case

    @staticmethod
    async def reject_case(
        db: AsyncSession,
        case_id: str,
        reason: str = "Rejected by merchant operator",
        user_id: str = "merchant_admin"
    ) -> RecoveryCase:
        stmt = select(RecoveryCase).where(RecoveryCase.id == case_id)
        result = await db.execute(stmt)
        case = result.scalar_one_or_none()
        if not case:
            raise ValueError("Case not found.")

        if case.status != CaseStatus.PENDING_APPROVAL:
            raise ValueError(f"Case cannot be rejected from state '{case.status.value}'. Must be PENDING_APPROVAL.")

        corr_id = str(uuid.uuid4())
        case.stopping_reason = StoppingReason.MERCHANT_REJECTED
        RecoveryStateMachine.transition(case, CaseStatus.STOPPED)

        audit = AuditEvent(
            correlation_id=corr_id,
            recovery_case_id=case.id,
            event_type=AuditEventType.ACTION_REJECTED,
            actor=ActorType.MERCHANT_USER,
            actor_id=user_id,
            description=f"Merchant human operator rejected recovery: {reason}",
            metadata_payload={"rejected_by": user_id, "reason": reason}
        )
        db.add(audit)
        await db.commit()
        return case


recovery_engine = RecoveryEngine()
