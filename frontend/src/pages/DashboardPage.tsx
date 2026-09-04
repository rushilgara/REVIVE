import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  Clock,
  ShieldCheck,
  ArrowUpRight,
  ArrowRight,
  Activity,
  PlayCircle,
  RefreshCw,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
} from 'recharts';

import { api } from '../api/client';
import { Header } from '../layouts/Header';
import { MetricCard } from '../components/common/MetricCard';
import { formatINR, formatPercentage } from '../utils/money';
import { Skeleton } from '../components/common/LoadingSkeleton';

export const DashboardPage: React.FC = () => {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => api.getDashboard(),
    refetchInterval: 10000,
  });

  if (isLoading) {
    return (
      <div className="flex flex-col flex-1">
        <Header title="Revenue Recovery" subtitle="Operational metrics & autonomous intervention performance" />
        <div className="p-8 space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-28 bg-surface rounded-xl border border-border p-4 animate-pulse" />
            ))}
          </div>
          <div className="h-80 bg-surface rounded-xl border border-border animate-pulse" />
        </div>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="flex flex-col flex-1">
        <Header title="Revenue Recovery" />
        <div className="p-8">
          <div className="bg-rose-50 border border-rose-200 rounded-xl p-6 text-center">
            <AlertTriangle className="w-8 h-8 text-rose-600 mx-auto mb-2" />
            <h3 className="text-sm font-semibold text-rose-900">Failed to load recovery dashboard</h3>
            <p className="text-xs text-rose-700 mt-1">Ensure backend server is running on port 8000.</p>
            <button
              onClick={() => refetch()}
              className="mt-4 px-3 py-1.5 bg-rose-600 text-white rounded-lg text-xs font-medium hover:bg-rose-700"
            >
              Retry Connection
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Format charts
  const timelineData = data.recovery_timeline.map((pt) => ({
    date: pt.date,
    atRisk: pt.revenue_at_risk_minor / 100,
    recovered: pt.revenue_recovered_minor / 100,
  }));

  return (
    <div className="flex flex-col flex-1">
      <Header
        title="Revenue Recovery"
        subtitle="Operational metrics & autonomous intervention performance"
        actions={
          <button
            onClick={() => refetch()}
            className="p-1.5 text-slate-500 hover:text-primary-900 hover:bg-slate-100 rounded-lg transition-fintech"
            title="Refresh metrics"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        }
      />

      <div className="p-8 space-y-8 max-w-7xl">
        {/* Top Operational Metrics */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <MetricCard
            label="Revenue at Risk"
            value={formatINR(data.revenue_at_risk_minor)}
            subtext="Total unresolved transaction loss"
            icon={<AlertTriangle className="w-4 h-4 text-slate-400" />}
          />
          <MetricCard
            label="Revenue Recovered"
            value={formatINR(data.revenue_recovered_minor)}
            subtext="Verified settled revenue"
            trend={{ value: `${formatPercentage(data.recovery_rate_pct)} rate`, positive: true }}
            icon={<CheckCircle2 className="w-4 h-4 text-emerald-500" />}
          />
          <MetricCard
            label="Recovery Rate"
            value={formatPercentage(data.recovery_rate_pct)}
            subtext={`${data.recovered_cases_count} cases recovered`}
            icon={<TrendingUp className="w-4 h-4 text-blue-500" />}
          />
          <MetricCard
            label="Active Cases"
            value={data.active_cases_count}
            subtext="Autonomous recovery in progress"
            icon={<Activity className="w-4 h-4 text-slate-400" />}
          />
          <Link to="/approvals" className="block">
            <div className={`rounded-xl p-5 border transition-fintech shadow-card ${
              data.pending_approvals_count > 0
                ? 'bg-amber-50/60 border-amber-300 hover:border-amber-400'
                : 'bg-surface border-border hover:border-slate-300'
            }`}>
              <div className="flex items-center justify-between text-slate-500 mb-2">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-600">Pending Approval</span>
                <Clock className="w-4 h-4 text-amber-600" />
              </div>
              <div className="flex items-baseline gap-2 mb-1">
                <span className="text-2xl font-bold tracking-tight text-primary-900">{data.pending_approvals_count}</span>
                {data.pending_approvals_count > 0 && (
                  <span className="text-xs font-semibold text-amber-700">Requires review</span>
                )}
              </div>
              <p className="text-xs text-slate-500">High-value policy threshold guard</p>
            </div>
          </Link>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recovery Timeline (Area Chart) */}
          <div className="lg:col-span-2 bg-surface border border-border rounded-xl p-6 shadow-card">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-sm font-semibold text-primary-900">Recovery Trend (7 Days)</h3>
                <p className="text-xs text-slate-500">Revenue at risk vs. verified revenue recovered</p>
              </div>
              <div className="flex items-center gap-4 text-xs">
                <div className="flex items-center gap-1.5 text-slate-600">
                  <span className="w-2.5 h-2.5 rounded-full bg-slate-300" />
                  <span>At Risk</span>
                </div>
                <div className="flex items-center gap-1.5 text-slate-800 font-medium">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                  <span>Recovered</span>
                </div>
              </div>
            </div>

            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={timelineData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#94A3B8" stopOpacity={0.15} />
                      <stop offset="95%" stopColor="#94A3B8" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorRec" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10B981" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="date" stroke="#94A3B8" fontSize={11} tickLine={false} />
                  <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} tickFormatter={(v) => `₹${v / 1000}k`} />
                  <Tooltip
                    formatter={(val: number) => [`₹${val.toLocaleString('en-IN')}`, '']}
                    contentStyle={{ backgroundColor: '#FFFFFF', borderColor: '#E2E8F0', borderRadius: '8px', fontSize: '12px' }}
                  />
                  <Area type="monotone" dataKey="atRisk" stroke="#94A3B8" strokeWidth={1.5} fillOpacity={1} fill="url(#colorRisk)" name="At Risk" />
                  <Area type="monotone" dataKey="recovered" stroke="#059669" strokeWidth={2} fillOpacity={1} fill="url(#colorRec)" name="Recovered" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Root Cause Telemetry */}
          <div className="bg-surface border border-border rounded-xl p-6 shadow-card flex flex-col justify-between">
            <div>
              <h3 className="text-sm font-semibold text-primary-900 mb-1">Diagnostic Root Cause</h3>
              <p className="text-xs text-slate-500 mb-5">AI classified failure categories</p>
              
              <div className="space-y-3.5">
                {data.root_cause_breakdown.map((item) => {
                  const pct = data.revenue_at_risk_minor > 0
                    ? Math.round((item.revenue_minor / data.revenue_at_risk_minor) * 100)
                    : 0;
                  return (
                    <div key={item.name} className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="font-medium text-slate-700 truncate max-w-[170px]">
                          {item.name.replace(/_/g, ' ')}
                        </span>
                        <span className="text-slate-500">{item.count} cases</span>
                      </div>
                      <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                        <div
                          className="bg-primary-900 h-1.5 rounded-full transition-all duration-500"
                          style={{ width: `${Math.max(8, pct)}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="pt-4 mt-4 border-t border-border/60 flex items-center justify-between text-xs text-slate-500">
              <span>Policy Guard Status</span>
              <span className="inline-flex items-center gap-1 text-emerald-700 font-medium">
                <ShieldCheck className="w-3.5 h-3.5" /> Active
              </span>
            </div>
          </div>
        </div>

        {/* Live Operational Feed & Quick Links */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Audit Feed */}
          <div className="lg:col-span-2 bg-surface border border-border rounded-xl p-6 shadow-card">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-semibold text-primary-900">Live Recovery Audit Ledger</h3>
                <p className="text-xs text-slate-500">Immutable chronological record of decisions and executions</p>
              </div>
              <Link to="/audit" className="text-xs font-medium text-primary-900 hover:text-primary-700 flex items-center gap-1">
                <span>View Full Trail</span>
                <ArrowRight className="w-3 h-3" />
              </Link>
            </div>

            <div className="divide-y divide-border/60">
              {data.recent_activity.map((event) => (
                <div key={event.id} className="py-3 flex items-start justify-between gap-4 text-xs">
                  <div className="flex items-start gap-2.5">
                    <span className="w-2 h-2 rounded-full bg-slate-400 mt-1.5 shrink-0" />
                    <div>
                      <span className="font-semibold text-primary-900">{event.event_type.replace(/_/g, ' ')}</span>
                      <p className="text-slate-600 mt-0.5">{event.description}</p>
                    </div>
                  </div>
                  <div className="text-right shrink-0 text-slate-400 font-mono text-[11px]">
                    {new Date(event.created_at).toLocaleTimeString()}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Guided Demo & Evaluation Links */}
          <div className="space-y-4">
            <div className="bg-surface border border-border rounded-xl p-6 shadow-card">
              <h3 className="text-sm font-semibold text-primary-900 mb-1">One-Click Guided Demo</h3>
              <p className="text-xs text-slate-500 mb-4 leading-relaxed">
                Step through the 3 canonical Buildathon scenarios: retail payment link, ₹87k approval gate, and safety disconnect.
              </p>
              <Link
                to="/demo"
                className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-primary-900 text-white rounded-lg text-xs font-semibold hover:bg-primary-800 transition-fintech shadow-subtle"
              >
                <PlayCircle className="w-4 h-4" />
                <span>Launch Interactive Demo</span>
              </Link>
            </div>

            <div className="bg-surface border border-border rounded-xl p-6 shadow-card">
              <h3 className="text-sm font-semibold text-primary-900 mb-1">REVIVE vs Baseline Benchmark</h3>
              <p className="text-xs text-slate-500 mb-4 leading-relaxed">
                Scientifically compare autonomous context-aware recovery against naive brute-force retry on an identical cloned dataset.
              </p>
              <Link
                to="/evaluation"
                className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-primary-900 rounded-lg text-xs font-semibold transition-fintech border border-slate-200"
              >
                <span>View Evaluation Metrics</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
