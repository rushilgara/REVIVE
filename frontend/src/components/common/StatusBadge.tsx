import React from 'react';
import { CaseStatus } from '../../types';

interface StatusBadgeProps {
  status: CaseStatus | string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const normalized = status.toUpperCase();

  let colorClasses = 'bg-slate-100 text-slate-700 border-slate-200';
  let dotColor = 'bg-slate-400';

  switch (normalized) {
    case 'RECOVERED':
      colorClasses = 'bg-emerald-50 text-emerald-800 border-emerald-200';
      dotColor = 'bg-emerald-500';
      break;
    case 'PENDING_APPROVAL':
      colorClasses = 'bg-amber-50 text-amber-800 border-amber-200';
      dotColor = 'bg-amber-500';
      break;
    case 'EXECUTING':
    case 'READY_FOR_ACTION':
    case 'DIAGNOSING':
      colorClasses = 'bg-blue-50 text-blue-800 border-blue-200';
      dotColor = 'bg-blue-500 animate-pulse';
      break;
    case 'STOPPED':
      colorClasses = 'bg-slate-100 text-slate-600 border-slate-200';
      dotColor = 'bg-slate-400';
      break;
    case 'FAILED':
    case 'ESCALATED':
      colorClasses = 'bg-rose-50 text-rose-800 border-rose-200';
      dotColor = 'bg-rose-500';
      break;
    default:
      colorClasses = 'bg-slate-50 text-slate-700 border-slate-200';
      dotColor = 'bg-slate-400';
  }

  const padding = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs font-medium';

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border ${padding} ${colorClasses} tracking-tight`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${dotColor}`} />
      {normalized.replace(/_/g, ' ')}
    </span>
  );
};
