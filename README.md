# Procur Agentic Procurement Platform

This repository implements the deterministic+LLM architecture for Procur, an agent-as-a-service platform that scouts, negotiates, and closes SaaS and physical goods purchases. The codebase provides:

- Data contracts for requests, vendors, offers, risk, and contracting objects
- Deterministic services for policy enforcement, scoring, compliance, guardrails, and explainability
- Buyer and seller agent lifecycles with negotiation planning, multi-round concession ladders, and bundling logic
- LLM orchestration interfaces with schema validation and guardrail enforcement
- Event-driven workflow orchestration, immutable logging, and metrics hooks

See `docs/architecture.md` for a detailed walkthrough of components, lifecycles, and integrations.
