import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  ArrowLeft,
  ShieldCheck,
  ShieldAlert,
  Clock,
  CheckCircle2,
  AlertCircle,
  Play,
  CreditCard,
  Send,
  User,
  History,
  FileText,
  ExternalLink,
  ChevronRight,
  Zap,
} from 'lucide-react';

import { api } from '../api/client';
import { Header } from '../layouts/Header';
import { StatusBadge } from '../components/common/StatusBadge';
import { formatINR } from '../utils/money';

export const CaseDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const { data: caseDetail, isLoading, isError, refetch } = useQuery({
    queryKey: ['caseDetail', id],
    queryFn: () => api.getCaseDetail(id!),
    enabled: !!id,
    refetchInterval: 5000,
  });

  // Mutation to Run Workflow
  const runMutation = useMutation({
    mutationFn: (simulatePayment: boolean) => api.runRecovery(id!, simulatePayment),
    onSuccess: (res) => {
      setActionMessage(
        res.recovered
          ? 'Autonomous workflow executed: Payment confirmed & case marked RECOVERED!'
          : `Workflow executed: Current status is ${res.status}.`
      );
      queryClient.invalidateQueries({ queryKey: ['caseDetail', id] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
    onError: (err: any) => {
      setActionMessage(`Error: ${err.message}`);
    },
  });

  // Mutation to Simulate Payment
  const simPaymentMutation = useMutation({
    mutationFn: () => api.simulatePayment(id!),
    onSuccess: (res) => {
      setActionMessage(res.message);
      queryClient.invalidateQueries({ queryKey: ['caseDetail', id] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
    onError: (err: any) => {
      setActionMessage(`Error: ${err.message}`);
    },
  });

  // Mutation to Approve Case
  const approveMutation = useMutation({
    mutationFn: () => api.approveCase(id!, true),
    onSuccess: () => {
      setActionMessage('Case approved by operator and executed successfully.');
      queryClient.invalidateQueries({ queryKey: ['caseDetail', id] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });

  if (isLoading) {
    return (
      <div className="p-8 space-y-6">
        <div className="h-8 w-48 bg-slate-200 rounded animate-pulse" />
        <div className="grid grid-cols-3 gap-6">
          <div className="h-64 bg-surface rounded-xl border border-border animate-pulse" />
          <div className="h-64 bg-surface rounded-xl border border-border animate-pulse" />
          <div className="h-64 bg-surface rounded-xl border border-border animate-pulse" />
        </div>
      </div>
    );
  }

  if (isError || !caseDetail) {
    return (
      <div className="p-8">
        <div className="bg-rose-50 border border-rose-200 rounded-xl p-6 text-center">
          <AlertCircle className="w-8 h-8 text-rose-600 mx-auto mb-2" />
          <h3 className="text-sm font-semibold text-rose-900">Case Not Found</h3>
          <button
            onClick={() => navigate('/recovery')}
            className="mt-4 px-4 py-2 bg-primary-900 text-white rounded-lg text-xs font-medium"
          >
            Back to Cases
          </button>
        </div>
      </div>
    );
  }

  const isRecovered = caseDetail.status === 'RECOVERED';
  const isPendingApproval = caseDetail.status === 'PENDING_APPROVAL';

  return (
    <div className="flex flex-col flex-1">
      {/* Top Navigation Bar */}
      <div className="h-16 border-b border-border bg-surface px-8 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <Link
            to="/recovery"
            className="p-1.5 text-slate-500 hover:text-primary-900 hover:bg-slate-100 rounded-lg transition-fintech"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-sm font-semibold text-primary-900">
                Case {caseDetail.id.slice(0, 12)}
              </span>
              <StatusBadge status={caseDetail.status} />
            </div>
            <p className="text-[11px] text-slate-500">
              Detected {new Date(caseDetail.created_at).toLocaleString()}
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          {isPendingApproval ? (
            <button
              onClick={() => approveMutation.mutate()}
              disabled={approveMutation.isPending}
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold shadow-subtle transition-fintech"
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Approve & Dispatch</span>
            </button>
          ) : !isRecovered ? (
            <>
              <button
                onClick={() => runMutation.mutate(false)}
                disabled={runMutation.isPending}
                className="inline-flex items-center gap-1.5 px-3 py-2 bg-primary-900 hover:bg-primary-800 text-white rounded-lg text-xs font-medium shadow-subtle transition-fintech"
              >
                <Zap className="w-3.5 h-3.5" />
                <span>Run Autonomous Recovery</span>
              </button>

              <button
                onClick={() => simPaymentMutation.mutate()}
                disabled={simPaymentMutation.isPending}
                className="inline-flex items-center gap-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-primary-900 border border-border rounded-lg text-xs font-medium transition-fintech"
              >
                <CreditCard className="w-3.5 h-3.5 text-emerald-600" />
                <span>Simulate Customer Payment</span>
              </button>
            </>
          ) : (
            <div className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-xs font-medium">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Revenue Verified & Settled</span>
            </div>
          )}
        </div>
      </div>

      {/* Action status message toast if any */}
      {actionMessage && (
        <div className="bg-slate-900 text-white px-8 py-2.5 text-xs flex items-center justify-between">
          <span>{actionMessage}</span>
          <button onClick={() => setActionMessage(null)} className="text-slate-400 hover:text-white">
            ✕
          </button>
        </div>
      )}

      {/* Content Body */}
      <div className="p-8 space-y-8 max-w-7xl">
        {/* Row 1: Financial State & Customer Recovery Memory */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Financial Loss Card */}
          <div className="bg-surface border border-border rounded-xl p-6 shadow-card">
            <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
              <span className="font-semibold uppercase tracking-wider">Revenue at Risk</span>
              <span className="font-mono">{caseDetail.risk_type.replace(/_/g, ' ')}</span>
            </div>
            <div className="text-3xl font-bold tracking-tight text-primary-900 mb-1">
              {formatINR(caseDetail.revenue_at_risk_minor)}
            </div>
            <p className="text-xs text-slate-500">
              {isRecovered
                ? `Fully recovered (${formatINR(caseDetail.recovered_amount_minor)})`
                : 'Pending recovery resolution'}
            </p>

            <div className="mt-6 pt-4 border-t border-border/60 space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-500">Attempt Count</span>
                <span className="font-medium text-slate-900">
                  {caseDetail.retry_count} retries · {caseDetail.contact_count} contacts
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Payment Instrument</span>
                <span className="font-medium text-slate-900 capitalize">
                  {caseDetail.transaction?.payment_method || 'Card'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Gateway Error Code</span>
                <span className="font-mono font-medium text-rose-700">
                  {caseDetail.transaction?.failure_code || 'GATEWAY_DECLINE'}
                </span>
              </div>
            </div>
          </div>

          {/* Customer Recovery Memory Card */}
          <div className="bg-surface border border-border rounded-xl p-6 shadow-card">
            <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
              <span className="font-semibold uppercase tracking-wider">Customer Memory</span>
              <User className="w-4 h-4 text-slate-400" />
            </div>
            <div className="text-base font-semibold text-primary-900 truncate">
              {caseDetail.customer?.name || 'Customer'}
            </div>
            <p className="text-xs text-slate-500 truncate mb-4">{caseDetail.customer?.email}</p>

            <div className="space-y-2.5 text-xs">
              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200/60 flex justify-between items-center">
                <span className="text-slate-600">Past Recoveries</span>
                <span className="font-semibold text-emerald-700">
                  {caseDetail.customer?.recovery_profile?.successful_recoveries || 0} Successful
                </span>
              </div>
              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200/60 flex justify-between items-center">
                <span className="text-slate-600">Preferred Channel</span>
                <span className="font-medium text-slate-800 capitalize">
                  {caseDetail.customer?.recovery_profile?.preferred_channel || 'Payment Link'}
                </span>
              </div>
              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200/60 flex justify-between items-center">
                <span className="text-slate-600">Opt-Out Status</span>
                <span className={caseDetail.customer?.is_opted_out ? 'text-rose-600 font-bold' : 'text-slate-600'}>
                  {caseDetail.customer?.is_opted_out ? 'OPTED OUT' : 'Subscribed'}
                </span>
              </div>
            </div>
          </div>

          {/* Policy Guardrails Status Card */}
          <div className="bg-surface border border-border rounded-xl p-6 shadow-card flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
                <span className="font-semibold uppercase tracking-wider">Merchant Policy Guard</span>
                {caseDetail.policy_authorization?.blocked ? (
                  <ShieldAlert className="w-4 h-4 text-rose-500" />
                ) : (
                  <ShieldCheck className="w-4 h-4 text-emerald-500" />
                )}
              </div>
              <div className="text-base font-semibold text-primary-900 mb-1">
                {caseDetail.policy_authorization?.requires_approval
                  ? 'Human Approval Required'
                  : caseDetail.policy_authorization?.blocked
                  ? 'Policy Blocked'
                  : 'Policy Authorized'}
              </div>
              <p className="text-xs text-slate-600 leading-relaxed mb-4">
                {caseDetail.policy_authorization?.reason || 'Complies with merchant safety thresholds.'}
              </p>
            </div>

            <div className="pt-3 border-t border-border/60 text-[11px] text-slate-500 flex justify-between">
              <span>Threshold: ₹50,000</span>
              <span>Max Retries: 3</span>
            </div>
          </div>
        </div>

        {/* Row 2: Explainable Recoverability & AI Diagnosis */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recoverability Score Breakdown */}
          <div className="bg-surface border border-border rounded-xl p-6 shadow-card">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-semibold text-primary-900">Recoverability Assessment</h3>
                <p className="text-xs text-slate-500">Deterministic scoring model (0–100)</p>
              </div>
              <div className="text-2xl font-extrabold text-primary-900 px-3 py-1 bg-slate-100 rounded-lg border border-slate-200">
                {caseDetail.recoverability_score}
                <span className="text-xs font-normal text-slate-500">/100</span>
              </div>
            </div>

            <div className="space-y-2 mt-4">
              <span className="text-xs font-semibold text-slate-600 uppercase tracking-wider">
                Explainable Score Contributors
              </span>
              <ul className="space-y-1.5 text-xs text-slate-700">
                {caseDetail.recoverability_reasons.map((r, i) => (
                  <li
                    key={i}
                    className={`p-2 rounded border ${
                      r.startsWith('+')
                        ? 'bg-emerald-50/60 border-emerald-200 text-emerald-900'
                        : r.startsWith('-')
                        ? 'bg-rose-50/60 border-rose-200 text-rose-900'
                        : 'bg-slate-50 border-slate-200 text-slate-800'
                    }`}
                  >
                    {r}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* AI Decision & ERV Proposal */}
          <div className="bg-surface border border-border rounded-xl p-6 shadow-card flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-sm font-semibold text-primary-900">Diagnosis & Proposal</h3>
                  <p className="text-xs text-slate-500">Decision Agent expected recovery value</p>
                </div>
                <span className="text-xs font-mono font-medium px-2 py-0.5 bg-slate-100 rounded border border-slate-200 text-slate-700">
                  {caseDetail.root_cause_category.replace(/_/g, ' ')}
                </span>
              </div>

              <div className="space-y-3 text-xs">
                <div>
                  <span className="font-semibold text-slate-500 uppercase tracking-wider text-[10px]">
                    Identified Root Cause
                  </span>
                  <p className="text-slate-800 font-medium mt-0.5">
                    {caseDetail.root_cause || 'Transient bank connectivity disruption.'}
                  </p>
                </div>

                <div>
                  <span className="font-semibold text-slate-500 uppercase tracking-wider text-[10px]">
                    Recommended Intervention
                  </span>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="font-bold text-primary-900 text-sm">
                      {caseDetail.recommended_action
                        ? caseDetail.recommended_action.replace(/_/g, ' ')
                        : 'PAYMENT LINK'}
                    </span>
                    <span className="text-emerald-700 font-medium">
                      (ERV: {formatINR((caseDetail.recoverability_score * caseDetail.revenue_at_risk_minor) / 100)})
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-border/60 text-[11px] text-slate-500">
              <span>Safety Rule: AI proposal validated through deterministic merchant policies.</span>
            </div>
          </div>
        </div>

        {/* Row 3: Chronological Audit Ledger Timeline */}
        <div className="bg-surface border border-border rounded-xl p-6 shadow-card">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-sm font-semibold text-primary-900">Chronological State Audit Trail</h3>
              <p className="text-xs text-slate-500">Immutable ledger of signals, policies, executions, and verification</p>
            </div>
            <History className="w-4 h-4 text-slate-400" />
          </div>

          <div className="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
            {caseDetail.audit_events.map((event, i) => (
              <div key={event.id} className="relative flex items-start justify-between gap-4 text-xs">
                <span className="absolute -left-6 top-1 w-2.5 h-2.5 rounded-full bg-primary-900 border-2 border-white shadow-sm" />
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-primary-900">{event.event_type.replace(/_/g, ' ')}</span>
                    <span className="text-[10px] px-1.5 py-0.2 bg-slate-100 text-slate-600 rounded">
                      {event.actor}
                    </span>
                  </div>
                  <p className="text-slate-700 mt-1 leading-relaxed">{event.description}</p>
                </div>
                <div className="shrink-0 text-slate-400 font-mono text-[11px]">
                  {new Date(event.created_at).toLocaleTimeString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
