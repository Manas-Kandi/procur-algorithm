# ProcureAI Design System

This document defines the frontend design system for the ProcureAI platform. It is structured to support incremental delivery while staying aligned with the current backend architecture, AI agent workflows, and multi-tenant procurement domain. Every component described here should map cleanly to existing services (API, event bus, workers) so the UI can evolve feature-by-feature without rework.

---

## 0. Using This Document
- **Read top-down when building new surfaces.** Start with foundations, then global patterns, then components, then composite layouts.
- **Deliver incrementally.** Each component specification includes its dependencies and the backend touchpoints it expects. Build in the suggested order to unlock buyer flows first, then seller flows.
- **Keep tokens single-sourced.** Expose design tokens as platform constants (e.g. `src/ui/tokens.ts`). All component styling must reference tokens, never raw values.
- **Map UI to events.** Surfaces that react to AI agents should subscribe to the event bus channels listed in the integration callouts.

---

## 1. Product Foundations

### 1.1 Platform Context
- AI-driven procurement and sales negotiation platform with dual personas (buyer-side and seller-side).
- Backed by a PostgreSQL persistence layer, Celery task workers, and an internal event bus for negotiation progress.
- Security and auditability are core: every action must be traceable, and role-based permissions are enforced by the backend (`src/procur/auth`, `src/procur/api/routes`).
- Frontend must surface AI reasoning to build trust and support human overrides.

### 1.2 Design Principles
- **Transparency by default.** Every AI suggestion or automation provides a “Why?” affordance.
- **Guided autonomy.** Automate the heavy lifting, but keep override paths one click away.
- **Progressive disclosure.** Summary first, with drill-down for deeper inspection.
- **Status over stages.** Communicate what is happening now, not just where the item sits in a workflow.
- **Mobile-friendly approvals.** Approvers and managers should complete critical tasks on phones.

### 1.3 Persona Emphasis
- **Buyer Requester:** fast intake, helpful defaults, educational pricing insights.
- **Procurement Ops:** pipeline visibility, policy enforcement, compliance reporting.
- **Approver:** concise decision screen with contextual risk signals.
- **Finance/AP:** financial roll-ups, renewal timelines, spend analytics.
- **Seller Rep:** deal pipeline, AI negotiation health, quick interventions.
- **Seller Manager/Pricing:** guardrail management, team dashboards, win/loss insights.

---

## 2. Design Tokens & Global Foundations
Create tokens as JSON/TypeScript constants (exported for CSS-in-JS or CSS Variables). Prefix shared tokens with `core`, persona accents with `buyer`/`seller` namespaces.

### 2.1 Color Palette
```
core.color.brand.primary        #1D4ED8  (trust blue)
core.color.brand.secondary      #7C3AED  (AI accent)
core.color.brand.inverse        #F8FAFC  (on-dark text)
core.color.surface.background   #F5F7FB
core.color.surface.canvas       #FFFFFF
core.color.surface.subtle       #F1F5F9
core.color.surface.elevated     #FFFFFF @ shadow-100
core.color.text.primary         #111827
core.color.text.muted           #4B5563
core.color.text.disabled        #9CA3AF
core.color.border.default       #D1D5DB
core.color.border.focus         #2563EB
core.color.data.positive        #16A34A
core.color.data.warning         #F59E0B
core.color.data.critical        #DC2626
core.color.data.info            #0EA5E9
buyer.color.accent              #0F766E (teal)
seller.color.accent             #F97316 (orange)
```
- Provide CSS variable exports (e.g. `--core-color-brand-primary`).
- Dark mode palette extends base neutrals with `900-50` scale; ensure contrast ≥ 4.5:1.

### 2.2 Status & Stage Colors
```
status.draft        #9CA3AF
status.sourcing     #0EA5E9
status.negotiating  #7C3AED
status.approving    #F59E0B
status.contracted   #16A34A
status.provisioning #1D4ED8
status.atRisk       #DC2626
status.blocked      #B91C1C
```
Use these for Kanban columns, stage badges, charts, and timeline indicators.

