# ProcureAI Frontend Workspace

This directory hosts the client-side application for the ProcureAI platform. The implementation follows the architecture and design patterns captured in `DESIGN_SYSTEM.md`.

## Getting Started

```bash
npm install
npm run dev
```

Vite will serve the application on `http://localhost:5173` by default.

## Project Structure

- `src/main.tsx` – Application entry point, mounting the React tree with the shared `ThemeProvider`.
- `src/App.tsx` – Top-level page shell placeholder that will be replaced as domain features land.
- `src/ui/tokens.ts` – Source of truth for design tokens (colors, typography, spacing, motion, breakpoints).
- `src/ui/theme/` – Theme helpers (`ThemeProvider`, app shell scaffolding) and future global context providers.
- `src/ui/components/` – Atomic components. Currently contains `RoleBadge` as a reference implementation.
- `src/ui/layouts/`, `src/ui/composites/`, `src/ui/hooks/` – Reserved directories mirroring the design system taxonomy for incremental build-out.
- `src/styles/global.css` – Baseline CSS applying tokens as CSS variables and setting application-level scaffolding.

## Incremental Build Targets

Aligned with the roadmap in `DESIGN_SYSTEM.md`, the next recommended steps are:

1. **Navigation primitives** – Replace the placeholder nav with a token-driven navigation component (e.g. `AppNavigation`) that can adapt to buyer/seller personas.
2. **Dashboard primitives** – Implement `MetricCard`, `StageBoard`, and `SmartAlert` components with Storybook stories.
3. **Request intake flow** – Build the `FlowStepper`, `BudgetInput`, and `NLInput` components backed by mocked data services.
4. **Event bus hooks** – Add real-time hooks in `src/ui/hooks` for subscribing to negotiation and sourcing channels.
5. **Testing toolchain** – Integrate Jest + React Testing Library and visual regression via Storybook once the first component tranche ships.

Each step should land with Storybook coverage and integration points to the existing backend APIs or mocked adapters when endpoints are still WIP.
