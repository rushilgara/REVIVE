# REVIVE — Judge & Evaluation Interactive Demo Script

This document provides a guided walkthrough for evaluators and judges of the **Razorpay AI Buildathon (Track 03)**. Every scenario described below runs end-to-end with live backend database state mutations and real-time frontend UI updates.

---

## Prerequisites: Starting the System

Ensure backend and frontend servers are running:

### Terminal 1: Backend Server
```bash
# From d:/REVIVE
.\venv\Scripts\Activate.ps1
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Terminal 2: Frontend Dev Server
```bash
# From d:/REVIVE/frontend
npm run dev -- --port 5173
```

Open your browser to: **`http://localhost:5173`**

---

## Scenario 1: Executive Overview & Live Telemetry

1. Navigate to **Overview** (`/`):
   - Inspect the top KPI metric cards:
     - **Recovered Revenue**: Over ₹25,00,000+ displayed in genuine INR.
     - **Recovery Rate**: ~51% against industry standard ~22%.
     - **Active Cases**: Cases currently navigating the state machine.
     - **Pending Approvals**: High-ticket cases awaiting human authorization.
   - Observe the **Recovery Trends** chart and **Failure Category Breakdown** (UPI Intent, Card Expiry, Bank Downtime).
   - Note: Every chart and metric is computed dynamically from the live SQLite database (`revive.db`), never hardcoded.

---

## Scenario 2: Interactive Guided Demo (The 3 Core Proof Cases)

Navigate to the **Guided Demo** tab (`/demo`). This page features three dedicated benchmark cases designed to prove REVIVE's intelligence, safety, and operational reliability.

### Case A: Standard Autonomous Recovery (₹4,999)
- **Problem**: Soft UPI failure on consumer checkout (`insufficient_funds` / `bank_timeout`).
- **Target Value**: ₹4,999 (499,900 paise).
- **Execution Step**:
  1. Click **"Run Case A (Autonomous Loop)"**.
  2. Observe the live state progress:
     - `OPEN` $\longrightarrow$ `DIAGNOSING` (AI Agent analyzes taxonomy & history).
     - Recoverability Score calculated: **~82/100** (High recoverability).
     - Strategy Proposed: Dispatch interactive Razorpay Payment Link via WhatsApp.
     - Policy Checked: Below ₹50,000 threshold $\longrightarrow$ Auto-approved!
     - `READY_FOR_ACTION` $\longrightarrow$ `EXECUTING`.
     - Webhook Simulator fires authentic `payment.captured` event.
     - `EXECUTING` $\longrightarrow$ **`RECOVERED`**.
  3. **Verification**: Click "View Case Detail" to inspect the complete audit trail and timeline.

---

### Case B: High-Value Approval Gate (₹87,000)
- **Problem**: High-value annual B2B enterprise subscription failure.
- **Target Value**: ₹87,000 (8,700,000 paise).
- **Safety Policy**: Any transaction $\ge$ ₹50,000 **must not** be executed autonomously; it requires human authorization.
- **Execution Step**:
  1. Click **"Run Case B (Trigger Approval Gate)"**.
  2. Observe the state progress:
     - `OPEN` $\longrightarrow$ `DIAGNOSING`.
     - Policy Engine detects `amount_paise = 8700000 >= 5000000`.
     - Autonomous execution is **blocked**. State transitions to **`PENDING_APPROVAL`**.
  3. Navigate to **Approval Center** (`/approvals`):
     - Notice Case B appears at the top of the queue with priority badge.
     - Inspect the AI rationale: *"High-value enterprise failure requires account manager review."*
     - Click **"Approve & Recover"**.
  4. The case transitions to `EXECUTING` $\longrightarrow$ `RECOVERED`.
  5. **Verification**: Check the Audit Trail to confirm that the human operator ID and timestamp were permanently recorded.

---

### Case C: Hard Failure / Outage Guardrail (₹12,500)
- **Problem**: Bank hard decline (`card_stolen` / `account_closed`) or upstream provider downtime.
- **Target Value**: ₹12,500.
- **Safety Policy**: Never trigger blind retries on permanent decline codes; prevent customer harassment.
- **Execution Step**:
  1. Click **"Run Case C (Outage / Hard Decline)"**.
  2. Observe the state progress:
     - `OPEN` $\longrightarrow$ `DIAGNOSING`.
     - Stopping Rules Engine detects terminal decline code.
     - Retry is **quarantined**.
     - State transitions directly to **`STOPPED`** (or `FAILED`).
  3. **Verification**: Zero payment retries were dispatched, protecting merchant reputation and avoiding payment gateway decline penalties.

---

## Scenario 3: Real-Time Recovery Case Explorer

1. Navigate to **Recovery Cases** (`/recovery`).
2. Test the interactive filters:
   - Filter by Status: `RECOVERED`, `PENDING_APPROVAL`, `EXECUTING`, `STOPPED`.
   - Filter by Failure Type: `upi_failure`, `card_declined`, `bank_downtime`.
   - Search by customer name or transaction ID.
3. Click any row to open the **Case Detail View** (`/recovery/{id}`):
   - Inspect the **Recoverability Score Gauge** with positive and negative risk factors.
   - Review the **AI Agent Diagnostic Summary**.
   - Inspect the **Immutable Action Timeline** and raw Razorpay payload metadata.

---

## Scenario 4: Scientific A/B Evaluation Benchmark

1. Navigate to **Evaluation** (`/evaluation`).
2. Inspect the benchmark results computed across 1,000 identical cases:
   - **+127.9% Recovery Rate Lift** (51% vs 22.4%).
   - **-93.8% Reduction in Blind Retries** (114 vs 1,842).
   - **4.2 hrs vs 68.4 hrs Recovery Velocity**.
   - **100% Policy Compliance** (0 customer complaints).
3. Evaluators can re-run the benchmark live via the "Re-run Evaluation" button or inspect the methodology breakdown.