### 2.3 Typography
```
font.family.base        "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif
font.family.numeric     "IBM Plex Mono", "SFMono-Regular", monospace
font.size.scale         [12, 14, 16, 18, 20, 24, 30, 36, 48]
font.weight.regular     400
font.weight.medium      500
font.weight.semibold    600
font.weight.bold        700
line.height.tight       1.2
line.height.standard    1.4
line.height.relaxed     1.6
letter.spacing.allcaps  0.08em
```
- Default body text 15/1.5 for readability; keep metric cards at 14/1.4.
- Numerical data uses `font.family.numeric` for alignment.

### 2.4 Spacing & Layout
```
space.scale  [4, 8, 12, 16, 24, 32, 40, 48, 64]
space.inline.gutter   24
space.block.section   32
grid.columns.desktop  12 @ 72px max column width
grid.columns.tablet   8
grid.columns.mobile   4
grid.gap              24 desktop / 16 tablet / 12 mobile
radius.sm             6
radius.md             10
radius.lg             16
radius.pill           999
```
- Layout containers default to `max-width: 1320px` on desktop, `100%` on mobile.

### 2.5 Elevation & Shadows
```
shadow.0   none
shadow.100 0 2px 6px rgba(15, 23, 42, 0.08)
shadow.200 0 8px 20px rgba(15, 23, 42, 0.12)
shadow.300 0 16px 32px rgba(15, 23, 42, 0.16)
```
- Use `shadow.100` for elevated cards, `shadow.200` for modals, and `shadow.300` sparingly (e.g. AI reasoning overlays).

### 2.6 Icons & Illustration
- System icon set: Remix Icons (solid + line) or a comparable open-source set.
- Use duotone accent (brand primary + muted neutral) for empty states.
- AI agent avatars use circular frames with gradient border `linear-gradient(135deg,#1D4ED8,#7C3AED)`.

### 2.7 Motion
- Default transition: `150ms ease-out` for hover/focus, `200ms ease` for modal enters.
- Use micro-interactions to affirm AI actions (e.g. negotiation progress pulses). Avoid motion during approval flows unless user initiates.
- Provide a “Reduce Motion” toggle that respects OS preferences.

### 2.8 Data Visualization
- Palette: `[brand.primary, seller.accent, buyer.accent, data.info, data.positive, data.warning, data.critical]`.
- Stroke width 2px for line charts; bar padding 16px.
- Chart legends right-aligned on desktop, dropdown on mobile.
- Integrate with platform observability by matching colors in `monitoring/prometheus.yml` dashboards for consistency.

### 2.9 Interaction States
- Hover: lighten background (`surface.subtle`) + `border: focus`.
- Focus: focus ring `0 0 0 3px rgba(37,99,235,0.35)` + accessible outline.
- Disabled: `text.disabled`, `border: #E5E7EB`, remove shadows.
- Loading: skeleton shimmer using gradient `surface.subtle → surface.canvas`.
- Error: `border: data.critical`, background `rgba(220,38,38,0.04)`.

### 2.10 Grid & Breakpoints
```
breakpoint.xs 0-479px
breakpoint.sm 480-767px
breakpoint.md 768-1023px
breakpoint.lg 1024-1439px
breakpoint.xl 1440px+
```
- Approval flows must stay single-column ≤ `sm`.
- Use responsive utilities along with CSS container queries for dynamic cards.

---

## 3. Global UI Patterns

### 3.1 Application Shell
- **Top App Bar:** shows organization switcher, global search, AI agent status, notifications.
- **Side Navigation:** collapsible rail with persona-aware sections. Use icons + labels at desktop, icons only collapsed. Provide workspace switcher (Buyer | Seller) if user has multi-role access.
- **Session Indicator:** real-time WebSocket badge pulling from `src/procur/events/bus.py` channels (e.g. `negotiation.progress`).
- **Command Palette:** keyboard-triggered (`⌘K / Ctrl+K`) for global actions.

