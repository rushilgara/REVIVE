import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  ShieldCheck,
  Save,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Sliders,
  Lock,
} from 'lucide-react';

import { api } from '../api/client';
import { Header } from '../layouts/Header';
import { PolicyConfig } from '../types';
import { formatINR, rupeesToMinor, minorToRupees } from '../utils/money';

export const PoliciesPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState<Partial<PolicyConfig>>({});
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const { data: policy, isLoading, refetch } = useQuery({
    queryKey: ['policy'],
    queryFn: () => api.getPolicies(),
  });

  useEffect(() => {
    if (policy) {
      setFormData(policy);
    }
  }, [policy]);

  const saveMutation = useMutation({
    mutationFn: (updated: Partial<PolicyConfig>) => api.updatePolicies(updated),
    onSuccess: (saved) => {
      setFormData(saved);
      setStatusMessage('Merchant policy guardrails updated successfully.');
      queryClient.invalidateQueries({ queryKey: ['policy'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
    onError: (err: any) => {
      setStatusMessage(`Error saving policy: ${err.message}`);
    },
  });

  const handleToggle = (key: keyof PolicyConfig) => {
    setFormData((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const handleChange = (key: keyof PolicyConfig, value: any) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
  };

  if (isLoading) {
    return (
      <div className="flex flex-col flex-1">
        <Header title="Merchant Policies" subtitle="Configurable deterministic guardrails" />
        <div className="p-8 space-y-4">
          <div className="h-64 bg-surface rounded-xl border border-border animate-pulse" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col flex-1">
      <Header
        title="Merchant Policies"
        subtitle="Configure deterministic safety boundaries, channel permissions, and human approval thresholds"
      />

      {statusMessage && (
        <div className="bg-slate-900 text-white px-8 py-2.5 text-xs flex items-center justify-between">
          <span className="flex items-center gap-2">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            {statusMessage}
          </span>
          <button onClick={() => setStatusMessage(null)} className="text-slate-400 hover:text-white">
            ✕
          </button>
        </div>
      )}

      <div className="p-8 space-y-8 max-w-5xl">
        {/* Guardrails Card */}
        <div className="bg-surface border border-border rounded-xl p-6 shadow-card space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-primary-900">Core Operational Guardrails</h3>
              <p className="text-xs text-slate-500">
                Safety thresholds enforced deterministically prior to executing any AI-proposed intervention.
              </p>
            </div>
            <ShieldCheck className="w-5 h-5 text-emerald-600" />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-2">
            {/* Approval Threshold */}
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold text-slate-700">
                Human Approval Threshold (₹ INR)
              </label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-xs font-bold text-slate-400">₹</span>
                <input
                  type="number"
                  value={formData.approval_threshold_minor !== undefined ? minorToRupees(formData.approval_threshold_minor) : 50000}
                  onChange={(e) => handleChange('approval_threshold_minor', rupeesToMinor(Number(e.target.value)))}
                  className="w-full pl-7 pr-3 py-2 text-xs bg-slate-50 border border-border rounded-lg text-primary-900 font-semibold focus:outline-none focus:border-primary-900"
                />
              </div>
              <p className="text-[11px] text-slate-500">
                Any recovery action exceeding this value triggers PENDING_APPROVAL status.
              </p>
            </div>

            {/* Cooldown Hours */}
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold text-slate-700">
                Intervention Cooldown Window (Hours)
              </label>
              <input
                type="number"
                min={0}
                max={72}
                value={formData.cooldown_hours || 12}
                onChange={(e) => handleChange('cooldown_hours', Number(e.target.value))}
                className="w-full px-3 py-2 text-xs bg-slate-50 border border-border rounded-lg text-primary-900 font-semibold focus:outline-none focus:border-primary-900"
              />
              <p className="text-[11px] text-slate-500">
                Minimum duration required between automated customer touchpoints.
              </p>
            </div>

            {/* Max Retries */}
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold text-slate-700">
                Maximum Automated Card Retries
              </label>
              <input
                type="number"
                min={1}
                max={5}
                value={formData.max_retry_attempts || 3}
                onChange={(e) => handleChange('max_retry_attempts', Number(e.target.value))}
                className="w-full px-3 py-2 text-xs bg-slate-50 border border-border rounded-lg text-primary-900 font-semibold focus:outline-none focus:border-primary-900"
              />
              <p className="text-[11px] text-slate-500">
                Prevents issuer blocking and protects customer relationships.
              </p>
            </div>

            {/* Max Contacts */}
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold text-slate-700">
                Maximum Outbound Contacts (Links/Messages)
              </label>
              <input
                type="number"
                min={1}
                max={10}
                value={formData.max_contact_attempts || 4}
                onChange={(e) => handleChange('max_contact_attempts', Number(e.target.value))}
                className="w-full px-3 py-2 text-xs bg-slate-50 border border-border rounded-lg text-primary-900 font-semibold focus:outline-none focus:border-primary-900"
              />
              <p className="text-[11px] text-slate-500">
                Hard ceiling on customer notifications to prevent spam fatigue.
              </p>
            </div>
          </div>
        </div>

        {/* Channel Permissions Card */}
        <div className="bg-surface border border-border rounded-xl p-6 shadow-card space-y-4">
          <h3 className="text-sm font-semibold text-primary-900">Allowed Intervention Channels</h3>
          <p className="text-xs text-slate-500">
            Control which communication rails the autonomous agent is authorized to deploy.
          </p>

          <div className="divide-y divide-border/60">
            <div className="py-3 flex items-center justify-between">
              <div>
                <span className="text-xs font-medium text-primary-900">Razorpay Payment Links</span>
                <p className="text-[11px] text-slate-500">Direct payment URLs supporting cards, UPI, and netbanking</p>
              </div>
              <input
                type="checkbox"
                checked={formData.allow_payment_links ?? true}
                onChange={() => handleToggle('allow_payment_links')}
                className="w-4 h-4 text-primary-900 rounded focus:ring-0 cursor-pointer"
              />
            </div>

            <div className="py-3 flex items-center justify-between">
              <div>
                <span className="text-xs font-medium text-primary-900">WhatsApp Business API</span>
                <p className="text-[11px] text-slate-500">Interactive conversational recovery prompts</p>
              </div>
              <input
                type="checkbox"
                checked={formData.allow_whatsapp ?? true}
                onChange={() => handleToggle('allow_whatsapp')}
                className="w-4 h-4 text-primary-900 rounded focus:ring-0 cursor-pointer"
              />
            </div>

            <div className="py-3 flex items-center justify-between">
              <div>
                <span className="text-xs font-medium text-primary-900">SMS Notification</span>
                <p className="text-[11px] text-slate-500">Direct transactional text alerts</p>
              </div>
              <input
                type="checkbox"
                checked={formData.allow_sms ?? true}
                onChange={() => handleToggle('allow_sms')}
                className="w-4 h-4 text-primary-900 rounded focus:ring-0 cursor-pointer"
              />
            </div>

            <div className="py-3 flex items-center justify-between">
              <div>
                <span className="text-xs font-medium text-primary-900">Email Recovery Notifications</span>
                <p className="text-[11px] text-slate-500">Personalized checkout & dunning emails</p>
              </div>
              <input
                type="checkbox"
                checked={formData.allow_email ?? true}
                onChange={() => handleToggle('allow_email')}
                className="w-4 h-4 text-primary-900 rounded focus:ring-0 cursor-pointer"
              />
            </div>
          </div>

          <div className="pt-4 flex justify-end">
            <button
              onClick={() => saveMutation.mutate(formData)}
              disabled={saveMutation.isPending}
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-primary-900 hover:bg-primary-800 text-white rounded-lg text-xs font-semibold shadow-subtle transition-fintech disabled:opacity-50"
            >
              <Save className="w-4 h-4" />
              <span>{saveMutation.isPending ? 'Saving Policies...' : 'Save Policy Changes'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
