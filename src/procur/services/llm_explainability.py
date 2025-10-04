"""LLM-powered explainability service for negotiation transparency and audit."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..llm import LLMClient
from ..models import Offer, Request, VendorProfile


@dataclass
class RationaleFact:
    """A single fact-to-implication pair in the explanation."""
    fact: str
    implication: str


@dataclass
class PolicyEvent:
    """A policy or guardrail enforcement event."""
    policy_id: str
    outcome: str  # applied|violated|enforced
    note: str


@dataclass
class NumericSnapshot:
    """Canonical numeric facts for audits and charts."""
    latest_unit_price: float
    budget_per_unit: float
    tco: float
    tco_vs_budget_pct: float
    acceptance_probability: float


@dataclass
class RecommendedAction:
    """A suggested next action with priority and type."""
    priority: int
    type: str  # present_counter|request_term|request_payment|escalate_to_human|close_deal
    text: str


@dataclass
class ExplainabilityTrace:
    """Internal trace for debugging and engineering."""
    step: str
    detail: str


@dataclass
class ExplanationRecord:
    """
    Complete explanation record (v1) for a negotiation state.

    This is the output schema returned by the LLM explainability service.
    """
    explanation_version: str
    short_summary: str
    detailed_explanation: str
    rationale: List[RationaleFact]
    policy_summary: List[PolicyEvent]
    numeric_snapshots: NumericSnapshot
    recommended_actions: List[RecommendedAction]
    confidence: float
    explainability_trace: List[ExplainabilityTrace]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


# System prompt for the LLM explainability agent
EXPLAINABILITY_SYSTEM_PROMPT = """You are an Explainability Agent for a negotiation engine.
Your job is to transform a structured negotiation state into:
1) A short 1-2 sentence user-facing summary.
2) A detailed, step-by-step explanation of what happened this round, why the engine made its decision, and the important numeric facts.
3) A prioritized list of recommended next actions (only suggestions; do not change engine state).
4) A concise structured audit record with key numeric snapshots.

Rules:
- Do NOT propose actions that violate policy events passed in policy_summary.
- Use only the facts in the input JSON. If a fact is missing, say "data not available" instead of inventing numbers.
- Keep numerical math consistent and show simple calculations inline where helpful.
- Keep the short_summary neutral and factual.
- Keep the detailed_explanation suitable for non-technical procurement people.
- Provide `confidence` in the explanation (0.0-1.0). If many fields are missing, reduce confidence.
- Do not produce legal or financial advice; add "Consult legal/compliance" when policy events require it.
- Output must be valid JSON per the ExplanationRecord v1 schema.
- Never invent policy or guardrails. All policy-related statements must be direct echoes of policy_events.

Output JSON schema:
{
  "explanation_version": "1.0",
  "short_summary": "string (1-2 sentences for UI header)",
  "detailed_explanation": "string (multi-paragraph narrative)",
  "rationale": [
    {"fact": "string", "implication": "string"}
  ],
  "policy_summary": [
    {"policy_id": "string", "outcome": "applied|violated|enforced", "note": "string"}
  ],
  "numeric_snapshots": {
    "latest_unit_price": 0.0,
    "budget_per_unit": 0.0,
    "tco": 0.0,
    "tco_vs_budget_pct": 0.0,
    "acceptance_probability": 0.0
  },
  "recommended_actions": [
    {"priority": 1, "type": "present_counter|request_term|request_payment|escalate_to_human|close_deal", "text": "string"}
  ],
  "confidence": 0.0,
  "explainability_trace": [
    {"step": "string", "detail": "string"}
  ]
}
"""


# Few-shot examples to guide the LLM
FEW_SHOT_EXAMPLES = """
# Example 1: Early Anchor (Round 1)
Input: {"round": 1, "latest_offer": {"unit_price": 95.0}, "budget_per_unit": 125.0, "decision": "COUNTER", "acceptance_probability": 0.72, "policy_events": ["Applied initial anchor at 15% below list price"]}

