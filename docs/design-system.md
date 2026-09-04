# REVIVE — Design System & Visual Standards

## 1. Design Philosophy: The Anti-"AI Slop" Manifesto

Most hackathon submissions and modern AI demos suffer from a common affliction: **AI Slop**. They feature generic dark-purple neon gradients, unreadable floating cards, meaningless glowing animations, fake static numbers, and decorative chatbot avatars that communicate zero financial credibility.

REVIVE is intentionally built like a **tier-one fintech application** inspired by the restraint and clarity of **Stripe, Ramp, Linear, and Apple Human Interface Guidelines**:

1. **Information Density with Breathing Room**: Designed for finance operations teams who need to parse 100+ cases a minute without visual fatigue.
2. **Subtle Depth & Micro-Surfaces**: Ultra-crisp borders (`1px border-slate-200`), muted slate backdrops (`#F8FAFC`), and clean elevation shadows (`shadow-subtle`, `shadow-fintech`).
3. **Monetary Typography**: Numbers and currency values use tabular numerals (`JetBrains Mono` or tabular `Inter`) to ensure columns align perfectly across tables and cards.
4. **Purposeful Color Semantics**: Every color conveys precise operational state — no decorative color for its own sake.

---

## 2. Color Palette & Token System

| Token Name | Hex Code | Tailwind Utility | Semantic Purpose |
| :--- | :---: | :--- | :--- |
| **Background** | `#F8FAFC` | `bg-background` | Application canvas backdrop |
| **Surface** | `#FFFFFF` | `bg-surface` | Cards, modals, sidebars, tables |
| **Border** | `#E2E8F0` | `border-border` | Subtle hairline dividers and outlines |
| **Primary 900** | `#0F172A` | `text-primary-900` | Headings, brand accents, primary buttons |
| **Primary 800** | `#1E293B` | `text-primary-800` | Navigation items, active states |
| **Muted Slate** | `#64748B` | `text-slate-500` | Secondary labels, descriptions, timestamps |
| **Success Emerald** | `#10B981` | `bg-emerald-500` | Recovered states, healthy connectivity, positive factors |
| **Warning Amber** | `#F59E0B` | `bg-amber-500` | Pending approvals, high risk warnings, cooldowns |
| **Critical Rose** | `#EF4444` | `bg-rose-500` | Failed cases, stopped policies, hard declines |
| **Accent Indigo** | `#4F46E5` | `bg-indigo-600` | Diagnostic agents, AI reasoning indicators |

---

## 3. Typography Hierarchy

Fonts loaded via Google Fonts in `index.html`:
- **Primary Interface Font**: `Inter` (weights: 400, 500, 600, 700)
- **Monospace & Financial Font**: `JetBrains Mono` (weights: 400, 500)

```css
/* Typography Scale */
.page-title    { font-size: 1.5rem;   line-height: 2rem;   font-weight: 700; letter-spacing: -0.025em; }
.section-title { font-size: 1.125rem; line-height: 1.75rem; font-weight: 600; letter-spacing: -0.015em; }
.card-header   { font-size: 0.875rem; line-height: 1.25rem; font-weight: 600; }
.body-text     { font-size: 0.875rem; line-height: 1.25rem; color: #334155; }
.caption-text  { font-size: 0.75rem;  line-height: 1rem;    color: #64748B; font-weight: 500; }
.mono-amount   { font-family: 'JetBrains Mono', monospace; font-variant-numeric: tabular-nums; }
```

---

## 4. Reusable Component Catalog

### 1. `StatusBadge` (`frontend/src/components/StatusBadge.tsx`)
Renders color-coded lifecycle badges with contextual SVG icons and border highlights:
- `RECOVERED`: Emerald background with checkmark icon.
- `PENDING_APPROVAL`: Amber background with clock/alert icon.
- `EXECUTING`: Blue background with pulsing sync icon.
- `FAILED` / `STOPPED`: Rose background with slash icon.

### 2. `MetricCard` (`frontend/src/components/MetricCard.tsx`)
Displays primary KPI statistics with trend indicators, tooltip explanations, and responsive typography:
```tsx
<MetricCard
  title="Recovered Revenue"
  value="₹25,48,200"
  trend="+127.9% vs baseline"
  trendDirection="up"
  icon={TrendingUp}
  subtitle="510 successful recoveries"
/>
```

### 3. `EmptyState` (`frontend/src/components/EmptyState.tsx`)
Provides informative feedback when search queries or filters yield zero records, preventing blank screens.

### 4. `LoadingSkeleton` (`frontend/src/components/LoadingSkeleton.tsx`)
Smooth pulse placeholder preventing layout shift while React Query fetches backend API payloads.
