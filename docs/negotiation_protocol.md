# Negotiation Protocol

## Message Schema
- Defined in `schemas/negotiation_message.schema.json` and mirrored by `procur.models.NegotiationMessage` (Pydantic model).
- Fields combine natural-language bullets with deterministic `machine_rationale` for audit and guardrail enforcement.

## Concession Ladder
1. `multi_year_discount`
2. `payment_terms`
3. `value_add`
4. `price_adjustment`

Stop conditions set by policy include minimum utility threshold, risk ceiling, and budget floor. The negotiation engine ensures concessions progress in order and never skip.

## Ledger Requirements
- Log every sent/received `NegotiationMessage` with timestamp, actor, hash of content.
- Capture policy validations, guardrail alerts, and approvals.
- Provide replay capability to regenerate "Why this pick" narratives.