Output: {
  "explanation_version": "1.0",
  "short_summary": "Round 1: Buyer opened with anchor at $95/unit (24% under budget). Engine decision: COUNTER with 72% acceptance probability.",
  "detailed_explanation": "The buyer initiated negotiations with an anchor offer of $95.00 per unit, which is 24% below the per-unit budget of $125.00. The negotiation engine applied an initial anchoring strategy, setting the opening offer at 15% below the vendor's list price. The acceptance probability of 72% suggests this is a reasonable starting point that balances buyer value with likelihood of seller engagement.",
  "rationale": [
    {"fact": "Buyer budget is $125/unit; anchor is $95/unit", "implication": "Creates 24% negotiation headroom for concessions if needed"},
    {"fact": "Acceptance probability at 72%", "implication": "Strong likelihood seller will engage rather than walk away"},
    {"fact": "Applied 15% below-list anchoring policy", "implication": "Standard aggressive-but-fair opening strategy"}
  ],
  "policy_summary": [
    {"policy_id": "anchor_strategy", "outcome": "applied", "note": "Applied initial anchor at 15% below list price"}
  ],
  "numeric_snapshots": {
    "latest_unit_price": 95.0,
    "budget_per_unit": 125.0,
    "tco": 0.0,
    "tco_vs_budget_pct": 76.0,
    "acceptance_probability": 0.72
  },
  "recommended_actions": [
    {"priority": 1, "type": "present_counter", "text": "Wait for seller's counteroffer to gauge their floor and flexibility"},
    {"priority": 2, "type": "request_term", "text": "If seller counters high, explore term/payment trades to reduce effective cost"},
    {"priority": 3, "type": "escalate_to_human", "text": "Escalate only if seller refuses to engage or demands above-budget pricing"}
  ],
  "confidence": 0.90,
  "explainability_trace": [
    {"step": "parse_inputs", "detail": "All required fields present"},
    {"step": "validate_policy", "detail": "1 policy event matches anchor strategy"},
    {"step": "compute_rationale", "detail": "Generated 3 fact-implication pairs"}
  ]
}

# Example 2: Stalemate (Round 6, no price movement)
Input: {"round": 6, "latest_offer": {"unit_price": 82.0, "term_months": 12}, "budget_per_unit": 125.0, "decision": "COUNTER", "acceptance_probability": 0.68, "opponent_model": {"consecutive_no_price_moves": 3}, "policy_events": ["Seller at estimated floor; recommend non-price levers"]}

Output: {
  "explanation_version": "1.0",
  "short_summary": "Round 6: Stalemate detected. Seller holding at $82/unit with 3 consecutive non-price moves. Engine recommends term/payment trades.",
  "detailed_explanation": "After 6 rounds of negotiation, the seller is holding firm at $82.00 per unit with no price movement for the last 3 rounds. The opponent model estimates the seller has reached their price floor. The acceptance probability remains moderate at 68%, but pure price concessions are unlikely to succeed. The engine recommends shifting to non-price levers: extending contract term (e.g., 24 months for volume discount) or offering favorable payment terms (e.g., NET-15 for cash flow benefit). If these trades fail, escalation to a human negotiator is warranted to reassess requirements or approve above-target pricing.",
  "rationale": [
    {"fact": "3 consecutive rounds with no seller price movement", "implication": "Seller likely at or near price floor; further price pressure may cause walkaway"},
    {"fact": "Current price $82/unit vs budget $125/unit", "implication": "Still 34% under budget; room to accept if non-price terms are favorable"},
    {"fact": "Policy recommends non-price levers", "implication": "Switch from price-only to term/payment trades to unlock value"}
  ],
  "policy_summary": [
    {"policy_id": "stalemate_detection", "outcome": "enforced", "note": "Seller at estimated floor; recommend non-price levers"}
  ],
  "numeric_snapshots": {
    "latest_unit_price": 82.0,
    "budget_per_unit": 125.0,
    "tco": 0.0,
    "tco_vs_budget_pct": 65.6,
    "acceptance_probability": 0.68
  },
  "recommended_actions": [
    {"priority": 1, "type": "request_term", "text": "Offer 24-month term in exchange for 3-5% volume discount"},
    {"priority": 2, "type": "request_payment", "text": "Propose NET-15 payment terms for cash flow benefit to seller"},
    {"priority": 3, "type": "escalate_to_human", "text": "If both trades rejected, escalate for human review of requirements or approval to accept current offer"}
  ],
  "confidence": 0.85,
  "explainability_trace": [
    {"step": "parse_inputs", "detail": "Round 6, stalemate pattern detected"},
    {"step": "opponent_model_check", "detail": "Consecutive no-price moves: 3"},
    {"step": "policy_enforcement", "detail": "Non-price lever policy triggered"}
  ]
}

