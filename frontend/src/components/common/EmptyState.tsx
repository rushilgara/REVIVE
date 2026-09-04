import React from 'react';

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  action,
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center bg-surface border border-dashed border-border rounded-xl">
      {icon && <div className="mb-4 text-slate-400 p-3 bg-slate-50 rounded-full">{icon}</div>}
      <h3 className="text-sm font-semibold text-primary-900 mb-1">{title}</h3>
      <p className="text-xs text-slate-500 max-w-sm mb-4 leading-relaxed">{description}</p>
      {action && (
        <button
          onClick={action.onClick}
          className="inline-flex items-center justify-center px-4 py-2 text-xs font-medium text-white bg-primary-900 hover:bg-primary-800 rounded-lg transition-fintech shadow-subtle"
        >
          {action.label}
        </button>
      )}
    </div>
  );
};
