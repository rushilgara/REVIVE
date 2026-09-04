import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  PlayCircle,
  CheckCircle2,
  AlertTriangle,
  ShieldAlert,
  ArrowRight,
  RefreshCw,
  ExternalLink,
  Zap,
} from 'lucide-react';

import { api } from '../api/client';
import { Header } from '../layouts/Header';
import { formatINR } from '../utils/money';

export const DemoPage: React.FC = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [activeScenario, setActiveScenario] = useState<'case-a' | 'case-b' | 'case-c' | null>(null);
  const [demoOutput, setDemoOutput] = useState<any | null>(null);

  const demoMutation = useMutation({
    mutationFn: (scenario: 'case-a' | 'case-b' | 'case-c') => {
      setActiveScenario(scenario);
      return api.runDemoScenario(scenario);
    },
    onSuccess: (data) => {
      setDemoOutput(data);
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['cases'] });
      queryClient.invalidateQueries({ queryKey: ['pendingApprovals'] });
    },
  });

  return (
    <div className="flex flex-col flex-1">
      <Header
        title="Interactive Demo Console"
        subtitle="One-click execution of the 3 canonical Buildathon evaluation narratives"
      />

      <div className="p-8 space-y-8 max-w-5xl">
        {/* Narrative Intro */}
        <div className="bg-surface border border-border rounded-xl p-6 shadow-card space-y-2">
          <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded border border-emerald-200">
            Buildathon Demo Script
          </span>
          <h2 className="text-lg font-bold text-primary-900">
            Autonomous Recovery & Financial Safety Demonstration
          </h2>
          <p className="text-xs text-slate-600 leading-relaxed max-w-3xl">
            Each scenario triggers real backend orchestration: signal detection, AI diagnosis, deterministic policy evaluation, action dispatch, and verified payment outcome recording.
          </p>
        </div>

        {/* 3 Interactive Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Scenario A Card */}
          <div className="bg-surface border border-border rounded-xl p-6 shadow-card hover:border-slate-300 transition-fintech flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Demo Case A</span>
                <span className="text-xs font-bold text-emerald-700 px-2 py-0.5 bg-emerald-50 rounded border border-emerald-200">
                  ₹4,999
                </span>
              </div>
              <h3 className="text-sm font-bold text-primary-900">Retail Payment Recovery</h3>
              <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                Transient bank failure on an established retail customer. REVIVE scores 98/100, generates a Razorpay payment link, verifies payment capture, and settles the case as RECOVERED.
              </p>
            </div>

            <button
              onClick={() => demoMutation.mutate('case-a')}
              disabled={demoMutation.isPending}
              className="w-full inline-flex items-center justify-center gap-1.5 py-2.5 bg-primary-900 hover:bg-primary-800 text-white rounded-lg text-xs font-semibold shadow-subtle transition-fintech disabled:opacity-50"
            >
              {demoMutation.isPending && activeScenario === 'case-a' ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Executing Loop...</span>
                </>
              ) : (
                <>
                  <PlayCircle className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Execute Case A</span>
                </>
              )}
            </button>
          </div>

          {/* Scenario B Card */}
          <div className="bg-surface border border-border rounded-xl p-6 shadow-card hover:border-slate-300 transition-fintech flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Demo Case B</span>
                <span className="text-xs font-bold text-amber-700 px-2 py-0.5 bg-amber-50 rounded border border-amber-200">
                  ₹87,000
                </span>
              </div>
              <h3 className="text-sm font-bold text-primary-900">High-Value Approval Gate</h3>
              <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                Commercial transaction exceeds the ₹50,000 policy threshold. REVIVE prohibits direct execution, transitions the case to PENDING_APPROVAL, and queues it in the Approval Center.
              </p>
            </div>

            <button
              onClick={() => demoMutation.mutate('case-b')}
              disabled={demoMutation.isPending}
              className="w-full inline-flex items-center justify-center gap-1.5 py-2.5 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-semibold shadow-subtle transition-fintech disabled:opacity-50"
            >
              {demoMutation.isPending && activeScenario === 'case-b' ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Enforcing Policy...</span>
                </>
              ) : (
                <>
                  <PlayCircle className="w-3.5 h-3.5" />
                  <span>Execute Case B</span>
                </>
              )}
            </button>
          </div>

          {/* Scenario C Card */}
          <div className="bg-surface border border-border rounded-xl p-6 shadow-card hover:border-slate-300 transition-fintech flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Demo Case C</span>
                <span className="text-xs font-bold text-rose-700 px-2 py-0.5 bg-rose-50 rounded border border-rose-200">
                  Safety Gate
                </span>
              </div>
              <h3 className="text-sm font-bold text-primary-900">Gateway Outage Safety</h3>
              <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                Execution gateway disconnects or fails. REVIVE guarantees zero false recovery claims, records execution failure in the audit log, and marks the case ESCALATED.
              </p>
            </div>

            <button
              onClick={() => demoMutation.mutate('case-c')}
              disabled={demoMutation.isPending}
              className="w-full inline-flex items-center justify-center gap-1.5 py-2.5 bg-slate-800 hover:bg-slate-900 text-white rounded-lg text-xs font-semibold shadow-subtle transition-fintech disabled:opacity-50"
            >
              {demoMutation.isPending && activeScenario === 'case-c' ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Testing Safety...</span>
                </>
              ) : (
                <>
                  <PlayCircle className="w-3.5 h-3.5 text-rose-400" />
                  <span>Execute Case C</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Live Execution Feedback Box */}
        {demoOutput && (
          <div className="bg-surface border border-border rounded-xl p-6 shadow-card space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <h3 className="text-sm font-semibold text-primary-900">{demoOutput.scenario} Result</h3>
              </div>
              <button
                onClick={() => navigate(`/recovery/${demoOutput.case_id}`)}
                className="inline-flex items-center gap-1 text-xs font-semibold text-primary-900 hover:underline"
              >
                <span>Inspect Full Case Detail</span>
                <ExternalLink className="w-3 h-3" />
              </button>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
              <div className="p-3 bg-slate-50 rounded border border-slate-200">
                <span className="text-slate-500 uppercase text-[10px] font-semibold">Case ID</span>
                <div className="font-mono font-medium text-slate-900 mt-1">{demoOutput.case_id.slice(0, 10)}...</div>
              </div>
              <div className="p-3 bg-slate-50 rounded border border-slate-200">
                <span className="text-slate-500 uppercase text-[10px] font-semibold">Amount</span>
                <div className="font-bold text-slate-900 mt-1">{formatINR(demoOutput.amount_minor)}</div>
              </div>
              <div className="p-3 bg-slate-50 rounded border border-slate-200">
                <span className="text-slate-500 uppercase text-[10px] font-semibold">Terminal State</span>
                <div className="font-bold text-primary-900 mt-1">{demoOutput.status}</div>
              </div>
              <div className="p-3 bg-slate-50 rounded border border-slate-200">
                <span className="text-slate-500 uppercase text-[10px] font-semibold">Recovery Verified</span>
                <div className={`font-bold mt-1 ${demoOutput.recovered ? 'text-emerald-700' : 'text-slate-500'}`}>
                  {demoOutput.recovered ? 'YES (Confirmed)' : 'NO (Protected)'}
                </div>
              </div>
            </div>

            <p className="text-xs text-slate-700 leading-relaxed p-3 bg-slate-50 rounded-lg border border-slate-200/80">
              {demoOutput.message}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
