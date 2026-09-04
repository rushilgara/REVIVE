import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Cpu,
  Play,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Sliders,
  Database,
  ArrowRight,
} from 'lucide-react';

import { api } from '../api/client';
import { Header } from '../layouts/Header';
import { formatINR, formatPercentage } from '../utils/money';
import { SimulationResult } from '../types';

export const SimulationPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [transactionCount, setTransactionCount] = useState<number>(1000);
  const [randomSeed, setRandomSeed] = useState<number>(42);
  const [scenarioPreset, setScenarioPreset] = useState<string>('all');
  const [result, setResult] = useState<SimulationResult | null>(null);

  const simMutation = useMutation({
    mutationFn: () =>
      api.runSimulation({
        transaction_count: transactionCount,
        random_seed: randomSeed,
        scenario_preset: scenarioPreset,
      }),
    onSuccess: (data) => {
      setResult(data);
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['cases'] });
    },
  });

  return (
    <div className="flex flex-col flex-1">
      <Header
        title="Simulation Console"
        subtitle="Generate and execute deterministic high-volume recovery scenarios"
      />

      <div className="p-8 space-y-8 max-w-7xl">
        {/* Simulation Configuration Panel */}
        <div className="bg-surface border border-border rounded-xl p-6 shadow-card">
          <div className="flex items-center gap-2 mb-4">
            <Sliders className="w-4 h-4 text-slate-500" />
            <h3 className="text-sm font-semibold text-primary-900">Simulation Configuration</h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1.5">
                Transaction Volume
              </label>
              <select
                value={transactionCount}
                onChange={(e) => setTransactionCount(Number(e.target.value))}
                className="w-full px-3 py-2 text-xs bg-slate-50 border border-border rounded-lg text-primary-900 focus:outline-none focus:border-primary-900"
              >
                <option value={100}>100 Transactions (Quick Test)</option>
                <option value={500}>500 Transactions</option>
                <option value={1000}>1,000 Transactions (Standard)</option>
                <option value={2500}>2,500 Transactions (High Volume)</option>
                <option value={5000}>5,000 Transactions (Stress Benchmark)</option>
              </select>
              <p className="text-[11px] text-slate-500 mt-1">Minimum requirement: 1,000+ cases.</p>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1.5">
                Deterministic Random Seed
              </label>
              <input
                type="number"
                value={randomSeed}
                onChange={(e) => setRandomSeed(Number(e.target.value))}
                className="w-full px-3 py-2 text-xs bg-slate-50 border border-border rounded-lg text-primary-900 focus:outline-none focus:border-primary-900"
              />
              <p className="text-[11px] text-slate-500 mt-1">Guarantees scientific reproducibility.</p>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1.5">
                Scenario Distribution Preset
              </label>
              <select
                value={scenarioPreset}
                onChange={(e) => setScenarioPreset(e.target.value)}
                className="w-full px-3 py-2 text-xs bg-slate-50 border border-border rounded-lg text-primary-900 focus:outline-none focus:border-primary-900"
              >
                <option value="all">All 16 Scenarios (Full Spectrum)</option>
                <option value="network_glitch">Network & Temporary Disruption</option>
                <option value="high_value">High-Value Commercial Cases</option>
                <option value="customer_issues">Balance & Card Expirations</option>
                <option value="limits">Safety Limit & Opt-Out Cutoffs</option>
              </select>
              <p className="text-[11px] text-slate-500 mt-1">Simulates realistic omnichannel conditions.</p>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-border flex items-center justify-between">
            <span className="text-xs text-slate-500">
              Generated records persist directly into the database with full audit trails.
            </span>
            <button
              onClick={() => simMutation.mutate()}
              disabled={simMutation.isPending}
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-primary-900 hover:bg-primary-800 text-white rounded-lg text-xs font-semibold shadow-subtle transition-fintech disabled:opacity-50"
            >
              {simMutation.isPending ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Generating {transactionCount} Transactions...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-white" />
                  <span>Execute Simulation</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Simulation Output Results */}
        {result && (
          <div className="bg-surface border border-border rounded-xl p-6 shadow-card space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                  Simulation Successful
                </span>
                <h3 className="text-sm font-semibold text-primary-900 mt-1.5">
                  Execution Report ({result.transaction_count} Transactions in {result.duration_ms}ms)
                </h3>
              </div>
              <span className="text-xs text-slate-500 font-mono">Seed: {result.random_seed}</span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="p-4 bg-slate-50 rounded-lg border border-slate-200/80">
                <span className="text-[11px] font-medium text-slate-500 uppercase">Revenue at Risk</span>
                <div className="text-lg font-bold text-primary-900 mt-1">
                  {formatINR(result.revenue_at_risk_minor)}
                </div>
              </div>
              <div className="p-4 bg-emerald-50/60 rounded-lg border border-emerald-200/80">
                <span className="text-[11px] font-medium text-emerald-800 uppercase">Recovered Revenue</span>
                <div className="text-lg font-bold text-emerald-900 mt-1">
                  {formatINR(result.revenue_recovered_minor)}
                </div>
              </div>
              <div className="p-4 bg-slate-50 rounded-lg border border-slate-200/80">
                <span className="text-[11px] font-medium text-slate-500 uppercase">Recovery Rate</span>
                <div className="text-lg font-bold text-primary-900 mt-1">
                  {formatPercentage(result.recovery_rate_pct)}
                </div>
              </div>
              <div className="p-4 bg-amber-50/60 rounded-lg border border-amber-200/80">
                <span className="text-[11px] font-medium text-amber-800 uppercase">Pending Approvals</span>
                <div className="text-lg font-bold text-amber-900 mt-1">
                  {result.pending_approval_cases} Cases
                </div>
              </div>
            </div>

            <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg text-xs space-y-2">
              <span className="font-semibold text-slate-700">16 Tested Scenarios:</span>
              <div className="flex flex-wrap gap-1.5">
                {result.scenarios_tested.map((s) => (
                  <span
                    key={s}
                    className="px-2 py-0.5 bg-white border border-slate-200 text-slate-700 rounded text-[10px]"
                  >
                    {s.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed italic">{result.summary_message}</p>
          </div>
        )}
      </div>
    </div>
  );
};
