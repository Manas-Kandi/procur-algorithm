# Procur Architecture Blueprint

## 1. System Overview
- **Control Plane Services**: policy engine, compliance, guardrails, scoring, explainability, negotiation.
- **Data Fabric**: Postgres (OLTP) for structured objects; object store for documents; immutable negotiation ledger (append-only).
- **Event Bus**: emits `request.created`, `offer.received`, `approval.granted`, `sla.breach`, etc. Worker pods for buyer/seller agent loops subscribe to events.
- **Integrations**: ERP/AP, e-sign, IDP/SSO, ticketing, vendor directories. All external calls pass through verification wrappers.
- **Observability**: metrics, traces, structured logs, policy alerting.

## 2. Data Contracts
- `Request`: structured procurement intent derived from free text.
- `VendorProfile`: capabilities, compliance posture, price tiers, guardrails.
- `Offer`: normalized proposals with deterministic score components.
- `RiskCard`: controls coverage, exceptions, remediation.
- `Contract`: template linkage, redlines, signature + fulfillment states.

Refer to `src/procur/models/` for canonical definitions.

## 3. Deterministic Services
- `PolicyEngine`: validates budget, approvals, clauses, risk, concession ladders.
- `ScoringService`: normalizes TCO, spec match, risk, time; computes weighted utility + sensitivity.
- `ComplianceService`: enforces compliance must-haves and manages exception workflow.
- `GuardrailService`: bank/KYC verification, anomaly detection, payment scrutiny.
- `ExplainabilityService`: transforms deterministic rationale into structured summaries.
- `NegotiationService`: coordinates multi-vendor rounds with stop conditions.

## 4. LLM Orchestration
- **Parsing & Clarification**: free-text to JSON with capped clarifiers.
- **Plan Suggestion**: anchor, BATNA, concession order; filtered by policy.
- **Message Drafting**: deterministic proposal + LLM natural language; validated against schema before dispatch.
- **Explainability**: deterministic metrics rendered into human-readable rationale.

See `src/procur/llm/` for orchestration adapters and schema validation.

## 5. Agent Lifecycles
### Buyer Agent
1. Intake & Policy validation
2. Sourcing & shortlist generation
3. Negotiation planning (deterministic + LLM)
4. Multi-vendor negotiation loop (parallel rounds)
5. Bundle creation and approval routing
6. Contracting, PO, provisioning/shipping
7. Aftercare, SLA monitoring, renewal automation

### Seller Agent
1. Guardrail setup and readiness
2. Qualification of buyer briefs
3. Policy-bound negotiation responses
4. Closing, ERP/AP handoff, renewal signals

Details in `src/procur/agents/`.

## 6. Negotiation Protocol
- Shared `NegotiationMessage` JSON schema with human + machine rationale.
- Concession ladders enforce policy-defined progression and stop conditions.
- Immutable ledger logs each round for audit and explainability.

## 7. Compliance & Trust
- SOC2/ISO/DPA gating, residency checks, exception workflow.
- Counter-party verification (DKIM/DMARC, KYC) before negotiations.
- Safety stops for outlier pricing, unusual payment terms, suspicious logistics.

## 8. Metrics & Feedback Loops
- Cycle time, savings, compliance exceptions, renewal leakage, trust/NPS.
- Negotiation analytics refine concession ladders, risk weighting, price bands.

## 9. Next Steps
- Connect persistence layer (SQLAlchemy migrations) and event bus implementation.
- Integrate with real LLM clients via `src/procur/llm/client.py`.
- Implement adapters for ERP/AP, e-sign, SSO provisioning.
- Instrument observability and policy alerting.