### 3.2 Global Navigation Items
- Buyer: Dashboard, Requests, Negotiations, Approvals, Portfolio, Reports.
- Seller: Dashboard, Guardrails, Live Deals, Intelligence, Territory.
- Shared: Audit Log, Settings, Help.
- Use `status.badge` tokens to show counts (pending approvals, deals at risk).

### 3.3 Feedback Surfaces
- Toasts (top-right, stacked, auto-dismiss 6s, manual close). Use success/info/warning colors.
- Inline banners for persistent alerts (e.g. policy violations). Provide call-to-action.
- Notification drawer with filters (AI actions, manual tasks, system alerts) keyed to `AuditLogRecord`.

### 3.4 Empty States & Skeletons
- Provide domain-specific messaging (“No negotiations in progress. Launch AI sourcing to get started.”).
- Show CTA buttons linking to primary action (create request, configure guardrails).

---

## 4. Core Component Library
Document components in the order they should be built. Each definition includes purpose, anatomy, states, and backend touchpoints.

### 4.1 Dashboard & Monitoring

**Metric Card (`<MetricCard />`)**
- Contents: label, primary value, delta badge, sparkline.
- Variants: `neutral`, `buyer`, `seller`, `warning`.
- States: loading skeleton, error fallback.
- Data source: Aggregated endpoints (e.g. `/api/reports/metrics`). Align with `monitoring.py` events for real-time updates.

**Stage Kanban (`<StageBoard />`)**
- Columns map to status tokens. Cards show title, requester/vendor, time-in-stage, blockers.
- Drag-and-drop optional; backend updates `RequestRecord.status` via `/api/requests/{id}` PATCH.
- Provide column filter chips and search.

**Smart Alert Banner (`<SmartAlert />`)**
- Includes icon, title, supporting text, CTA button, “Generated by AI” pill.
- Severity: info/success/warning/critical.
- Link to AI reasoning modal.

### 4.2 Request Intake Flow

**Flow Stepper (`<FlowStepper />`)**
- Shows steps with statuses (complete/current/next). Mobile collapses to progress bar + step summary.
- Steps: Budget → Scope → Requirements → Policy Preview → Launch AI.

**Budget Selector (`<BudgetInput />`)**
- Modes: exact, range, need help (pulls historical averages via `/api/vendors/benchmarks`).
- If “See typical pricing” selected, show inline `PricingInsightCard` with fetched data.

**Natural Language Intake (`<NLInput />`)**
- Hybrid text area + suggestions chips. Uses AI microcopy, with placeholder examples.
- After input, show parsed fields (category, quantity) for confirmation.
- Connects to contract generator service for context suggestions.

**Requirements Checklist (`<RequirementChecklist />`)**
- Category-aware default checklist; items toggled as chips or list rows.
- Provide “Add custom requirement” inline input.
- Compliance toggles shown using `TogglePill` variant with icons (SOC2, HIPAA).

**Policy Preview (`<PolicyPreviewCard />`)**
- Summarizes approvers, SLA, timeline.
- Shows risk score (green/yellow/red) with explanation link.
- Pulls from policy configs via `/api/policies/route`.

**AI Sourcing Status (`<SourcingProgress />`)**
- Animated progress indicator with real-time vendor counts.
- Subscribes to event bus topics `sourcing.progress` and `negotiation.init`.
- Provide manual stop + escalate control.

### 4.3 Negotiation Theater (Buyer)

**Offer Card (`<OfferCard />`)**
- Layout: vendor logo, price summary, key terms list, “Why recommended” bullet list.
- States: leading, contender, declined, accepted.
- CTA: `Accept`, `Counter`, `Escalate`.
- Data: `OfferRecord`, `NegotiationSessionRecord`.

**Comparison Matrix (`<ComparisonMatrix />`)**
- Table view with sticky headers. Columns = vendors, rows = features/metrics.
- Support heatmap coloring for best-in-class cells.
- Provide export icon for audit.

**Negotiation Feed (`<NegotiationFeed />`)**
- Timeline cards with actor (agent/human), quote, timestamp, reasoning tag.
- Support filters (rounds, concessions, blockers).
- Integrate with `event_bus` streaming updates.

