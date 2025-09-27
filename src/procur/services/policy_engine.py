from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

from ..models import NegotiationMessage, OfferComponents, Request, VendorProfile


@dataclass
class PolicyViolation:
    code: str
    message: str
    blocking: bool = True


@dataclass
class PolicyResult:
    valid: bool
    violations: List[PolicyViolation]

    @classmethod
    def ok(cls) -> "PolicyResult":
        return cls(valid=True, violations=[])


class PolicyEngine:
    """Enforces procurement policies, approvals, and concession guardrails."""

    def validate_request(self, request: Request) -> PolicyResult:
        violations: List[PolicyViolation] = []
        context = request.policy_context
        if context.budget_cap is not None and request.budget_max is not None:
            if request.budget_max > context.budget_cap:
                violations.append(
                    PolicyViolation(
                        code="budget_cap_exceeded",
                        message=f"Budget {request.budget_max} exceeds cap {context.budget_cap}",
                    )
                )
        if context.risk_threshold is not None:
            try:
                risk = float(request.specs.get("risk_score", 0))
                if risk > context.risk_threshold:
                    violations.append(
                        PolicyViolation(
                            code="risk_threshold_exceeded",
                            message=f"Risk {risk} exceeds threshold {context.risk_threshold}",
                        )
                    )
            except (TypeError, ValueError):
                violations.append(
                    PolicyViolation(
                        code="risk_score_invalid",
                        message="Risk score missing or invalid",
                        blocking=True,
                    )
                )
        return PolicyResult(valid=not violations, violations=violations)

    def validate_negotiation_message(
        self, message: NegotiationMessage, *, allowed_concessions: Iterable[str]
    ) -> PolicyResult:
        violations: List[PolicyViolation] = []
        concession_taken = message.machine_rationale.concession_taken
        if concession_taken not in allowed_concessions:
            violations.append(
                PolicyViolation(
                    code="concession_not_allowed",
                    message=f"Concession {concession_taken} is not permitted for this stage",
                )
            )
        if not message.machine_rationale.constraints_respected:
            violations.append(
                PolicyViolation(
                    code="constraints_not_checked",
                    message="Constraints must be listed to confirm compliance",
                )
            )
        return PolicyResult(valid=not violations, violations=violations)

    def validate_offer(
        self,
        request: Request,
        offer: OfferComponents,
        *,
        vendor: Optional[VendorProfile] = None,
        is_buyer_proposal: bool = True,
    ) -> PolicyResult:
        violations: List[PolicyViolation] = []

        budget_cap = request.policy_context.budget_cap or request.budget_max
        if budget_cap is not None:
            projected_spend = offer.unit_price * offer.quantity * (offer.term_months / 12)
            if projected_spend > budget_cap * 1.05:  # allow small buffer
                violations.append(
                    PolicyViolation(
                        code="budget_exceeded",
                        message=f"Projected spend ${projected_spend:,.2f} exceeds cap ${budget_cap:,.2f}",
                    )
                )

        max_term = request.specs.get("max_term_months")
        if max_term and offer.term_months > max_term:
            violations.append(
                PolicyViolation(
                    code="term_too_long",
                    message=f"Term {offer.term_months} exceeds maximum {max_term}",
                )
            )

        if vendor and vendor.guardrails.payment_terms_allowed:
            allowed = set(vendor.guardrails.payment_terms_allowed)
            if offer.payment_terms.value not in allowed:
                violations.append(
                    PolicyViolation(
                        code="payment_terms_not_allowed",
                        message=f"Payment terms {offer.payment_terms.value} not allowed by vendor guardrails",
                    )
                )

        if vendor and vendor.guardrails.price_floor is not None and not is_buyer_proposal:
            floor = vendor.guardrails.price_floor
            if offer.unit_price < floor:
                violations.append(
                    PolicyViolation(
                        code="price_floor_breach",
                        message=f"Counter offer {offer.unit_price} under vendor floor {floor}",
                    )
                )

        min_accept = request.specs.get("minimum_acceptance_price")
        if min_accept and offer.unit_price > min_accept and is_buyer_proposal:
            violations.append(
                PolicyViolation(
                    code="buyer_price_above_minimum",
                    message=f"Buyer proposal {offer.unit_price} exceeds acceptable target {min_accept}",
                    blocking=False,
                )
            )

        return PolicyResult(valid=not violations, violations=violations)

    def determine_approvals(self, request: Request, spend: float) -> List[str]:
        chain = list(request.policy_context.approval_chain)
        if spend > (request.policy_context.budget_cap or spend):
            chain.append("cfo")
        return chain

    def enforce_concession_floor(
        self,
        floor_price: Optional[float],
        proposed_price: float,
    ) -> PolicyResult:
        if floor_price is None:
            return PolicyResult.ok()
        if proposed_price < floor_price:
            return PolicyResult(
                valid=False,
                violations=[
                    PolicyViolation(
                        code="price_floor_breach",
                        message=f"Proposed unit price {proposed_price} under floor {floor_price}",
                    )
                ],
            )
        return PolicyResult.ok()
