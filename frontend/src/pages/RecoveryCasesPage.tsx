import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  Filter,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  ArrowUpDown,
  ExternalLink,
} from 'lucide-react';

import { api } from '../api/client';
import { Header } from '../layouts/Header';
import { StatusBadge } from '../components/common/StatusBadge';
import { formatINR } from '../utils/money';
import { TableRowSkeleton } from '../components/common/LoadingSkeleton';
import { EmptyState } from '../components/common/EmptyState';
import { CaseStatus, RiskType } from '../types';

export const RecoveryCasesPage: React.FC = () => {
  const navigate = useNavigate();
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [riskFilter, setRiskFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [minScore, setMinScore] = useState<number | undefined>(undefined);
  const [offset, setOffset] = useState<number>(0);
  const limit = 20;

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['cases', statusFilter, riskFilter, searchQuery, minScore, offset],
    queryFn: () =>
      api.getRecoveryCases({
        status: statusFilter || undefined,
        risk_type: riskFilter || undefined,
        search: searchQuery || undefined,
        min_score: minScore,
        limit,
        offset,
      }),
  });

  const cases = data?.items || [];

  return (
    <div className="flex flex-col flex-1">
      <Header
        title="Recovery Cases"
        subtitle="Manage and inspect autonomous revenue recovery cases"
        actions={
          <button
            onClick={() => refetch()}
            className="p-1.5 text-slate-500 hover:text-primary-900 hover:bg-slate-100 rounded-lg transition-fintech"
            title="Refresh cases"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        }
      />

      <div className="p-8 space-y-6 max-w-7xl">
        {/* Filter & Search Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-surface p-4 rounded-xl border border-border shadow-card">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search customer, case ID..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setOffset(0);
              }}
              className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-border rounded-lg text-primary-900 focus:outline-none focus:border-primary-900 transition-fintech"
            />
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setOffset(0);
              }}
              className="px-3 py-1.5 text-xs bg-slate-50 border border-border rounded-lg text-primary-900 focus:outline-none focus:border-primary-900"
            >
              <option value="">All Statuses</option>
              <option value="OPEN">Open</option>
              <option value="DIAGNOSING">Diagnosing</option>
              <option value="READY_FOR_ACTION">Ready for Action</option>
              <option value="PENDING_APPROVAL">Pending Approval</option>
              <option value="EXECUTING">Executing</option>
              <option value="RECOVERED">Recovered</option>
              <option value="STOPPED">Stopped</option>
              <option value="ESCALATED">Escalated</option>
            </select>

            {/* Risk Type Filter */}
            <select
              value={riskFilter}
              onChange={(e) => {
                setRiskFilter(e.target.value);
                setOffset(0);
              }}
              className="px-3 py-1.5 text-xs bg-slate-50 border border-border rounded-lg text-primary-900 focus:outline-none focus:border-primary-900"
            >
              <option value="">All Risk Types</option>
              <option value="FAILED_PAYMENT">Failed Payment</option>
              <option value="CHECKOUT_ABANDONMENT">Checkout Abandonment</option>
              <option value="SUBSCRIPTION_FAILURE">Subscription Failure</option>
              <option value="OVERDUE_RECEIVABLE">Overdue Receivable</option>
            </select>

            {/* Clear filters button if active */}
            {(statusFilter || riskFilter || searchQuery) && (
              <button
                onClick={() => {
                  setStatusFilter('');
                  setRiskFilter('');
                  setSearchQuery('');
                  setOffset(0);
                }}
                className="text-xs text-slate-500 hover:text-primary-900 underline"
              >
                Clear
              </button>
            )}
          </div>
        </div>

        {/* Data Table */}
        <div className="bg-surface border border-border rounded-xl shadow-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-border bg-slate-50/70 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                  <th className="py-3 px-4">Case</th>
                  <th className="py-3 px-4">Customer</th>
                  <th className="py-3 px-4">Risk Type</th>
                  <th className="py-3 px-4">Amount</th>
                  <th className="py-3 px-4">Recoverability</th>
                  <th className="py-3 px-4">Recommendation</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60 text-xs">
                {isLoading ? (
                  Array.from({ length: 8 }).map((_, i) => <TableRowSkeleton key={i} cols={8} />)
                ) : cases.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="py-12">
                      <EmptyState
                        title="No recovery cases found"
                        description="Try adjusting your search criteria or run a simulation to generate cases."
                      />
                    </td>
                  </tr>
                ) : (
                  cases.map((c) => {
                    const scoreColor =
                      c.recoverability_score >= 80
                        ? 'text-emerald-700 bg-emerald-50 border-emerald-200'
                        : c.recoverability_score >= 50
                        ? 'text-blue-700 bg-blue-50 border-blue-200'
                        : 'text-amber-700 bg-amber-50 border-amber-200';

                    return (
                      <tr
                        key={c.id}
                        onClick={() => navigate(`/recovery/${c.id}`)}
                        className="hover:bg-slate-50/70 cursor-pointer transition-fintech group"
                      >
                        <td className="py-3.5 px-4 font-mono font-medium text-primary-900">
                          <span className="group-hover:underline flex items-center gap-1">
                            {c.id.slice(0, 8)}
                            <ExternalLink className="w-3 h-3 text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                          </span>
                        </td>
                        <td className="py-3.5 px-4">
                          <div className="font-medium text-primary-900 truncate max-w-[140px]">
                            {c.customer?.name || 'Customer'}
                          </div>
                          <div className="text-[11px] text-slate-500 truncate max-w-[140px]">
                            {c.customer?.email}
                          </div>
                        </td>
                        <td className="py-3.5 px-4 text-slate-700">
                          {c.risk_type.replace(/_/g, ' ')}
                        </td>
                        <td className="py-3.5 px-4 font-semibold text-primary-900">
                          {formatINR(c.revenue_at_risk_minor)}
                        </td>
                        <td className="py-3.5 px-4">
                          <span
                            className={`inline-flex items-center px-2 py-0.5 rounded-full border text-[11px] font-bold ${scoreColor}`}
                          >
                            {c.recoverability_score}/100
                          </span>
                        </td>
                        <td className="py-3.5 px-4 text-slate-700">
                          {c.recommended_action ? c.recommended_action.replace(/_/g, ' ') : '—'}
                        </td>
                        <td className="py-3.5 px-4">
                          <StatusBadge status={c.status} size="sm" />
                        </td>
                        <td className="py-3.5 px-4 text-right text-slate-500 font-mono text-[11px]">
                          {new Date(c.created_at).toLocaleDateString()}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="p-4 border-t border-border flex items-center justify-between text-xs text-slate-500 bg-slate-50/30">
            <span>Showing {cases.length} records</span>
            <div className="flex items-center gap-2">
              <button
                disabled={offset === 0}
                onClick={() => setOffset(Math.max(0, offset - limit))}
                className="p-1.5 rounded border border-border bg-white disabled:opacity-40 hover:bg-slate-50 transition-fintech"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
              </button>
              <button
                disabled={cases.length < limit}
                onClick={() => setOffset(offset + limit)}
                className="p-1.5 rounded border border-border bg-white disabled:opacity-40 hover:bg-slate-50 transition-fintech"
              >
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