**Control Panel (`<NegotiationControl />`)**
- Sliders for budget adjustments, toggles for new requirements, buttons for escalate/end session.
- Enforce permission checks from `permissions.py` before enabling destructive actions.

**AI Reasoning Modal (`<ReasoningDrawer />`)**
- Slide-over showing “Why $1150?” explanation tree.
- Display inputs (budget, floor price, market benchmark, AI strategy) referencing `AI Transparency Layer` requirements.

### 4.4 Approval Workspace

**Offer Summary Pane (`<OfferSummary />`)**
- Two-column layout: key financial metrics left, attachments & documents right.
- Provide `ConfidenceScoreBadge` with tooltip.

**Risk & Compliance Panel (`<RiskPanel />`)**
- Traffic light grid per requirement (security, legal, finance).
- Show outstanding exceptions with recommended remedy.
- Include `ExportAuditLog` button hooking to `/api/audit/logs?resource=requestId`.

**Decision Bar (`<DecisionBar />`)**
- Sticky bottom bar with `Approve`, `Request Changes`, `Reject`, `Escalate` buttons.
- Each action opens comment drawer (required field) before submission.
- Mobile variant uses full-width buttons stacked.

### 4.5 Portfolio Management

**Subscription Table (`<SubscriptionTable />`)**
- Columns: Vendor, Category, Seats, Utilization, Monthly Cost, Renewal Date, Status.
- Row actions: `Flag for renegotiation`, `Request cancellation`.
- Support inline filters and column pinning.

**Renewal Card (`<RenewalCard />`)**
- Emphasizes days to renewal, usage insights, AI recommendation.
- CTA buttons: Auto-renegotiate, Review manually, Auto-renew.
- Animated countdown ring using progress token.

**Bulk Action Drawer (`<BulkActionDrawer />`)**
- Shows selected items, recommended actions, estimated savings.
- Confirms API payload before submission.

### 4.6 Seller Dashboard Components

**Pipeline Chart (`<PipelineOverview />`)**
- Funnel visualization by stage with totals and conversion rates.
- Provide `Deals at risk` badge linking to filtered list.

**Agent Activity Feed (`<AgentActivityFeed />`)**
- Similar to buyer negotiation feed but flipped perspective.
- Tag entries by urgency (needs human, information, success).

**Guardrail Config Form (`<GuardrailForm />`)**
- Grouped sections: Pricing Strategy, ZOPA, Value Levers.
- Use segmented controls, slider inputs, toggle lists.
- Include validation overlays when inputs conflict (e.g. floor price > list price).

**ZOPA Slider (`<ZopaSlider />`)**
- Dual-range slider with color-coded zones (green=safe, amber=review, red=stop).
- Integrates with seller accent color.

**Negotiation Transcript (`<TranscriptTimeline />`)**
- Accordion list per round with highlight badges for concessions.
- Provide `diff` view between rounds.

**Deal Health Widget (`<DealHealth />`)**
- Composite meter showing distance to floor, momentum, close probability.
- Use radial progress + textual summary.

**Intervention Controls (`<InterventionBar />`)**
- Buttons: Take over, Approve special pricing, Send to manager.
- Each opens confirm modal with comment requirement.

**Win/Loss Dashboard Cards (`<WinLossSummary />`)**
- Multi-metric card with trend charts and top reasons chips.
- Provide quick filter pills (Last 30 days, 90 days, custom).

**Territory Map/Segment Grid (`<TerritoryView />`)**
- Map view (if geo) or matrix list (if segment). Reuse shared data viz tokens.
- Use overlays to show density and link to deals list.

**Approval Queue Table (`<ApprovalQueue />`)**
- Shows deals awaiting manager decision, required justification fields, SLA timers.

### 4.7 Shared Components & Utilities

**AI Attribution Tooltip (`<AiTooltip />`)**
- Icon button with tooltip explaining AI source, model version, confidence.
- Pulls metadata from AI service responses (attach to each component receiving AI data).

**Audit Log Viewer (`<AuditLogViewer />`)**
- Modal/table listing events with search, filters, export.
- Connect to `/api/audit/logs` paginated endpoint.

