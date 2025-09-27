# LLM Integration Guide

The platform uses NVIDIA's OpenAI-compatible endpoint for language understanding, planning, and drafting. All calls must be wrapped with deterministic validators before outputs affect state.

## Client
```
from openai import OpenAI

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="<api-key>"
)
```

`src/procur/llm/client.py` provides the `LLMClient` helper that encapsulates this pattern with sensible defaults (temperature 1.0, top_p 1.0, max_tokens 4096).

## Guarded Completions
- All prompts expect strict JSON outputs.
- `guarded_completion` retries up to two times on JSON parsing or schema validation failures.
- Parsers (`parse_request`, `parse_negotiation_message`) leverage Pydantic models, providing deterministic validation and error surfacing.

## Prompts
- `intake_prompt`: converts raw intake text into the `Request` schema, optionally prompting for clarifiers.
- `negotiation_prompt`: drafts negotiation messages for a specific concession ladder step and vendor context.

## Safety Requirements
- Never allow LLM output to bypass policy enforcement; deterministic layers (PolicyEngine, GuardrailService) always gate actions.
- Record all prompts/responses in the immutable ledger for audit.
- If validator retries exceed the limit, flag for human escalation rather than assuming defaults.
