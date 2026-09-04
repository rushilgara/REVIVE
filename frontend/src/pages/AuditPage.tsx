import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { History, RefreshCw, Search, Code, Eye, X } from 'lucide-react';

import { api } from '../api/client';
import { Header } from '../layouts/Header';
import { TableRowSkeleton } from '../components/common/LoadingSkeleton';

export const AuditPage: React.FC = () => {
  const [searchCaseId, setSearchCaseId] = useState<string>('');
  const [selectedEvent, setSelectedEvent] = useState<any | null>(null);

  const { data: events = [], isLoading, refetch } = useQuery({
    queryKey: ['auditEvents', searchCaseId],
    queryFn: () => api.getAuditEvents(searchCaseId || undefined, 100),
  });

  return (
    <div className="flex flex-col flex-1">
      <Header
        title="Audit Trail"
        subtitle="Immutable ledger of decisions, policy checks, executions, and outcome verifications"
        actions={
          <button
            onClick={() => refetch()}
            className="p-1.5 text-slate-500 hover:text-primary-900 hover:bg-slate-100 rounded-lg transition-fintech"
            title="Refresh audit"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        }
      />

      <div className="p-8 space-y-6 max-w-7xl">
        {/* Search by Case ID */}
        <div className="bg-surface p-4 rounded-xl border border-border shadow-card flex items-center justify-between gap-4">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Filter by Recovery Case ID..."
              value={searchCaseId}
              onChange={(e) => setSearchCaseId(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-border rounded-lg text-primary-900 focus:outline-none focus:border-primary-900"
            />
          </div>
          <span className="text-xs text-slate-500 font-mono">
            {events.length} immutable events recorded
          </span>
        </div>

        {/* Audit Table */}
        <div className="bg-surface border border-border rounded-xl shadow-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-border bg-slate-50/70 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4">Event Type</th>
                  <th className="py-3 px-4">Case ID</th>
                  <th className="py-3 px-4">Actor</th>
                  <th className="py-3 px-4">Description</th>
                  <th className="py-3 px-4 text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60 text-xs">
                {isLoading ? (
                  Array.from({ length: 8 }).map((_, i) => <TableRowSkeleton key={i} cols={6} />)
                ) : events.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-12 text-center text-slate-500 text-xs">
                      No audit events matching criteria.
                    </td>
                  </tr>
                ) : (
                  events.map((e) => (
                    <tr key={e.id} className="hover:bg-slate-50/60 transition-fintech">
                      <td className="py-3.5 px-4 font-mono text-[11px] text-slate-500 whitespace-nowrap">
                        {new Date(e.created_at).toLocaleString()}
                      </td>
                      <td className="py-3.5 px-4 font-semibold text-primary-900">
                        <span className="px-2 py-0.5 rounded-full bg-slate-100 text-[11px] text-slate-800 border border-slate-200">
                          {e.event_type.replace(/_/g, ' ')}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 font-mono text-[11px] text-slate-600">
                        {e.recovery_case_id ? e.recovery_case_id.slice(0, 8) : 'SYSTEM'}
                      </td>
                      <td className="py-3.5 px-4 font-medium text-slate-700">
                        {e.actor}
                      </td>
                      <td className="py-3.5 px-4 text-slate-700 max-w-md truncate">
                        {e.description}
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <button
                          onClick={() => setSelectedEvent(e)}
                          className="p-1 text-slate-400 hover:text-primary-900 hover:bg-slate-100 rounded transition-fintech"
                          title="View JSON metadata"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Metadata Modal */}
        {selectedEvent && (
          <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
            <div className="bg-surface border border-border rounded-xl p-6 max-w-xl w-full shadow-elevated space-y-4">
              <div className="flex items-center justify-between border-b border-border pb-3">
                <div>
                  <h3 className="text-sm font-semibold text-primary-900">
                    {selectedEvent.event_type.replace(/_/g, ' ')}
                  </h3>
                  <span className="text-[11px] font-mono text-slate-500">
                    Correlation ID: {selectedEvent.correlation_id}
                  </span>
                </div>
                <button
                  onClick={() => setSelectedEvent(null)}
                  className="p-1 text-slate-400 hover:text-primary-900 rounded"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="space-y-2">
                <span className="text-xs font-semibold text-slate-700">Description</span>
                <p className="text-xs text-slate-600 p-2.5 bg-slate-50 rounded border border-slate-200">
                  {selectedEvent.description}
                </p>
              </div>

              <div className="space-y-2">
                <span className="text-xs font-semibold text-slate-700">Structured Payload Metadata</span>
                <pre className="text-[11px] font-mono p-3 bg-slate-900 text-slate-100 rounded-lg overflow-x-auto max-h-60">
                  {JSON.stringify(selectedEvent.metadata_payload, null, 2)}
                </pre>
              </div>

              <div className="flex justify-end pt-2">
                <button
                  onClick={() => setSelectedEvent(null)}
                  className="px-4 py-1.5 bg-primary-900 text-white rounded-lg text-xs font-medium"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