# Example 3: Policy Enforcement (Floor Applied)
Input: {"round": 4, "latest_offer": {"unit_price": 78.0}, "budget_per_unit": 125.0, "decision": "COUNTER", "acceptance_probability": 0.88, "policy_events": ["Vendor guardrail: price floor $75.00 enforced; adjusted offer from $72 to $78"]}

Output: {
  "explanation_version": "1.0",
  "short_summary": "Round 4: Vendor price floor ($75) enforced. Engine adjusted buyer offer from $72 to $78/unit. Acceptance probability 88%.",
  "detailed_explanation": "In round 4, the buyer's initial counter would have been $72.00 per unit. However, the vendor's guardrails specify a hard price floor of $75.00. The negotiation engine automatically enforced this guardrail and adjusted the buyer's offer upward to $78.00 per unit (with a small buffer to avoid appearing at the floor). This enforcement ensures compliance with vendor constraints while preserving deal viability. The acceptance probability increased to 88%, indicating high likelihood of seller acceptance at this price point.",
  "rationale": [
    {"fact": "Buyer counter would have been $72, but vendor floor is $75", "implication": "Engine must enforce guardrail to comply with vendor policy"},
    {"fact": "Adjusted offer to $78 (with buffer above floor)", "implication": "Avoids signaling buyer is aware of exact floor; maintains negotiation positioning"},
    {"fact": "Acceptance probability jumped to 88%", "implication": "Offer is now well within seller's acceptable range"}
  ],
  "policy_summary": [
    {"policy_id": "vendor_guardrail_floor", "outcome": "enforced", "note": "Vendor guardrail: price floor $75.00 enforced; adjusted offer from $72 to $78"}
  ],
  "numeric_snapshots": {
    "latest_unit_price": 78.0,
    "budget_per_unit": 125.0,
    "tco": 0.0,
    "tco_vs_budget_pct": 62.4,
    "acceptance_probability": 0.88
  },
  "recommended_actions": [
    {"priority": 1, "type": "present_counter", "text": "Present adjusted offer at $78/unit; high probability of seller acceptance"},
    {"priority": 2, "type": "close_deal", "text": "If seller accepts, proceed to finalize contract with current terms"},
    {"priority": 3, "type": "request_term", "text": "If seeking additional value, explore term extension or value-adds rather than further price reduction"}
  ],
  "confidence": 0.95,
  "explainability_trace": [
    {"step": "guardrail_check", "detail": "Vendor floor $75 detected"},
    {"step": "policy_enforcement", "detail": "Adjusted buyer offer from $72 to $78"},
    {"step": "acceptance_probability", "detail": "Recomputed to 88% after adjustment"}
  ]
}
"""


class LLMExplainabilityService:
    """
    LLM-powered explainability service for negotiation transparency.

    Converts negotiation state into human-readable explanations, structured
    audit trails, and actionable recommendations using an LLM.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """Initialize the explainability service with an LLM client."""
        self.llm_client = llm_client or LLMClient()
        self.explanation_version = "1.0"

    def build_payload(
        self,
        request: Request,
        vendor: VendorProfile,
        latest_offer: Offer,
        history: List[Offer],
        round_number: int,
        decision: str,
        acceptance_probability: float,
        policy_events: List[str],
        opponent_model: Optional[Dict[str, Any]] = None,
        plan: Optional[Dict[str, Any]] = None,
        competing_offers: Optional[List[Dict[str, Any]]] = None,
        concession_notes: Optional[List[str]] = None,
        derived_metrics: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Build the compact JSON payload to send to the LLM.

        Args:
            request: The procurement request
            vendor: The vendor being negotiated with
            latest_offer: The most recent offer
            history: Last N offers (3-6 recommended)
            round_number: Current negotiation round
            decision: Engine decision (ACCEPT/COUNTER/DROP/etc)
            acceptance_probability: Computed acceptance probability
            policy_events: List of policy enforcement notes
            opponent_model: Opponent model summary
            plan: Negotiation plan summary
            competing_offers: List of competing vendor offers
            concession_notes: Engine-appended concession notes
            derived_metrics: Pre-computed metrics

        Returns:
            Compact JSON payload for LLM
        """
        # Build minimal request representation
        budget_per_unit = None
        if request.budget_max and request.quantity:
            budget_per_unit = request.budget_max / request.quantity

        request_data = {
            "id": request.request_id,
            "quantity": request.quantity,
            "budget_max": request.budget_max,
            "budget_per_unit": budget_per_unit,
            "must_haves": request.must_haves,
            "compliance_requirements": request.compliance_requirements,
        }

        # Build minimal vendor representation
        vendor_data = {
            "id": vendor.vendor_id,
            "name": vendor.name,
            "price_tiers": vendor.price_tiers,
            "guardrails": {
                "price_floor": vendor.guardrails.price_floor if vendor.guardrails else None,
                "price_ceiling": vendor.guardrails.price_ceiling if vendor.guardrails else None,
            },
            "capability_tags": vendor.capability_tags,
            "certifications": vendor.certifications,
        }

        # Build latest offer representation
        offer_data = {
            "components": {
                "unit_price": latest_offer.components.unit_price,
                "currency": latest_offer.components.currency,
                "quantity": latest_offer.components.quantity,
                "term_months": latest_offer.components.term_months,
                "payment_terms": latest_offer.components.payment_terms.value,
                "one_time_fees": latest_offer.components.one_time_fees or {},
            },
            "score": {
                "utility": latest_offer.score.utility,
                "risk": latest_offer.score.risk,
                "tco": latest_offer.score.tco if hasattr(latest_offer.score, 'tco') else None,
            },
        }

        # Build history (last 3-6 offers)
        history_data = []
        for offer in history[-6:]:
            history_data.append({
                "timestamp": offer.timestamp.isoformat() if hasattr(offer, 'timestamp') else None,
                "actor": "buyer" if offer.from_buyer else "seller",
                "unit_price": offer.components.unit_price,
                "term_months": offer.components.term_months,
                "utility": offer.score.utility,
            })

        payload = {
            "metadata": {
                "engine_version": "1.0",
                "explanation_version": self.explanation_version,
                "timestamp": datetime.utcnow().isoformat(),
                "round": round_number,
            },
            "request": request_data,
            "vendor": vendor_data,
            "latest_offer": offer_data,
            "history": history_data,
            "opponent_model": opponent_model or {},
            "plan": plan or {},
            "policy_events": policy_events,
            "acceptance_probability": acceptance_probability,
            "decision": decision,
            "competing_offers": competing_offers or [],
            "concession_notes": concession_notes or [],
            "derived_metrics": derived_metrics or {},
        }

        return payload

    def explain_state(
        self,
        request: Request,
        vendor: VendorProfile,
        latest_offer: Offer,
        history: List[Offer],
        round_number: int,
        decision: str,
        acceptance_probability: float,
        policy_events: List[str],
        **kwargs
    ) -> ExplanationRecord:
        """
        Generate an LLM-powered explanation of the current negotiation state.

        This is the main entry point for the explainability service.

        Args:
            request: The procurement request
            vendor: The vendor being negotiated with
            latest_offer: The most recent offer
            history: Last N offers
            round_number: Current negotiation round
            decision: Engine decision
            acceptance_probability: Computed acceptance probability
            policy_events: List of policy enforcement notes
            **kwargs: Additional optional parameters (opponent_model, plan, etc.)

        Returns:
            ExplanationRecord with LLM-generated explanation
        """
        # Build payload
        payload = self.build_payload(
            request=request,
            vendor=vendor,
            latest_offer=latest_offer,
            history=history,
            round_number=round_number,
            decision=decision,
            acceptance_probability=acceptance_probability,
            policy_events=policy_events,
            **kwargs
        )

        # Create user prompt with payload
        user_prompt = f"""Given the negotiation payload below, produce an ExplanationRecord v1 JSON.
Make 'short_summary' first, then 'detailed_explanation', then other fields.
Use clear bullets in 'detailed_explanation' and include 3 prioritized 'recommended_actions'.

Here are some examples to guide your response:
{FEW_SHOT_EXAMPLES}

Now, analyze this negotiation payload:
{json.dumps(payload, indent=2)}

Respond with valid JSON matching the ExplanationRecord schema."""

        # Call LLM
        try:
            response = self.llm_client.complete(
                messages=[
                    {"role": "system", "content": EXPLAINABILITY_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,  # Low temperature for consistency
                max_tokens=1500,
            )

            # Parse JSON response
            content = response["content"]

            # Extract JSON from markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            parsed = json.loads(content)

            # Validate and convert to ExplanationRecord
            explanation = self._validate_and_convert(parsed, payload)

            return explanation

        except Exception as e:
            # Return fallback explanation on LLM failure
            return self._fallback_explanation(
                payload=payload,
                error=str(e),
            )

    def _validate_and_convert(
        self,
        parsed: Dict[str, Any],
        payload: Dict[str, Any],
    ) -> ExplanationRecord:
        """
        Validate LLM output and convert to ExplanationRecord.

        Args:
            parsed: Parsed JSON from LLM
            payload: Original payload for validation

        Returns:
            Validated ExplanationRecord
        """
        # Validate required fields
        required_fields = [
            "explanation_version",
            "short_summary",
            "detailed_explanation",
            "rationale",
            "policy_summary",
            "numeric_snapshots",
            "recommended_actions",
            "confidence",
            "explainability_trace"
        ]

        for field in required_fields:
            if field not in parsed:
                raise ValueError(f"Missing required field: {field}")

        # Validate numeric snapshots against payload
        numeric_snapshots = parsed["numeric_snapshots"]
        derived_metrics = payload.get("derived_metrics", {})

        # Prefer engine-provided numbers
        if "budget_per_unit" in payload["request"] and payload["request"]["budget_per_unit"]:
            numeric_snapshots["budget_per_unit"] = payload["request"]["budget_per_unit"]

        if "latest_unit_price" in payload["latest_offer"]["components"]:
            numeric_snapshots["latest_unit_price"] = payload["latest_offer"]["components"]["unit_price"]

        # Convert to dataclass
        explanation = ExplanationRecord(
            explanation_version=parsed["explanation_version"],
            short_summary=parsed["short_summary"],
            detailed_explanation=parsed["detailed_explanation"],
            rationale=[
                RationaleFact(**item) for item in parsed["rationale"]
            ],
            policy_summary=[
                PolicyEvent(**item) for item in parsed["policy_summary"]
            ],
            numeric_snapshots=NumericSnapshot(**numeric_snapshots),
            recommended_actions=[
                RecommendedAction(**item) for item in parsed["recommended_actions"]
            ],
            confidence=float(parsed["confidence"]),
            explainability_trace=[
                ExplainabilityTrace(**item) for item in parsed["explainability_trace"]
            ],
        )

        return explanation

    def _fallback_explanation(
        self,
        payload: Dict[str, Any],
        error: str,
    ) -> ExplanationRecord:
        """
        Generate deterministic fallback explanation when LLM fails.

        Args:
            payload: Original payload
            error: Error message

        Returns:
            Fallback ExplanationRecord
        """
        latest_offer = payload["latest_offer"]
        request = payload["request"]

        unit_price = latest_offer["components"]["unit_price"]
        budget_per_unit = request.get("budget_per_unit", 0)
        decision = payload["decision"]
        round_num = payload["metadata"]["round"]

        # Generate simple fallback
        short_summary = (
            f"Round {round_num}: Current offer at ${unit_price:.2f}/unit. "
            f"Engine decision: {decision}."
        )

        detailed_explanation = (
            f"Negotiation round {round_num} summary:\n"
            f"- Current unit price: ${unit_price:.2f}\n"
            f"- Budget per unit: ${budget_per_unit:.2f}\n"
            f"- Engine decision: {decision}\n"
            f"- Policy events: {len(payload['policy_events'])} recorded\n\n"
            f"Note: Full LLM explanation unavailable due to error: {error}\n"
            f"This is a deterministic fallback summary."
        )

        return ExplanationRecord(
            explanation_version=self.explanation_version,
            short_summary=short_summary,
            detailed_explanation=detailed_explanation,
            rationale=[
                RationaleFact(
                    fact=f"Current offer: ${unit_price:.2f}/unit",
                    implication="Price information available for review"
                )
            ],
            policy_summary=[
                PolicyEvent(
                    policy_id="llm_fallback",
                    outcome="applied",
                    note=f"LLM explanation failed; using fallback: {error[:100]}"
                )
            ],
            numeric_snapshots=NumericSnapshot(
                latest_unit_price=unit_price,
                budget_per_unit=budget_per_unit,
                tco=latest_offer["score"].get("tco", 0.0) or 0.0,
                tco_vs_budget_pct=0.0,
                acceptance_probability=payload.get("acceptance_probability", 0.0),
            ),
            recommended_actions=[
                RecommendedAction(
                    priority=1,
                    type="escalate_to_human",
                    text="Review negotiation state manually due to explanation service error"
                )
            ],
            confidence=0.3,  # Low confidence for fallback
            explainability_trace=[
                ExplainabilityTrace(
                    step="llm_call_failed",
                    detail=f"Error: {error[:200]}"
                ),
                ExplainabilityTrace(
                    step="fallback_generated",
                    detail="Using deterministic fallback explanation"
                )
            ],
        )
