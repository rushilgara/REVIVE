# REVIVE — Architectural Decision Records (ADRs)

This document records the foundational engineering and architectural decisions made during the design and construction of REVIVE.

---

## ADR 001: 64-Bit Integer Arithmetic for Currency (Paise)

### Context
Floating-point arithmetic (`0.1 + 0.2 = 0.30000000000000004`) causes unacceptable round-off errors in financial ledgers, tax accounting, and gateway reconciliation.

### Decision
All monetary values across the backend, database schemas, and frontend API contracts are represented strictly as **64-bit integers in minor units** (paise for INR: ₹4,999.00 = `499900`). Conversion to major units occurs strictly at the presentation layer using `formatINR()`.

### Consequences
- **Positive**: Exact, lossless calculations across aggregations, percentages, and fees.
- **Trade-off**: Requires consistent discipline across backend models and frontend utility parsers.

---

## ADR 002: Strict State Machine Enforcement

### Context
Unconstrained dunning loops frequently jump states (e.g. attempting to execute an action on a closed or failed transaction), leading to duplicate debits, customer rage, and merchant chargebacks.

### Decision
We implemented a formal state machine (`backend/app/engine/state_machine.py`) enforcing legal lifecycle transitions:
`OPEN` $\longrightarrow$ `DIAGNOSING` $\longrightarrow$ `READY_FOR_ACTION` (or `PENDING_APPROVAL`) $\longrightarrow$ `EXECUTING` $\longrightarrow$ `RECOVERED` (or `FAILED` / `STOPPED`).
Attempting an illegal transition (e.g., `OPEN` directly to `EXECUTING`) raises a `StateMachineError` and records a security incident.

### Consequences
- **Positive**: Invariant guarantees at every stage; impossible to double-execute or bypass approval.
- **Trade-off**: Requires every pipeline step to register state transitions explicitly.

---

## ADR 003: Separation of Authority: AI Proposes, Policy Authorizes

### Context
LLMs are probabilistic and prone to hallucination, prompt injection, and unpredictability. Entrusting direct financial control or database mutations to an LLM is dangerous in production fintech.

### Decision
We enforced a strict boundary:
1. AI Agents (`DiagnosisAgent`, `DecisionAgent`) generate structured proposals (e.g., predicted recovery score, suggested channel, explanation).
2. The deterministic `PolicyEngine` and `StoppingRulesEngine` independently evaluate merchant invariants (caps, cooldowns, high-value thresholds).
3. Only the deterministic execution engine dispatches API calls, and only if policy authorizes.

### Consequences
- **Positive**: Complete compliance safety. An errant LLM output can never execute a transaction or violate merchant policy.
- **Trade-off**: Slightly higher orchestration complexity.

---

## ADR 004: Decoupling Action Dispatch from Outcome Verification

### Context
Many recovery tools trigger an email or payment link and immediately report the revenue as "recovered" or "in recovery", misleading merchant financial reporting.

### Decision
REVIVE strictly decouples execution from outcome. Disagreeing with naive optimism, generating a Razorpay link merely leaves the case in `EXECUTING`. Transition to `RECOVERED` requires:
- An authenticated incoming Razorpay webhook (`payment.captured` with HMAC signature), OR
- An explicit cryptographic settlement verification from Razorpay's API.

### Consequences
- **Positive**: Zero false positive recoveries. Financial metrics reflect actual settled bank funds.
- **Trade-off**: Requires persistent webhook listening and timeout handling for expired links.

---

## ADR 005: Dual-Database Strategy (SQLite + PostgreSQL)

### Context
Evaluators, judges, and developers need to clone and run REVIVE locally in under 60 seconds without provisioning complex external cloud services, while enterprise production requires enterprise PostgreSQL.

### Decision
SQLAlchemy 2.0 models are built with cross-database dialect compatibility:
- Local development: Zero-configuration SQLite (`revive.db`) with foreign keys and WAL mode enabled.
- Production: PostgreSQL with connection pooling and SSL mode.

### Consequences
- **Positive**: Instant single-command evaluation for hackathon judges with full production readiness.

---

## ADR 006: Deterministic Simulation Fallback

### Context
External payment gateway sandboxes frequently suffer outages, rate limits, or require merchant KYC before credentials can be provisioned.

### Decision
We built `DeterministicFallbackProvider` for AI and `INTEGRATION_MODE=simulation` for Razorpay. In simulation mode:
- 16 realistic failure scenarios across 1,000 cases can be simulated deterministically without external API keys.
- Real API keys can be provided at any time via `.env` to switch seamlessly to live Razorpay Test Mode.

### Consequences
- **Positive**: 100% offline evaluability with zero fragility.
