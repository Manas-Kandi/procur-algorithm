# ProcureAI Frontend Workspace

This workspace contains the ProcureAI web client. The build mirrors the UX architecture documented in `DESIGN_SYSTEM.md` with shared tokens, persona-driven layouts, and modular components for buyer and seller workflows.

## Getting Started

```bash
npm install --prefix frontend
npm run --prefix frontend dev
```

The development server runs on `http://localhost:5173`.

## Project Structure Highlights

- `src/main.tsx` – React entry point wiring the theme provider and React Query client.
- `src/App.tsx` – Suspense boundary that renders all route compositions.
- `src/routes/` – Route definitions with an authenticated layout wrapper.
- `src/components/layout/` – Application shell primitives (`AppLayout`, `Navigation`).
- `src/components/shared/` – Cross-cutting UI atoms/molecules (`MetricCard`, `SmartAlert`, `StageBoard`, etc.).
- `src/components/buyer/` – Buyer-specific composites (request intake, negotiation, approvals).
- `src/components/buyer/request/` – Guided intake components (`BudgetSelector`, `ScopeDetails`, `RequirementChecklist`).
- `src/components/buyer/negotiation/` – Negotiation theater cards and feeds.
- `src/components/buyer/approval/` – Approval workspace panels and decision bar.
- `src/pages/` – Page-level compositions for buyer and seller personas.
- `src/ui/tokens.ts` – Source of truth for design tokens surfaced as CSS variables.
- `src/ui/theme/ThemeProvider.tsx` – Injects tokens into CSS variables and exposes them via context.
- `tailwind.config.js` – Points Tailwind utilities at the design-token variables.

## Implemented UX Flows

- Buyer dashboard with metric cards, smart alerts, and a reusable `StageBoard` pipeline.
- New request flow using `FlowStepper`, intake components, and AI sourcing progress visualisations.
- Negotiation theater composed of `OfferCard`, `NegotiationFeed`, and `NegotiationControl` primitives.
- Approval workspace using modular `OfferSummary`, `RiskPanel`, and `DecisionBar` components.
- Seller workspace scaffolding with routes for dashboard, live deals, guardrails, intelligence, and territory views.

## Next Steps

1. **Portfolio & analytics polish** – Replace placeholder portfolio table with shared data-grid utilities and renewals cards per design system.
2. **Seller composites** – Flesh out guardrail forms, live deal room, and win/loss dashboards using shared tokens.
3. **Event streaming hooks** – Add WebSocket hooks (`src/ui/hooks`) for negotiation and sourcing updates.
4. **Storybook + tests** – Stand up Storybook stories for shared components and add Jest/RTL coverage.
5. **Authentication flow** – Expand auth pages (register, forgot password) and hydrate user context on load.

Refer to `DESIGN_SYSTEM.md` for component specs and roadmap coordination.
