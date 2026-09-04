import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AppLayout } from './layouts/AppLayout';

import { DashboardPage } from './pages/DashboardPage';
import { RecoveryCasesPage } from './pages/RecoveryCasesPage';
import { CaseDetailPage } from './pages/CaseDetailPage';
import { ApprovalsPage } from './pages/ApprovalsPage';
import { SimulationPage } from './pages/SimulationPage';
import { EvaluationPage } from './pages/EvaluationPage';
import { PoliciesPage } from './pages/PoliciesPage';
import { AuditPage } from './pages/AuditPage';
import { SystemPage } from './pages/SystemPage';
import { DemoPage } from './pages/DemoPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5000,
    },
  },
});

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<AppLayout />}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/recovery" element={<RecoveryCasesPage />} />
            <Route path="/recovery/:caseId" element={<CaseDetailPage />} />
            <Route path="/approvals" element={<ApprovalsPage />} />
            <Route path="/simulation" element={<SimulationPage />} />
            <Route path="/evaluation" element={<EvaluationPage />} />
            <Route path="/policies" element={<PoliciesPage />} />
            <Route path="/audit" element={<AuditPage />} />
            <Route path="/system" element={<SystemPage />} />
            <Route path="/demo" element={<DemoPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

export default App;
