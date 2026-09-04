export type RiskType =
  | 'FAILED_PAYMENT'
  | 'CHECKOUT_ABANDONMENT'
  | 'SUBSCRIPTION_FAILURE'
  | 'OVERDUE_RECEIVABLE';

export type CaseStatus =
  | 'OPEN'
  | 'DIAGNOSING'
  | 'READY_FOR_ACTION'
  | 'PENDING_APPROVAL'
  | 'EXECUTING'
  | 'RECOVERED'
  | 'FAILED'
  | 'ESCALATED'
  | 'STOPPED'
  | 'EXPIRED';

export type InterventionType =
  | 'RETRY'
  | 'PAYMENT_LINK'
  | 'EMAIL'
  | 'SMS'
  | 'WHATSAPP'
  | 'SUBSCRIPTION_RETRY'
  | 'HUMAN_ESCALATION'
  | 'STOP';

export type RootCauseCategory =
  | 'TEMPORARY_PAYMENT_FAILURE'
  | 'CUSTOMER_PAYMENT_ISSUE'
  | 'REPEATED_PAYMENT_FAILURE'
  | 'CHECKOUT_ABANDONMENT'
  | 'SUBSCRIPTION_FAILURE'
  | 'OVERDUE_RECEIVABLE'
  | 'UNKNOWN';

export interface CustomerBrief {
  id: string;
  name: string;
  email: string;
  phone?: string;
  recovery_profile: {
    total_transactions?: number;
    successful_recoveries?: number;
    failure_count?: number;
    preferred_channel?: string;
    channel_history?: Record<string, string[]>;
  };
  is_opted_out: boolean;
}

export interface RecoveryCase {
  id: string;
  merchant_id: string;
  customer_id: string;
  transaction_id?: string;
  risk_type: RiskType;
  status: CaseStatus;
  revenue_at_risk_minor: number;
  recovered_amount_minor: number;
  recoverability_score: number;
  recoverability_reasons: string[];
  root_cause?: string;
  root_cause_category: RootCauseCategory;
  recommended_action?: InterventionType;
  stopping_reason?: string;
  retry_count: number;
  contact_count: number;
  last_action_at?: string;
  expires_at?: string;
  created_at: string;
  updated_at: string;
  customer?: CustomerBrief;
}

export interface RecoveryCaseDetail extends RecoveryCase {
  transaction?: {
    id: string;
    amount_minor: number;
    currency: string;
    payment_method: string;
    failure_code?: string;
    failure_reason?: string;
    created_at: string;
  };
  interventions: Array<{
    id: string;
    type: InterventionType;
    status: string;
    idempotency_key: string;
    payload: any;
    execution_result: any;
    error_message?: string;
    created_at: string;
  }>;
  decisions: Array<{
    id: string;
    agent_name: string;
    provider: string;
    proposed_action: string;
    confidence_score: number;
    expected_recovery_minor: number;
    reasoning_summary: string;
    is_fallback: boolean;
    created_at: string;
  }>;
  outcomes: Array<{
    id: string;
    verified: boolean;
    amount_recovered_minor: number;
    confirmation_source: string;
    gateway_payment_id?: string;
    verified_at?: string;
    created_at: string;
  }>;
  audit_events: Array<{
    id: string;
    correlation_id: string;
    event_type: string;
    actor: string;
    description: string;
    metadata_payload: any;
    created_at: string;
  }>;
  policy_authorization?: {
    authorized: boolean;
    requires_approval: boolean;
    blocked: boolean;
    stopping_reason?: string;
    reason: string;
  };
}

export interface DashboardMetrics {
  revenue_at_risk_minor: number;
  revenue_recovered_minor: number;
  recovery_rate_pct: number;
  active_cases_count: number;
  pending_approvals_count: number;
  recovered_cases_count: number;
  failed_cases_count: number;
  stopped_cases_count: number;
  escalated_cases_count: number;
  recovery_timeline: Array<{
    date: string;
    revenue_at_risk_minor: number;
    revenue_recovered_minor: number;
    cases_count: number;
  }>;
  intervention_performance: Array<{
    name: string;
    count: number;
    recovered_count: number;
    revenue_minor: number;
  }>;
  root_cause_breakdown: Array<{
    name: string;
    count: number;
    recovered_count: number;
    revenue_minor: number;
  }>;
  recent_activity: Array<{
    id: string;
    correlation_id: string;
    case_id?: string;
    event_type: string;
    actor: string;
    description: string;
    created_at: string;
  }>;
}

export interface PolicyConfig {
  id: string;
  merchant_id: string;
  max_retry_attempts: number;
  max_contact_attempts: number;
  cooldown_hours: number;
  approval_threshold_minor: number;
  max_discount_minor: number;
  max_recovery_attempts: number;
  allow_whatsapp: boolean;
  allow_sms: boolean;
  allow_email: boolean;
  allow_payment_links: boolean;
  auto_escalate_repeated_failures: boolean;
  created_at: string;
  updated_at: string;
}

export interface StrategyMetrics {
  strategy_name: string;
  total_cases: number;
  revenue_at_risk_minor: number;
  revenue_recovered_minor: number;
  recovery_rate_pct: number;
  total_retries: number;
  total_customer_contacts: number;
  total_interventions: number;
  policy_violations: number;
  unauthorized_attempts: number;
  escalated_cases: number;
  stopped_cases: number;
  recovered_cases: number;
  average_recovery_time_hours: number;
  average_recovery_amount_minor: number;
}

export interface EvaluationResult {
  evaluation_id: string;
  dataset_size: number;
  random_seed: number;
  revive: StrategyMetrics;
  baseline: StrategyMetrics;
  lift_recovered_revenue_pct: number;
  contact_reduction_pct: number;
  policy_compliance_improvement_pct: number;
  key_findings: string[];
}

export interface SimulationResult {
  simulation_id: string;
  scenario_preset: string;
  transaction_count: number;
  random_seed: number;
  duration_ms: number;
  total_cases_created: number;
  recovered_cases: number;
  pending_approval_cases: number;
  stopped_cases: number;
  escalated_cases: number;
  revenue_at_risk_minor: number;
  revenue_recovered_minor: number;
  recovery_rate_pct: number;
  scenarios_tested: string[];
  summary_message: string;
}
