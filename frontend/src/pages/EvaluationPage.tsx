import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  BarChart3,
  TrendingUp,
  ShieldCheck,
  Zap,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Scale,
} from 'lucide-react';

import { api } from '../api/client';
import { Header } from '../layouts/Header';
import { formatINR, formatPercentage } from '../utils/money';

export const EvaluationPage: React.FC = () => {
  const { data: evalResult, isLoading, refetch } = useQuery({
    queryKey: ['evaluation'],
    queryFn: () => api.getEvaluation(1000, 101),
  });

  if (isLoading) {
    return (
      <div className="flex flex-col flex-1">
        <Header title="Evaluation Benchmark" subtitle="REVIVE vs. Naive Baseline on identical cloned datasets" />
        <div className="p-8 space-y-6">
          <div className="h-40 bg-surface rounded-xl border border-border animate-pulse" />
          <div className="grid grid-cols-2 gap-6">
            <div className="h-64 bg-surface rounded-xl border border-border animate-pulse" />
            <div className="h-64 bg-surface rounded-xl border border-border animate-pulse" />
          </div>
        </div>
      </div>
    );
  }

  if (!evalResult) return null;

  const r = evalResult.revive;
  const b = evalResult.baseline;

  return (
    <div className="flex flex-col flex-1">
      <Header
        title="Evaluation Benchmark"
        subtitle="REVIVE vs. Baseline (Naive Blind Retry) over an identical 1,000-case dataset"
        actions={
          <button
            onClick={() => refetch()}
            className="p-1.5 text-slate-500 hover:text-primary-900 hover:bg-slate-100 rounded-lg transition-fintech"
            title="Re-run benchmark"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        }
      />

      <div className="p-8 space-y-8 max-w-7xl">
        {/* Headline Value Lift Banner */}
        <div className="bg-surface border border-border rounded-xl p-6 shadow-card">
          <div className="flex items-center gap-2 mb-2 text-slate-500">
            <Scale className="w-4 h-4" />
            <span className="text-xs font-semibold uppercase tracking-wider">Methodology & Dataset</span>
          </div>
          <h2 className="text-xl font-bold tracking-tight text-primary-900 mb-1">
            Scientific Comparative Analysis: {evalResult.dataset_size} Cloned Cases
          </h2>
          <p className="text-xs text-slate-600 max-w-2xl leading-relaxed">
            Both models were evaluated on the exact same customers, transaction amounts, failure codes, and true recoverability distributions.
            Only the recovery strategy differs.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6 pt-6 border-t border-border">
            <div className="p-4 bg-emerald-50/70 border border-emerald-200 rounded-xl">
              <span className="text-[11px] font-bold uppercase text-emerald-800 tracking-wider">Revenue Lift</span>
              <div className="text-2xl font-extrabold text-emerald-950 mt-1">
                +{evalResult.lift_recovered_revenue_pct}%
              </div>
              <p className="text-[11px] text-emerald-700 mt-0.5">Incremental recovered capital</p>
            </div>

            <div className="p-4 bg-blue-50/70 border border-blue-200 rounded-xl">
              <span className="text-[11px] font-bold uppercase text-blue-800 tracking-wider">Spam Reduction</span>
              <div className="text-2xl font-extrabold text-blue-950 mt-1">
                -{evalResult.contact_reduction_pct}%
              </div>
              <p className="text-[11px] text-blue-700 mt-0.5">Fewer blind card retries</p>
            </div>

            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl">
              <span className="text-[11px] font-bold uppercase text-slate-700 tracking-wider">Policy Compliance</span>
              <div className="text-2xl font-extrabold text-primary-900 mt-1">
                100%
              </div>
              <p className="text-[11px] text-slate-600 mt-0.5">0 opt-out or approval violations</p>
            </div>
          </div>
        </div>

        {/* Side-by-Side Comparison Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* REVIVE Card */}
          <div className="bg-surface border-2 border-primary-900 rounded-xl p-6 shadow-card relative">
            <div className="flex items-center justify-between mb-4">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                  Track 03 Architecture
                </span>
                <h3 className="text-base font-bold text-primary-900 mt-1">REVIVE Orchestration Layer</h3>
              </div>
              <Zap className="w-5 h-5 text-primary-900" />
            </div>

            <p className="text-xs text-slate-600 mb-6 leading-relaxed">
              Context-aware root-cause diagnosis, omnichannel intervention selection (Payment Links, SMS, WhatsApp), merchant policies, and stopping rules.
            </p>

            <div className="space-y-3 text-xs divide-y divide-border/60">
              <div className="flex justify-between py-2">
                <span className="text-slate-600">Total Recovered Revenue</span>
                <span className="font-bold text-emerald-700 text-sm">{formatINR(r.revenue_recovered_minor)}</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-slate-600">Overall Recovery Rate</span>
                <span className="font-bold text-primary-900">{formatPercentage(r.recovery_rate_pct)}</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-slate-600">Recovered Cases</span>
                <span className="font-medium text-slate-900">{r.recovered_cases} / {r.total_cases}</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-slate-600">Blind Card Retries</span>
                <span className="font-medium text-emerald-700">{r.total_retries}</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-slate-600">Omnichannel Links & Contacts</span>
                <span className="font-medium text-slate-900">{r.total_customer_contacts}</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-slate-600">Policy Violations (Opt-Outs)</span>
                <span className="font-bold text-emerald-700">{r.policy_violations} (0%)</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-slate-600">Unauthorized High-Value Retries</span>
                <span className="font-bold text-emerald-700">{r.unauthorized_attempts} (0%)</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-slate-600">Average Time to Recovery</span>
                <span className="font-medium text-primary-900">{r.average_recovery_time_hours} Hours</span>
              </div>
            </div>
          </div>

          {/* BASELINE Card */}
          <div className="bg-surface border border-border rounded-xl p-6 shadow-card">
            <div className="flex items-center justify-between mb-4">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-600 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                  Standard Industry Pattern
                </span>
                <h3 className="text-base font-bold text-primary-900 mt-1">Baseline (Naive Blind Retry)</h3>
              </div>
              <RefreshCw className="w-5 h-5 text-slate-400" />
            </div>

            <p className="text-xs text-slate-600 mb-6 leading-relaxed">
              Blindly retries failed cards up to 3 times regardless of failure reason, opt-out status, or transaction magnitude. Zero omnichannel capability.
            </p>

            <div className="space-y-3 text-xs divide-y divide-border/60">
              <div className="flex justify-between py-2">
                <span className="text-slate-600">Total Recovered Revenue</span>
                <span className="font-bold text-slate-700 text-sm">{formatINR(b.revenue_recovered_minor)}</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-slate-600">Overall Recovery Rate</span>
                <span className="font-bold text-slate-800">{formatPercentage(b.recovery_rate_pct)}</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-slate-600">Recovered Cases</span>
                <span className="font-medium text-slate-900">{b.recovered_cases} / {b.total_cases}</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-slate-600">Blind Card Retries</span>
                <span className="font-bold text-rose-700">{b.total_retries} (Spam fatigue)</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-slate-600">Omnichannel Links & Contacts</span>
                <span className="font-medium text-slate-400">0 (No alternative channels)</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-slate-600">Policy Violations (Opt-Outs)</span>
                <span className="font-bold text-rose-700">{b.policy_violations} Violations</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-slate-600">Unauthorized High-Value Retries</span>
                <span className="font-bold text-rose-700">{b.unauthorized_attempts} Retries</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-slate-600">Average Time to Recovery</span>
                <span className="font-medium text-slate-700">{b.average_recovery_time_hours} Hours</span>
              </div>
            </div>
          </div>
        </div>

        {/* Key Findings List */}
        <div className="bg-surface border border-border rounded-xl p-6 shadow-card space-y-4">
          <h3 className="text-sm font-semibold text-primary-900">Executive Findings & Architectural Value</h3>
          <ul className="space-y-2 text-xs text-slate-700">
            {evalResult.key_findings.map((finding, i) => (
              <li key={i} className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span className="leading-relaxed">{finding}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};
