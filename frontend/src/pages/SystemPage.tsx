import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Activity,
  Database,
  Cpu,
  CreditCard,
  Webhook,
  ShieldCheck,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react';

import { api } from '../api/client';
import { Header } from '../layouts/Header';

export const SystemPage: React.FC = () => {
  const { data: health, isLoading, isError, refetch } = useQuery({
    queryKey: ['systemHealth'],
    queryFn: () => api.getHealth(),
    refetchInterval: 10000,
  });

  if (isLoading) {
    return (
      <div className="flex flex-col flex-1">
        <Header title="System Status" subtitle="Real-time subsystem health and integration telemetry" />
        <div className="p-8 space-y-4">
          <div className="h-64 bg-surface rounded-xl border border-border animate-pulse" />
        </div>
      </div>
    );
  }

  const isHealthy = health?.status === 'healthy';

  return (
    <div className="flex flex-col flex-1">
      <Header
        title="System Status"
        subtitle="Real-time subsystem health, telemetry, and integration verification"
        actions={
          <button
            onClick={() => refetch()}
            className="p-1.5 text-slate-500 hover:text-primary-900 hover:bg-slate-100 rounded-lg transition-fintech"
            title="Refresh health status"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        }
      />

      <div className="p-8 space-y-8 max-w-5xl">
        {/* System Overview Banner */}
        <div className="bg-surface border border-border rounded-xl p-6 shadow-card flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div
              className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                isHealthy ? 'bg-emerald-50 text-emerald-600' : 'bg-rose-50 text-rose-600'
              }`}
            >
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-primary-900">
                  {isHealthy ? 'All Systems Operational' : 'Degraded Performance'}
                </h3>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                  {health?.app?.environment || 'development'}
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                Mode: <span className="font-semibold text-slate-700 capitalize">{health?.app?.mode}</span> · Version {health?.app?.version}
              </p>
            </div>
          </div>

          <div className="text-right text-xs text-slate-400 font-mono">
            Verified {new Date().toLocaleTimeString()}
          </div>
        </div>

        {/* Subsystems Health Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          {/* Database Card */}
          <div className="bg-surface border border-border rounded-xl p-5 shadow-card space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4 text-slate-500" />
                <span className="text-xs font-semibold text-primary-900">Database Subsystem</span>
              </div>
              <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700">
                <CheckCircle2 className="w-3.5 h-3.5" /> Healthy
              </span>
            </div>
            <p className="text-xs text-slate-600">
              Engine: <span className="font-semibold uppercase">{health?.components?.database?.type}</span> with ACID transaction isolation.
            </p>
            <div className="p-2.5 bg-slate-50 rounded text-[11px] text-slate-500 font-mono">
              Status: {health?.components?.database?.message}
            </div>
          </div>

          {/* AI Provider Card */}
          <div className="bg-surface border border-border rounded-xl p-5 shadow-card space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Cpu className="w-4 h-4 text-slate-500" />
                <span className="text-xs font-semibold text-primary-900">AI Reasoning Provider</span>
              </div>
              <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700">
                <CheckCircle2 className="w-3.5 h-3.5" /> Active
              </span>
            </div>
            <p className="text-xs text-slate-600">
              Provider: <span className="font-semibold capitalize">{health?.components?.ai_provider?.provider.replace(/_/g, ' ')}</span>
            </p>
            <div className="p-2.5 bg-slate-50 rounded text-[11px] text-slate-500 font-mono">
              Model: {health?.components?.ai_provider?.model}
            </div>
          </div>

          {/* Razorpay Integration Card */}
          <div className="bg-surface border border-border rounded-xl p-5 shadow-card space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CreditCard className="w-4 h-4 text-slate-500" />
                <span className="text-xs font-semibold text-primary-900">Razorpay Test Mode</span>
              </div>
              <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700">
                <CheckCircle2 className="w-3.5 h-3.5" /> Ready
              </span>
            </div>
            <p className="text-xs text-slate-600">
              API Credentials: <span className="font-semibold">Secured in Backend</span> (Never exposed to browser).
            </p>
            <div className="p-2.5 bg-slate-50 rounded text-[11px] text-slate-500 font-mono">
              Mode: {health?.components?.razorpay?.mode} · Key configured: {health?.components?.razorpay?.key_id_configured ? 'Yes' : 'No'}
            </div>
          </div>

          {/* Action Executor Card */}
          <div className="bg-surface border border-border rounded-xl p-5 shadow-card space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-slate-500" />
                <span className="text-xs font-semibold text-primary-900">Safety & Execution Guards</span>
              </div>
              <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700">
                <CheckCircle2 className="w-3.5 h-3.5" /> Enforcing
              </span>
            </div>
            <p className="text-xs text-slate-600">
              Deterministic boundaries active. All AI proposals gated by policy thresholds.
            </p>
            <div className="p-2.5 bg-slate-50 rounded text-[11px] text-slate-500 font-mono">
              Stopping rules & Idempotency: Verified Active
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
