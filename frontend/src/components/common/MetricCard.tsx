import React from 'react';

interface MetricCardProps {
  label: string;
  value: string | number;
  subtext?: string;
  trend?: {
    value: string;
    positive?: boolean;
  };
  icon?: React.ReactNode;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  subtext,
  trend,
  icon,
}) => {
  return (
    <div className="bg-surface border border-border rounded-xl p-5 shadow-card hover:border-slate-300 transition-fintech">
      <div className="flex items-center justify-between text-primary-500 mb-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">{label}</span>
        {icon && <div className="text-slate-400">{icon}</div>}
      </div>
      <div className="flex items-baseline gap-2 mb-1">
        <span className="text-2xl font-bold tracking-tight text-primary-900">{value}</span>
        {trend && (
          <span
            className={`text-xs font-medium ${
              trend.positive ? 'text-emerald-700' : 'text-slate-500'
            }`}
          >
            {trend.value}
          </span>
        )}
      </div>
      {subtext && <p className="text-xs text-slate-500 leading-relaxed">{subtext}</p>}
    </div>
  );
};
