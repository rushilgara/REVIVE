import {
  DashboardMetrics,
  RecoveryCase,
  RecoveryCaseDetail,
  PolicyConfig,
  EvaluationResult,
  SimulationResult,
} from '../types';

const API_BASE = '/api/v1';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = 'Request failed';
    try {
      const err = await res.json();
      errorDetail = err.message || err.detail || JSON.stringify(err);
    } catch {
      errorDetail = `HTTP ${res.status}: ${res.statusText}`;
    }
    throw new Error(errorDetail);
  }
  return res.json();
}

export const api = {
  // Dashboard
  getDashboard: (merchantId?: string): Promise<DashboardMetrics> => {
    const url = merchantId ? `${API_BASE}/dashboard?merchant_id=${merchantId}` : `${API_BASE}/dashboard`;
    return fetch(url).then(handleResponse<DashboardMetrics>);
  },

  // Recovery Cases
  getRecoveryCases: (params?: {
    status?: string;
    risk_type?: string;
    search?: string;
    min_score?: number;
    limit?: number;
    offset?: number;
  }): Promise<{ items: RecoveryCase[]; limit: number; offset: number }> => {
    const query = new URLSearchParams();
    if (params?.status) query.append('status', params.status);
    if (params?.risk_type) query.append('risk_type', params.risk_type);
    if (params?.search) query.append('search', params.search);
    if (params?.min_score !== undefined) query.append('min_score', params.min_score.toString());
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.offset) query.append('offset', params.offset.toString());
    return fetch(`${API_BASE}/recovery/cases?${query.toString()}`).then(
      handleResponse<{ items: RecoveryCase[]; limit: number; offset: number }>
    );
  },

  getCaseDetail: (caseId: string): Promise<RecoveryCaseDetail> => {
    return fetch(`${API_BASE}/recovery/cases/${caseId}`).then(handleResponse<RecoveryCaseDetail>);
  },

  runRecovery: (caseId: string, simulatePayment: boolean = false): Promise<any> => {
    return fetch(`${API_BASE}/recovery/cases/${caseId}/run?simulate_payment=${simulatePayment}`, {
      method: 'POST',
    }).then(handleResponse);
  },

  // Actions
  executeAction: (
    caseId: string,
    interventionType?: string,
    simulatePayment: boolean = false
  ): Promise<any> => {
    return fetch(`${API_BASE}/actions/${caseId}/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        intervention_type: interventionType,
        simulate_payment: simulatePayment,
      }),
    }).then(handleResponse);
  },

  simulatePayment: (caseId: string): Promise<any> => {
    return fetch(`${API_BASE}/actions/${caseId}/simulate-payment`, {
      method: 'POST',
    }).then(handleResponse);
  },

  // Approvals
  getPendingApprovals: (): Promise<RecoveryCase[]> => {
    return fetch(`${API_BASE}/approvals`).then(handleResponse<RecoveryCase[]>);
  },

  approveCase: (caseId: string, simulatePayment: boolean = true): Promise<any> => {
    return fetch(`${API_BASE}/approvals/${caseId}/approve?simulate_payment=${simulatePayment}`, {
      method: 'POST',
    }).then(handleResponse);
  },

  rejectCase: (caseId: string, reason: string): Promise<any> => {
    return fetch(`${API_BASE}/approvals/${caseId}/reject`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reason }),
    }).then(handleResponse);
  },

  // Policies
  getPolicies: (): Promise<PolicyConfig> => {
    return fetch(`${API_BASE}/policies`).then(handleResponse<PolicyConfig>);
  },

  updatePolicies: (policy: Partial<PolicyConfig>): Promise<PolicyConfig> => {
    return fetch(`${API_BASE}/policies`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(policy),
    }).then(handleResponse<PolicyConfig>);
  },

  // Audit
  getAuditEvents: (caseId?: string, limit: number = 50): Promise<any[]> => {
    const url = caseId ? `${API_BASE}/audit?case_id=${caseId}&limit=${limit}` : `${API_BASE}/audit?limit=${limit}`;
    return fetch(url).then(handleResponse<any[]>);
  },

  // Simulation
  runSimulation: (params: {
    transaction_count: number;
    random_seed: number;
    scenario_preset: string;
  }): Promise<SimulationResult> => {
    return fetch(`${API_BASE}/simulation/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    }).then(handleResponse<SimulationResult>);
  },

  // Evaluation
  getEvaluation: (datasetSize: number = 1000, seed: number = 101): Promise<EvaluationResult> => {
    return fetch(`${API_BASE}/evaluation?dataset_size=${datasetSize}&random_seed=${seed}`).then(
      handleResponse<EvaluationResult>
    );
  },

  // Health
  getHealth: (): Promise<any> => {
    return fetch(`${API_BASE}/health`).then(handleResponse);
  },

  // Demo
  runDemoScenario: (scenario: 'case-a' | 'case-b' | 'case-c'): Promise<any> => {
    return fetch(`${API_BASE}/demo/${scenario}`, { method: 'POST' }).then(handleResponse);
  },
};