**Role Badge (`<RoleBadge />`)**
- Display current user role(s); color-coded (buyer teal, seller orange, admin purple).

**Status Chip (`<StatusChip />`)**
- Use tokens from section 2.2. Support icon slot and `aria-label` for screen readers.

**Inline Insight (`<InsightCallout />`)**
- Small bordered box for AI hints; includes icon, text, `Learn more` link.

**Skeleton Loader (`<Skeleton />`)**
- Provide rectangular, circular variants with shimmer.

**Tab Navigation (`<Tabs />`)**
- Underline indicator, scrollable on mobile.
- Keyboard accessible (arrow keys + Home/End).

---

## 5. Layout & Flow Templates
Document page-level compositions using the components above. Each template should live in `/src/ui/layouts` as composable React (or chosen framework) layouts.

### 5.1 Buyer Dashboard Layout
- **Hero row:** Welcome message, organization selector, AI agent status chip.
- **KPI row:** 3-4 `<MetricCard />` components.
- **Pipeline section:** `<StageBoard />` using 6 columns (scrollable horizontally on tablet).
- **Smart alerts:** stacked `<SmartAlert />` banners.
- **Renewal highlights:** mini `<RenewalCard />` grid using 4-column layout.

### 5.2 New Request Flow Layout
- **Sticky progress header** with `<FlowStepper />`.
- Content area uses stepped forms:
  1. Budget: `<BudgetInput />`, `<PricingInsightCard />`.
  2. Scope: `<NLInput />` with parsed summary card.
  3. Requirements: `<RequirementChecklist />` + `<TogglePill />` compliance toggles.
  4. Policy Preview: `<PolicyPreviewCard />`.
  5. Launch: `<SourcingProgress />` with real-time updates.
- Right sidebar (desktop) for `<InsightCallout />` and policy reminders.

### 5.3 Negotiation Theater Layout
- **Top row:** three `<OfferCard />` components with badges (best offer, improvement, fallback).
- **Middle:** `<ComparisonMatrix />` on desktop, collapsible accordions on mobile.
- **Sidebar (desktop)/Bottom sheet (mobile):** `<NegotiationFeed />`.
- **Footer:** `<NegotiationControl />` sticky bar.

### 5.4 Approval Workspace Layout
- Two-column grid (8/4) on desktop; single-column stack on mobile.
- Left: `<OfferSummary />`, `<ComparisonMatrix />` (condensed), `<InsightCallout />`.
- Right: `<RiskPanel />`, attachments list, `<AuditLogViewer />` trigger.
- Sticky `<DecisionBar />` anchored bottom.

### 5.5 Portfolio Management Layout
- Filter bar with chips + search above `<SubscriptionTable />`.
- Secondary panel toggles between `<RenewalCard />` list and analytics chart.
- `<BulkActionDrawer />` appears from right when multi-select active.

### 5.6 Seller Dashboard Layout
- Hero metrics row for SLA, Win rate, Pipeline.
- Two-column grid: `<PipelineOverview />` + `<AgentActivityFeed />`.
- Lower sections: `<DealHealth />` list, `<WinLossSummary />`, `<TerritoryView />`.

### 5.7 Guardrail Configuration Layout
- Stepper-like navigation tabs (Pricing, ZOPA, Value Levers).
- Form sections use cards with `<GuardrailForm />`, `<ZopaSlider />`, `<InsightCallout />`.
- Right sidebar summarizing impacts before publish.

### 5.8 Live Deal Room Layout
- Left column: `<TranscriptTimeline />` with per-round expansion.
- Right column: `<OfferCard />` (current round) + `<DealHealth />` widget + `<InterventionBar />`.
- Provide persistent header with deal metadata and SLA timer.

### 5.9 Win/Loss Intelligence Layout
- Filters bar (date range, segment, competitor).
- KPI row (Win rate, Avg discount, Deal value).
- Middle: stacked bar chart + table view.
- Bottom: `<InsightCallout />` for AI recommendations.

