import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, PlayCircle, Activity } from 'lucide-react';

interface HeaderProps {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
}

export const Header: React.FC<HeaderProps> = ({ title, subtitle, actions }) => {
  return (
    <header className="h-16 border-b border-border bg-surface px-8 flex items-center justify-between sticky top-0 z-10">
      <div>
        <h1 className="text-base font-semibold tracking-tight text-primary-900">{title}</h1>
        {subtitle && <p className="text-xs text-slate-500">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-3">
        {/* Environment Badge */}
        <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
          <span>Simulation Active</span>
        </div>

        {/* Quick Demo CTA */}
        <Link
          to="/demo"
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-primary-900 bg-slate-100 hover:bg-slate-200/80 transition-fintech border border-slate-200"
        >
          <PlayCircle className="w-3.5 h-3.5 text-emerald-600" />
          <span>Interactive Demo</span>
        </Link>

        {actions}
      </div>
    </header>
  );
};
