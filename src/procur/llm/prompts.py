from __future__ import annotations

from typing import Dict, List

from ..models import Request


def intake_prompt(raw_text: str, policy_summary: str) -> List[dict]:
    schema_example = {
        "request_id": "req-001",
        "requester_id": "user-001", 
        "type": "saas",
        "description": "CRM software for sales team",
        "specs": {"seats": 100, "features": ["crm", "automation"]},
        "quantity": 100,
        "budget_max": 120000,
        "currency": "USD",
        "must_haves": ["soc2"]
    }
    
    return [
        {
            "role": "system",
            "content": f"You are a procurement intake assistant. Produce JSON strictly matching this schema: {schema_example}. Generate unique IDs for request_id and requester_id.",
        },
        {
            "role": "user",
            "content": (
                "Convert the following request into structured JSON matching the schema exactly. "
                "Policy Summary: {policy}. Request: {request}"
            ).format(policy=policy_summary, request=raw_text),
        },
    ]


def negotiation_prompt(request: Request, vendor_context: Dict[str, str], ladder_step: str) -> List[dict]:
    """Enhanced negotiation prompt with strategy context"""
    schema_example = {
        "actor": "buyer_agent",
        "round": 1,
        "proposal": {
            "unit_price": 95.0,
            "currency": "USD",
            "quantity": 100,
            "term_months": 12,
            "payment_terms": "Net30"
        },
        "justification_bullets": ["Seeking competitive pricing for long-term partnership"],
        "machine_rationale": {
            "score_components": {"price": 0.8, "compliance": 1.0},
            "constraints_respected": ["budget_cap", "soc2_required"],
            "concession_taken": "price"
        },
        "next_step_hint": "counter"
    }
    
    # Extract strategy information from context
    strategy = vendor_context.get("strategy", "price_pressure")
    opening_bundle = vendor_context.get("opening_bundle", {})
    target_price = opening_bundle.get("price", vendor_context.get("target_price", 0))
    estimated_floor = vendor_context.get("estimated_floor", 0)
    round_num = vendor_context.get("round", 1)
    
    # Strategy-specific guidance
    strategy_guidance = {
        "price_anchor": "Set an aggressive low price anchor to establish negotiation range. Be bold but professional.",
        "term_trade": "Offer longer contract terms in exchange for better unit pricing. Emphasize revenue predictability.",
        "payment_trade": "Propose faster payment terms to justify price concessions. Highlight cash flow benefits.",
        "value_add": "Request additional services or training to justify current pricing levels.",
        "ultimatum": "Present final offer with clear decision timeline. Be firm but respectful.",
        "price_pressure": "Continue pushing for incremental price reductions through competitive positioning."
    }
    
    guidance = strategy_guidance.get(strategy, "Negotiate professionally for mutual benefit.")
    
    return [
        {
            "role": "system",
            "content": f"""You are a sophisticated procurement negotiation agent using strategy: {strategy}.
            
            STRATEGY GUIDANCE: {guidance}
            
            NEGOTIATION CONTEXT:
            - Round: {round_num}
            - Target price: ${target_price:.2f}/unit
            - Estimated vendor floor: ${estimated_floor:.2f}/unit
            - Vendor: {vendor_context.get('vendor_name', 'Unknown')}
            
            TACTICAL APPROACH:
            - Use the target price as your offer baseline
            - Justify offers with strategy-appropriate reasoning
            - Consider multi-dimensional trades (price, terms, payment, value-adds)
            - Be professional but assertive in pursuing your objectives
            
            Respond with JSON strictly matching this schema: {schema_example}
            
            Ensure your proposal aligns with the {strategy} strategy and targets the specified price point.""",
        },
        {
            "role": "user",
            "content": (
                f"Execute {strategy} strategy for {request.description}. "
                f"Quantity: {request.quantity}. Budget: ${request.budget_max}. "
                f"Target: ${target_price:.2f}/unit. "
                f"Vendor context: {vendor_context}. "
                f"Concession step: {ladder_step}."
            ),
        },
    ]