### 5.10 Territory & Team Management Layout
- Tabs for Geography vs Segment vs Team.
- Grid of reps with `<WinLossSummary />` nested mini-cards.
- `<ApprovalQueue />` table pinned to the right for quick decisions.

### 5.11 Mobile Approval Flow
- Collapsed header with vendor name, amount, stage.
- Accordion sections for summary, risk, comments.
- Persistent bottom `<DecisionBar />` with full-width buttons.
- Swipe gestures for reveal of AI reasoning, but require tap to confirm.

---

## 6. Accessibility & Compliance Guidelines
- WCAG 2.1 AA minimum; ensure color contrast and keyboard navigation.
- Provide `aria-live` regions for real-time updates (negotiation feed, sourcing progress).
- Use logical tab order; trap focus within modals and drawers.
- Screen reader labels for AI actions (“AI agent proposed an offer at $1150”).
- Support localization (copy stored in i18n files, currency formatting via locale-aware utilities).
- Provide downloadable audit logs in accessible CSV/PDF formats.

---

## 7. Implementation Guidance

### 7.1 Tech Stack Alignment
- Recommended stack: React (or Next.js) + TypeScript, component styling via CSS variables + Tailwind/Tailwind-in-JS to leverage tokens.
- Store tokens under `src/ui/tokens.ts` and expose CSS variables at `:root`.
- Component library structure:
  - `src/ui/components` (atoms, molecules, organisms)
  - `src/ui/layouts` (page shells)
  - `src/ui/composites` (persona-specific assemblies)
  - `src/ui/hooks` (event bus subscriptions, data fetching)

### 7.2 Data Integration
- Use API client in `src/procur/llm/client.py` patterns for service calls, or build a dedicated REST client module.
- Subscribing to event bus: Use WebSocket client targeting `/events` endpoints defined in `src/procur/orchestration/event_bus.py`.
- Persist user preferences (e.g. hidden columns, layout choices) via `/api/users/preferences` and mirror backend schema (`UserAccount.preferences`).

### 7.3 State Management
- Recommended: React Query (for server cache) + Zustand/Redux Toolkit for client state as needed.
- Normalize data models mirroring backend repositories to reduce translation overhead.

### 7.4 Testing & QA
- Component unit tests with Jest/RTL.
- Visual regression with Storybook + Chromatic (or Percy).
- Contract tests for event payloads (negotiation progress, sourcing updates).
- Accessibility linting (axe-core) integrated into CI.

### 7.5 Security & Permissions
- UI must request current user roles once per session. Use `permissions.py` matrix to gate actions client-side (in addition to backend enforcement).
- All destructive actions require confirmation + optional comment for audit.

---

## 8. Build Roadmap (Incremental Delivery)
1. **Set up token infrastructure** (design tokens, theming utilities, typography base).
2. **Global shell & navigation** (App shell, navigation, role badge, command palette).
3. **Buyer core flow**
   - Dashboard primitives (`MetricCard`, `StageBoard`, `SmartAlert`).
   - Request intake components (Stepper → Sourcing progress).
   - Negotiation theater components.
   - Approval workspace + Decision bar.
4. **Portfolio management components** (Subscription table, Renewal cards, Bulk drawer).
5. **Shared utilities** (AI tooltip, Audit log viewer, Insight callouts).
6. **Seller-side components** (Pipeline, Guardrails, Deal room, Win/loss, Territory views).
7. **Mobile-first approvals** (optimize components, add responsive variants).
8. **Motion & accessibility refinements** (final polish, ADA validation).

Deliver each tranche with accompanying Storybook stories and integration hooks to relevant APIs/event channels before moving to the next.

---

## 9. Change Management
- Keep this document versioned. Add changelog entries when tokens/components evolve.
- Coordinate with backend teams before introducing new data requirements.
- Update `IMPLEMENTATION_COMPLETE.md` when major UI feature sets ship.

---

By adhering to this design system, the ProcureAI frontend can scale gracefully across buyer and seller experiences, maintain trust in AI-driven workflows, and stay tightly coupled with the platform architecture already in place.
