import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  RefreshCw,
  CheckCircle2,
  Cpu,
  BarChart3,
  ShieldAlert,
  History,
  Activity,
  PlayCircle,
} from 'lucide-react';

const NAV_ITEMS = [
  { label: 'Overview', path: '/', icon: LayoutDashboard },
  { label: 'Recovery Cases', path: '/recovery', icon: RefreshCw },
  { label: 'Approval Center', path: '/approvals', icon: CheckCircle2 },
  { label: 'Simulation', path: '/simulation', icon: Cpu },
  { label: 'Evaluation', path: '/evaluation', icon: BarChart3 },
  { label: 'Policies', path: '/policies', icon: ShieldAlert },
  { label: 'Audit Trail', path: '/audit', icon: History },
  { label: 'System Status', path: '/system', icon: Activity },
  { label: 'Guided Demo', path: '/demo', icon: PlayCircle, highlight: true },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 border-r border-border bg-surface flex flex-col justify-between h-screen sticky top-0 select-none">
      <div>
        {/* Brand Header */}
        <div className="h-16 flex items-center px-6 border-b border-border/80 gap-3">
          <div className="w-8 h-8 rounded-lg bg-primary-900 text-white flex items-center justify-center font-bold text-sm tracking-widest shadow-sm">
            R
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-semibold text-sm tracking-tight text-primary-900">REVIVE</span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.2 bg-slate-100 text-slate-600 rounded">
                v1.0
              </span>
            </div>
            <p className="text-[11px] text-slate-500 font-medium">Revenue Recovery Orchestration</p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="p-3 space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-medium transition-fintech ${
                    isActive
                      ? 'bg-primary-900 text-white shadow-subtle'
                      : item.highlight
                      ? 'text-primary-900 font-semibold bg-emerald-50/70 hover:bg-emerald-100/70'
                      : 'text-slate-600 hover:text-primary-900 hover:bg-slate-100/70'
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Merchant Details & Track Info */}
      <div className="p-4 border-t border-border/80 bg-slate-50/50">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[11px] font-medium text-slate-500">Merchant Account</span>
          <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-700">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
            Test Mode
          </span>
        </div>
        <p className="text-xs font-semibold text-primary-900 truncate">Acro Retail India</p>
        <p className="text-[10px] text-slate-500 truncate mt-0.5">Razorpay AI Buildathon — Track 03</p>
      </div>
    </aside>
  );
};
