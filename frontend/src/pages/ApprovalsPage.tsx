import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  CheckCircle2,
  XCircle,
  Clock,
  AlertTriangle,
  RefreshCw,
  ArrowRight,
  ShieldAlert,
} from 'lucide-react';

import { api } from '../api/client';
import { Header } from '../layouts/Header';
import { formatINR } from '../utils/money';
import { EmptyState } from '../components/common/EmptyState';

export const ApprovalsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [rejectModalCaseId, setRejectModalCaseId] = useState<string | null>(null);
  const [rejectReason, setRejectReason] = useState<string>('Exceeds current operational risk tolerance');

  const { data: cases = [], isLoading, refetch } = useQuery({
    queryKey: ['pendingApprovals'],
    queryFn: () => api.getPendingApprovals(),
    refetchInterval: 5000,
  });

  const approveMutation = useMutation({
    mutationFn: (caseId: string) => api.approveCase(caseId, true),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pendingApprovals'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['cases'] });
    },
  });

  const rejectMutation = useMutation({
    mutationFn: ({ caseId, reason }: { caseId: string; reason: string }) =>
      api.rejectCase(caseId, reason),
    onSuccess: () => {
      setRejectModalCaseId(null);
      queryClient.invalidateQueries({ queryKey: ['pendingApprovals'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['cases'] });
    },
  });

  return (
    <div className="flex flex-col flex-1">
      <Header
        title="Approval Center"
        subtitle="Review high-value recovery interventions restricted by merchant policy"
        actions={
          <button
            onClick={() => refetch()}
            className="p-1.5 text-slate-500 hover:text-primary-900 hover:bg-slate-100 rounded-lg transition-fintech"
            title="Refresh approvals"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        }
      />

      <div className="p-8 space-y-6 max-w-7xl">
        {/* Policy Notice Card */}
        <div className="bg-amber-50/70 border border-amber-200/80 rounded-xl p-4 flex items-center justify-between text-xs text-amber-900">
          <div className="flex items-center gap-3">
            <ShieldAlert className="w-5 h-5 text-amber-600 shrink-0" />
            <div>
              <span className="font-semibold">Deterministic Policy Threshold Active: </span>
              <span>All recovery actions involving ₹50,000 or greater require explicit merchant authorization.</span>
            </div>
          </div>
          <span className="font-bold text-amber-800 bg-amber-100 px-2.5 py-1 rounded-md">
            {cases.length} Awaiting Authorization
          </span>
        </div>

        {/* Approvals List */}
        {isLoading ? (
          <div className="space-y-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-32 bg-surface rounded-xl border border-border animate-pulse" />
            ))}
          </div>
        ) : cases.length === 0 ? (
          <EmptyState
            icon={<CheckCircle2 className="w-8 h-8 text-emerald-500" />}
            title="Approval queue clear"
            description="No recovery actions currently exceed policy thresholds or require human intervention."
          />
        ) : (
          <div className="space-y-4">
            {cases.map((c) => (
              <div
                key={c.id}
                className="bg-surface border border-border rounded-xl p-6 shadow-card hover:border-slate-300 transition-fintech flex flex-col md:flex-row items-start md:items-center justify-between gap-6"
              >
                {/* Case & Customer Info */}
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-semibold text-primary-900">
                      {c.id.slice(0, 8)}
                    </span>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 font-semibold">
                      PENDING APPROVAL
                    </span>
                  </div>
                  <div className="text-xl font-bold tracking-tight text-primary-900">
                    {formatINR(c.revenue_at_risk_minor)}
                  </div>
                  <p className="text-xs text-slate-600">
                    Customer: <span className="font-medium text-slate-900">{c.customer?.name}</span> ({c.customer?.email})
                  </p>
                </div>

                {/* AI Recommendation & Rationale */}
                <div className="bg-slate-50 border border-slate-200/80 rounded-lg p-3 text-xs space-y-1 max-w-md w-full">
                  <div className="flex justify-between items-center text-slate-500 text-[10px] font-semibold uppercase">
                    <span>Proposed Intervention</span>
                    <span className="text-emerald-700 font-bold">
                      Recoverability: {c.recoverability_score}/100
                    </span>
                  </div>
                  <div className="font-bold text-primary-900">
                    {c.recommended_action ? c.recommended_action.replace(/_/g, ' ') : 'PAYMENT LINK'}
                  </div>
                  <p className="text-slate-600 text-[11px] leading-relaxed">
                    Policy Requirement: Action paused because transaction value exceeds threshold (₹50,000).
                  </p>
                </div>

                {/* Action Buttons */}
                <div className="flex items-center gap-2 w-full md:w-auto shrink-0">
                  <button
                    onClick={() => approveMutation.mutate(c.id)}
                    disabled={approveMutation.isPending}
                    className="flex-1 md:flex-none inline-flex items-center justify-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold shadow-subtle transition-fintech disabled:opacity-50"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Approve & Execute</span>
                  </button>

                  <button
                    onClick={() => setRejectModalCaseId(c.id)}
                    className="flex-1 md:flex-none inline-flex items-center justify-center gap-1.5 px-3 py-2 bg-slate-100 hover:bg-rose-50 hover:text-rose-700 text-slate-700 border border-slate-200 rounded-lg text-xs font-medium transition-fintech"
                  >
                    <XCircle className="w-4 h-4" />
                    <span>Reject</span>
                  </button>

                  <button
                    onClick={() => navigate(`/recovery/${c.id}`)}
                    className="p-2 text-slate-400 hover:text-primary-900 hover:bg-slate-100 rounded-lg transition-fintech"
                    title="View case detail"
                  >
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Reject Modal */}
        {rejectModalCaseId && (
          <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
            <div className="bg-surface border border-border rounded-xl p-6 max-w-md w-full shadow-elevated space-y-4">
              <h3 className="text-sm font-semibold text-primary-900">Reject Recovery Intervention</h3>
              <p className="text-xs text-slate-500">
                Provide a reason for stopping this recovery action. This will be permanently recorded in the immutable audit log.
              </p>
              <textarea
                rows={3}
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                className="w-full text-xs p-2.5 bg-slate-50 border border-border rounded-lg text-primary-900 focus:outline-none focus:border-primary-900"
              />
              <div className="flex justify-end gap-2">
                <button
                  onClick={() => setRejectModalCaseId(null)}
                  className="px-3 py-1.5 text-xs text-slate-600 hover:text-primary-900 font-medium"
                >
                  Cancel
                </button>
                <button
                  onClick={() =>
                    rejectMutation.mutate({ caseId: rejectModalCaseId, reason: rejectReason })
                  }
                  className="px-3 py-1.5 text-xs bg-rose-600 hover:bg-rose-700 text-white rounded-lg font-semibold"
                >
                  Confirm Rejection
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
