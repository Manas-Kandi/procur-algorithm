from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from ..models import (
    ActorRole,
    CandidateEvaluation,
    NegotiationDecision,
    Offer,
    OfferComponents,
    Request,
    RoundMemory,
    VendorProfile,
)
from ..services import (
    AuditTrailService,
    ComplianceService,
    ExplainabilityService,
    GuardrailService,
    MemoryService,
    NegotiationEngine,
    PolicyEngine,
    RetrievalService,
    ScoringService,
)
from ..services.guardrail_service import GuardrailAlert
from ..services.negotiation_engine import (
    NegotiationPlan,
    NegotiationStrategy,
    OpponentModel,
    VendorNegotiationState,
)
from ..services.negotiation_engine import SellerStrategy
from ..llm import (
    LLMClient,
    guarded_completion,
    intake_prompt,
    negotiation_prompt,
    parse_negotiation_message,
    parse_request,
)
from ..llm.validators import LLMValidationError
from ..models import NegotiationMessage
from ..models.offer import MachineRationale
from .seller_agent import SellerAgent, SellerAgentConfig
from ..models.enums import PaymentTerms


@dataclass
class BuyerAgentConfig:
    clarifier_limit: int = 5
    concession_ladder: tuple[str, ...] = (
        "multi_year_discount",
        "payment_terms",
        "value_add",
        "price_adjustment",
    )


class BuyerAgent:
    """Outcome-first procurement agent for buyers."""

    def __init__(
        self,
        policy_engine: PolicyEngine,
        compliance_service: ComplianceService,
        guardrail_service: GuardrailService,
        scoring_service: ScoringService,
        negotiation_engine: NegotiationEngine,
        explainability_service: ExplainabilityService,
        llm_client: LLMClient,
        config: BuyerAgentConfig | None = None,
        audit_service: AuditTrailService | None = None,
        memory_service: MemoryService | None = None,
        retrieval_service: RetrievalService | None = None,
        seller_config: SellerAgentConfig | None = None,
    ) -> None:
        self.policy_engine = policy_engine
        self.compliance_service = compliance_service
        self.guardrail_service = guardrail_service
        self.scoring_service = scoring_service
        self.negotiation_engine = negotiation_engine
        self.explainability_service = explainability_service
        self.llm_client = llm_client
        self.config = config or BuyerAgentConfig()
        self.audit_service = audit_service
        self.memory_service = memory_service
        self.retrieval_service = retrieval_service
        self.seller_config = seller_config or SellerAgentConfig()
        self._last_audit_export: Optional[Dict[str, dict]] = None

    def intake_request(self, raw_text: str, policy_summary: str) -> Request:
        messages = intake_prompt(raw_text, policy_summary)
        return guarded_completion(
            lambda: self.llm_client.complete(messages), parser=parse_request
        )

    def shortlist_vendors(
        self, request: Request, vendors: Iterable[VendorProfile]
    ) -> List[VendorProfile]:
        shortlisted: List[VendorProfile] = []
        for vendor in vendors:
            findings = self.compliance_service.evaluate_vendor(request, vendor)
            if any(finding.blocking for finding in findings):
                continue
            shortlisted.append(vendor)
        return shortlisted

    def plan_negotiation(self, request: Request) -> NegotiationPlan:
        anchors = {"price": request.budget_min or 0.0}
        stop_conditions = {"utility": 0.6, "risk": 0.5}
        allowed_concessions = list(self.config.concession_ladder)
        return NegotiationPlan(
            anchors=anchors,
            concession_ladder=list(self.config.concession_ladder),
            stop_conditions=stop_conditions,
            allowed_concessions=allowed_concessions,
        )

    def negotiate(
        self,
        request: Request,
        vendors: List[VendorProfile],
    ) -> Dict[str, Offer]:
        offers: Dict[str, Offer] = {}
        for vendor in vendors:
            state = self._build_state(request, vendor)
            compliance_findings = self.compliance_service.evaluate_vendor(request, vendor)
            compliance_messages = [finding.message for finding in compliance_findings]
            scenario_tags = self._scenario_tags(request, vendor)

            seller_agent = SellerAgent(
                vendor=vendor,
                policy_engine=self.policy_engine,
                scoring_service=self.scoring_service,
                guardrail_service=self.guardrail_service,
                negotiation_engine=self.negotiation_engine,
                config=self.seller_config,
            )

            if self.audit_service:
                self.audit_service.start_session(request.request_id, vendor.vendor_id)
                self.audit_service.record_event(
                    request.request_id,
                    "vendor.negotiation_started",
                    {
                        "vendor_id": vendor.vendor_id,
                        "vendor_name": vendor.name,
                        "compliance_findings": compliance_messages,
                    },
                )
            if self.memory_service:
                self.memory_service.start_session(
                    request.request_id,
                    vendor.vendor_id,
                    scenario_tags=scenario_tags,
                )

            previous_offer = self._baseline_offer(request, vendor)
            final_offer: Optional[Offer] = None
            outcome = "stalemate"
            close_reason = ""
            max_rounds = state.plan.exchange_policy.max_rounds
            round_result: Dict[str, object] = {}

            for round_number in range(1, max_rounds + 1):
                round_result = self._run_round(
                    request=request,
                    state=state,
                    seller_agent=seller_agent,
                    previous_offer=previous_offer,
                    round_number=round_number,
                    compliance_notes=compliance_messages,
                )

                previous_offer = round_result["seller_offer"].components

                decision: NegotiationDecision = round_result["decision"]
                should_close: bool = round_result["should_close"]
                close_reason = round_result["close_reason"]

                if should_close or decision == NegotiationDecision.ACCEPT:
                    final_offer = round_result["seller_offer"]
                    outcome = "accepted"
                    break
                if decision == NegotiationDecision.DROP:
                    final_offer = state.best_offer or round_result["buyer_offer"]
                    outcome = "dropped"
                    break

            if final_offer is None:
                if state.best_offer:
                    final_offer = state.best_offer
                elif round_result:
                    final_offer = round_result["buyer_offer"]

            if final_offer:
                offers[vendor.vendor_id] = final_offer

            if self.audit_service:
                summary = self._build_summary(request, vendor, final_offer, state)
                summary["outcome"] = outcome
                summary["reason"] = close_reason
                self.audit_service.finalize_session(
                    request_id=request.request_id,
                    vendor_id=vendor.vendor_id,
                    outcome=outcome,
                    summary=summary,
                )
            if self.memory_service:
                summary = self._build_summary(request, vendor, final_offer, state)
                self.memory_service.finalize_session(
                    request.request_id,
                    vendor.vendor_id,
                    outcome=outcome,
                    savings=summary.get("savings"),
                )
                if self.retrieval_service:
                    memory = self.memory_service.get_memory(request.request_id, vendor.vendor_id)
                    if memory:
                        self.retrieval_service.register_memory(memory)

        if self.audit_service:
            self._last_audit_export = self.audit_service.export_sessions(request.request_id)

        return offers

    def _build_state(self, request: Request, vendor: VendorProfile) -> VendorNegotiationState:
        plan = self.plan_negotiation(request)
        tier_key = str(request.quantity)
        anchor_price = vendor.price_tiers.get(tier_key, request.budget_max or 0.0)
        plan.anchors["price"] = anchor_price * 0.9 if anchor_price else request.budget_min or 0.0

        opponent_model = OpponentModel(
            price_floor_estimate=(vendor.guardrails.price_floor or anchor_price) * 0.9,
            price_ceiling_estimate=(anchor_price or request.budget_max or 0.0) * 1.1,
        )
        plan.opponent_model = opponent_model
        return VendorNegotiationState(
            vendor=vendor,
            opponent_model=opponent_model,
            plan=plan,
        )

    def _baseline_offer(self, request: Request, vendor: VendorProfile) -> OfferComponents:
        tier_key = str(request.quantity)
        fallback_price = vendor.guardrails.price_floor or (
            (request.budget_max or 0.0) / max(request.quantity, 1)
        )
        list_price = vendor.price_tiers.get(tier_key, fallback_price)
        payment_value = vendor.guardrails.payment_terms_allowed[0] if vendor.guardrails.payment_terms_allowed else PaymentTerms.NET_30.value
        payment_terms = self._resolve_payment_terms(payment_value)
        return OfferComponents(
            unit_price=list_price,
            currency=request.currency,
            quantity=request.quantity,
            term_months=12,
            payment_terms=payment_terms,
        )

    def _resolve_payment_terms(self, value: str | PaymentTerms | None) -> PaymentTerms:
        if isinstance(value, PaymentTerms):
            return value
        if isinstance(value, str):
            try:
                return PaymentTerms(value)
            except ValueError:
                return PaymentTerms.NET_30
        return PaymentTerms.NET_30

    def _assess_bundle(self, bundle, request: Request) -> None:
        bundle.tco = self.negotiation_engine.calculate_tco_for_bundle(bundle, request)
        mock_offer = OfferComponents(
            unit_price=bundle.price,
            currency=request.currency,
            quantity=request.quantity,
            term_months=bundle.term_months,
            payment_terms=bundle.payment_terms,
        )
        bundle.utility = self.negotiation_engine.calculate_utility(mock_offer, request, is_buyer=True)

    def _select_bundle(self, bundles, request: Request):
        for bundle in bundles:
            if bundle.utility == 0:
                self._assess_bundle(bundle, request)
        return max(bundles, key=lambda b: b.utility)

    def _strategy_lever(self, strategy: NegotiationStrategy) -> str:
        return {
            NegotiationStrategy.PRICE_ANCHOR: "price",
            NegotiationStrategy.PRICE_PRESSURE: "price",
            NegotiationStrategy.TERM_TRADE: "term",
            NegotiationStrategy.PAYMENT_TRADE: "payment",
            NegotiationStrategy.VALUE_ADD: "value",
            NegotiationStrategy.ULTIMATUM: "price",
        }[strategy]

    def _seller_lever(self, strategy: SellerStrategy) -> str:
        return {
            SellerStrategy.ANCHOR_HIGH: "price",
            SellerStrategy.REJECT_BELOW_FLOOR: "price",
            SellerStrategy.MINIMAL_CONCESSION: "price",
            SellerStrategy.TERM_VALUE: "term",
            SellerStrategy.PAYMENT_PREMIUM: "payment",
            SellerStrategy.CLOSE_DEAL: "price",
            SellerStrategy.GRADUAL_CONCESSION: "price",
        }[strategy]

    def _bundle_to_components(self, bundle, request: Request) -> OfferComponents:
        components = OfferComponents(
            unit_price=bundle.price,
            currency=request.currency,
            quantity=request.quantity,
            term_months=bundle.term_months,
            payment_terms=bundle.payment_terms,
        )
        if bundle.value_adds:
            components.notes = f"Value adds: {bundle.value_adds}"
        return components

    def _infer_primary_lever(
        self,
        previous: OfferComponents | None,
        current: OfferComponents,
    ) -> str:
        if previous is None:
            return "price"
        if current.term_months != previous.term_months:
            return "term"
        if current.payment_terms != previous.payment_terms:
            return "payment"
        if abs(current.unit_price - previous.unit_price) > 1e-6:
            return "price"
        return "value"

    def _offers_equal(self, a: OfferComponents, b: OfferComponents) -> bool:
        return (
            round(a.unit_price, 2) == round(b.unit_price, 2)
            and a.term_months == b.term_months
            and a.payment_terms == b.payment_terms
            and a.quantity == b.quantity
        )

    def _build_candidate_evaluation(
        self,
        request: Request,
        vendor: VendorProfile,
        components: OfferComponents,
        lever: str,
        *,
        policy_result=None,
        guardrail_alerts=None,
        rationale: Optional[List[str]] = None,
        is_buyer_proposal: bool = True,
    ) -> CandidateEvaluation:
        cloned_offer = components.model_copy(deep=True)
        tco = self.negotiation_engine.calculate_tco(cloned_offer)
        buyer_util = self.negotiation_engine.calculate_utility(cloned_offer, request, is_buyer=True)
        seller_util = self.negotiation_engine.calculate_utility(
            cloned_offer,
            request,
            vendor=vendor,
            is_buyer=False,
        )

        policy_result = policy_result or self.policy_engine.validate_offer(
            request,
            cloned_offer,
            vendor=vendor,
            is_buyer_proposal=is_buyer_proposal,
        )
        guardrail_alerts = guardrail_alerts or self.guardrail_service.vet_offer(vendor, cloned_offer)

        valid = policy_result.valid and not any(alert.blocking for alert in guardrail_alerts)

        return CandidateEvaluation(
            offer=cloned_offer,
            primary_lever=lever,
            tco=tco,
            buyer_utility=buyer_util,
            seller_utility=seller_util,
            valid=valid,
            policy_violations=[violation.message for violation in policy_result.violations],
            guardrail_alerts=[alert.message for alert in guardrail_alerts],
            rationale=list(rationale or []),
        )

    def _bucket_quantity(self, quantity: int) -> str:
        if quantity < 25:
            return "small"
        if quantity < 150:
            return "mid"
        if quantity < 500:
            return "large"
        return "enterprise"

    def _scenario_tags(self, request: Request, vendor: VendorProfile) -> List[str]:
        tags = [f"category:{request.type.value}", f"qty:{self._bucket_quantity(request.quantity)}"]
        if request.must_haves:
            tags.extend(f"must:{tag.lower()}" for tag in request.must_haves)
        tier_key = str(request.quantity)
        list_price = vendor.price_tiers.get(tier_key)
        if list_price:
            tags.append("list_price_known")
        if vendor.guardrails.price_floor:
            floor = vendor.guardrails.price_floor
            tags.append("floor_known")
            if request.budget_max and request.quantity:
                budget_per_unit = request.budget_max / request.quantity
                ratio = budget_per_unit / max(floor, 1.0)
                if ratio <= 1.05:
                    tags.append("budget:tight")
                elif ratio >= 1.25:
                    tags.append("budget:loose")
                else:
                    tags.append("budget:balanced")
        return tags

    def _generate_buyer_message(
        self,
        *,
        request: Request,
        state: VendorNegotiationState,
        strategy: NegotiationStrategy,
        bundle,
        round_number: int,
        previous_offer: OfferComponents | None,
    ) -> Optional[NegotiationMessage]:
        vendor = state.vendor
        target_price = bundle.price
        opponent_floor = (
            state.opponent_model.price_floor_estimate
            if state.opponent_model
            else vendor.guardrails.price_floor or target_price
        )
        vendor_context = {
            "vendor_name": vendor.name,
            "strategy": strategy.value,
            "target_price": target_price,
            "estimated_floor": opponent_floor,
            "round": round_number,
            "guardrails": vendor.guardrails.model_dump(),
            "opening_bundle": {
                "price": bundle.price,
                "term_months": bundle.term_months,
                "payment_terms": bundle.payment_terms.value,
                "value_adds": bundle.value_adds,
            },
            "previous_offer": (
                {
                    "unit_price": previous_offer.unit_price,
                    "term_months": previous_offer.term_months,
                    "payment_terms": previous_offer.payment_terms.value,
                }
                if previous_offer
                else None
            ),
        }

        if self.retrieval_service:
            tags = self._scenario_tags(request, vendor)
            exemplars = self.retrieval_service.exemplar_context(tags, k=3)
            if exemplars:
                vendor_context["exemplars"] = exemplars

        messages = negotiation_prompt(request, vendor_context, strategy.value)
        try:
            negotiation_message = guarded_completion(
                lambda: self.llm_client.complete(messages),
                parser=parse_negotiation_message,
            )
        except (LLMValidationError, Exception):
            return None

        proposal = negotiation_message.proposal
        proposal.quantity = request.quantity
        proposal.currency = request.currency

        if proposal.unit_price <= 0:
            proposal.unit_price = bundle.price
        if proposal.term_months <= 0:
            proposal.term_months = bundle.term_months

        if previous_offer and proposal.unit_price > previous_offer.unit_price:
            proposal.unit_price = max(bundle.price, previous_offer.unit_price - state.plan.exchange_policy.min_step_abs)

        return negotiation_message

    def _create_offer(self, request: Request, vendor: VendorProfile, components: OfferComponents, *, suffix: str) -> Offer:
        score = self.scoring_service.score_offer(vendor, components, request)
        return Offer(
            offer_id=f"{request.request_id}-{vendor.vendor_id}-{suffix}",
            request_id=request.request_id,
            vendor_id=vendor.vendor_id,
            components=components,
            score=score,
        )

    def _policy_notes(self, violations) -> List[str]:
        return [violation.message for violation in violations]

    def _guardrail_notes(self, alerts: List[GuardrailAlert]) -> List[str]:
        return [alert.message for alert in alerts]

    def _run_round(
        self,
        *,
        request: Request,
        state: VendorNegotiationState,
        seller_agent: SellerAgent,
        previous_offer: OfferComponents,
        round_number: int,
        compliance_notes: List[str],
    ) -> Dict[str, object]:
        state.round = round_number
        plan = state.plan or self.plan_negotiation(request)
        policy = plan.exchange_policy

        prev_tco: Optional[float] = None
        prev_buyer_utility: Optional[float] = None
        if previous_offer:
            prev_tco = self.negotiation_engine.calculate_tco(previous_offer)
            prev_buyer_utility = self.negotiation_engine.calculate_utility(previous_offer, request, is_buyer=True)

        if not state.history:
            bundles = self.negotiation_engine.seed_bundles(request, state.vendor, policy)
            for bundle in bundles:
                self._assess_bundle(bundle, request)
            chosen_bundle = self._select_bundle(bundles, request)
            strategy = NegotiationStrategy.PRICE_ANCHOR
        else:
            strategy = self.negotiation_engine.determine_buyer_strategy(state, previous_offer)
            bundles = self.negotiation_engine.generate_multiple_bundles(strategy, request, previous_offer, state)
            chosen_bundle = self._select_bundle(bundles, request)

        plan.current_strategy = strategy
        lever = self._strategy_lever(strategy)

        candidate_evaluations: List[CandidateEvaluation] = []
        for bundle in bundles:
            candidate_components = self._bundle_to_components(bundle, request)
            candidate_lever = self._infer_primary_lever(previous_offer, candidate_components)
            preview_policy = self.policy_engine.validate_offer(
                request,
                candidate_components,
                vendor=state.vendor,
                is_buyer_proposal=True,
            )
            preview_guardrails = self.guardrail_service.vet_offer(state.vendor, candidate_components)
            candidate_evaluations.append(
                self._build_candidate_evaluation(
                    request,
                    state.vendor,
                    candidate_components,
                    candidate_lever,
                    policy_result=preview_policy,
                    guardrail_alerts=preview_guardrails,
                )
            )

        negotiation_message = self._generate_buyer_message(
            request=request,
            state=state,
            strategy=strategy,
            bundle=chosen_bundle,
            round_number=round_number,
            previous_offer=previous_offer,
        )

        if negotiation_message:
            buyer_components = negotiation_message.proposal
        else:
            buyer_components = self._bundle_to_components(chosen_bundle, request)

        exchange_notes = self.negotiation_engine.enforce_exchange_requirements(
            policy,
            previous_offer,
            buyer_components,
            state.vendor,
        )

        buyer_offer = self._create_offer(
            request,
            state.vendor,
            buyer_components,
            suffix=f"buyer-{round_number}",
        )

        policy_adjustment_note: Optional[str] = None
        policy_result = self.policy_engine.validate_offer(
            request,
            buyer_components,
            vendor=state.vendor,
            is_buyer_proposal=True,
        )

        if not policy_result.valid and any(v.blocking for v in policy_result.violations):
            buyer_components = self._bundle_to_components(chosen_bundle, request)
            policy_result = self.policy_engine.validate_offer(
                request,
                buyer_components,
                vendor=state.vendor,
                is_buyer_proposal=True,
            )
            buyer_offer = self._create_offer(
                request,
                state.vendor,
                buyer_components,
                suffix=f"buyer-{round_number}",
            )
            if negotiation_message:
                negotiation_message.proposal = buyer_components
            policy_adjustment_note = "Adjusted to policy-compliant bundle due to blocking violations"
        guardrail_alerts = self.guardrail_service.vet_offer(state.vendor, buyer_components)

        self.negotiation_engine.record_offer(state, buyer_offer)
        buyer_tco = self.negotiation_engine.calculate_tco(buyer_components)
        buyer_utility = self.negotiation_engine.calculate_utility(buyer_components, request, is_buyer=True)
        seller_projection = self.negotiation_engine.calculate_utility(
            buyer_components,
            request,
            vendor=state.vendor,
            is_buyer=False,
        )

        buyer_rationale: List[str]
        if negotiation_message:
            buyer_rationale = list(negotiation_message.justification_bullets)
            machine_rationale = negotiation_message.machine_rationale
        else:
            buyer_rationale = [
                f"Strategy {strategy.value}",
                f"Bundle utility {buyer_utility:.3f}",
                "LLM fallback engaged",
            ]
            machine_rationale = MachineRationale(
                score_components={"utility": buyer_utility},
                constraints_respected=[],
                concession_taken=self._strategy_lever(strategy),
            )
        buyer_rationale.extend(exchange_notes)
        if policy_adjustment_note:
            buyer_rationale.append(policy_adjustment_note)

        selected_evaluation = self._build_candidate_evaluation(
            request,
            state.vendor,
            buyer_components,
            lever,
            policy_result=policy_result,
            guardrail_alerts=guardrail_alerts,
            rationale=buyer_rationale,
            is_buyer_proposal=True,
        )
        rejected_evaluations = [
            eval_item
            for eval_item in candidate_evaluations
            if not self._offers_equal(eval_item.offer, selected_evaluation.offer)
        ]

        delta_utility = (
            selected_evaluation.buyer_utility - prev_buyer_utility
            if prev_buyer_utility is not None
            else selected_evaluation.buyer_utility
        )
        delta_tco = (
            (prev_tco - selected_evaluation.tco) if prev_tco is not None else 0.0
        )

        if self.audit_service:
            self.audit_service.record_move(
                request_id=request.request_id,
                vendor_id=state.vendor.vendor_id,
                actor=ActorRole.BUYER_AGENT,
                round_number=round_number,
                offer=buyer_components,
                lever=lever,
                rationale=buyer_rationale
                + [
                    f"Machine score: {machine_rationale.score_components}",
                    f"Constraints: {machine_rationale.constraints_respected}",
                ],
                buyer_utility=buyer_utility,
                seller_utility=seller_projection,
                tco=buyer_tco,
                decision=NegotiationDecision.COUNTER,
                policy_notes=self._policy_notes(policy_result.violations),
                guardrail_notes=self._guardrail_notes(guardrail_alerts),
                compliance_notes=compliance_notes,
            )

        if state.opponent_model:
            self.negotiation_engine.update_opponent_model(
                state.opponent_model,
                buyer_components,
                previous_offer,
            )

        seller_offer, seller_strategy, seller_guardrails, seller_policy = seller_agent.respond(
            request=request,
            state=state,
            buyer_offer=buyer_components,
            round_number=round_number,
        )

        seller_exchange_notes = self.negotiation_engine.enforce_exchange_requirements(
            policy,
            buyer_components,
            seller_offer.components,
            state.vendor,
        )
        seller_offer.score = self.scoring_service.score_offer(state.vendor, seller_offer.components, request)

        self.negotiation_engine.record_offer(state, seller_offer)

        if state.opponent_model:
            self.negotiation_engine.update_opponent_model(
                state.opponent_model,
                seller_offer.components,
                buyer_components,
            )

        seller_lever = self._seller_lever(seller_strategy)
        seller_tco = self.negotiation_engine.calculate_tco(seller_offer.components)
        seller_utility = self.negotiation_engine.calculate_utility(
            seller_offer.components,
            request,
            vendor=state.vendor,
            is_buyer=False,
        )
        buyer_view = self.negotiation_engine.calculate_utility(
            seller_offer.components,
            request,
            is_buyer=True,
        )

        if self.audit_service:
            self.audit_service.record_move(
                request_id=request.request_id,
                vendor_id=state.vendor.vendor_id,
                actor=ActorRole.SELLER_AGENT,
                round_number=round_number,
                offer=seller_offer.components,
                lever=seller_lever,
                rationale=[f"Strategy {seller_strategy.value}"] + seller_exchange_notes,
                buyer_utility=buyer_view,
                seller_utility=seller_utility,
                tco=seller_tco,
                decision=NegotiationDecision.COUNTER,
                policy_notes=self._policy_notes(seller_policy.violations),
                guardrail_notes=self._guardrail_notes(seller_guardrails),
                compliance_notes=compliance_notes,
            )


        decision = self.negotiation_engine.decide_next_move(plan, state, seller_offer)
        should_close, reason = self.negotiation_engine.should_close_deal(state, seller_offer.components, request)

        seller_evaluation = self._build_candidate_evaluation(
            request,
            state.vendor,
            seller_offer.components,
            seller_lever,
            policy_result=seller_policy,
            guardrail_alerts=seller_guardrails,
            rationale=[f"Strategy {seller_strategy.value}"] + seller_exchange_notes,
            is_buyer_proposal=False,
        )
        seller_delta_utility = seller_evaluation.seller_utility - seller_projection
        seller_delta_tco = buyer_tco - seller_evaluation.tco

        if self.memory_service:
            buyer_round_memory = RoundMemory(
                request_id=request.request_id,
                vendor_id=state.vendor.vendor_id,
                round_number=round_number,
                actor=ActorRole.BUYER_AGENT,
                strategy=strategy.value,
                selected=selected_evaluation,
                rejected=rejected_evaluations,
                decision=decision,
                delta_utility=delta_utility,
                delta_tco=delta_tco,
            )
            seller_round_memory = RoundMemory(
                request_id=request.request_id,
                vendor_id=state.vendor.vendor_id,
                round_number=round_number,
                actor=ActorRole.SELLER_AGENT,
                strategy=seller_strategy.value,
                selected=seller_evaluation,
                rejected=[],
                decision=decision,
                delta_utility=seller_delta_utility,
                delta_tco=seller_delta_tco,
            )
            self.memory_service.record_round(buyer_round_memory)
            self.memory_service.record_round(seller_round_memory)

        return {
            "buyer_offer": buyer_offer,
            "seller_offer": seller_offer,
            "decision": decision,
            "should_close": should_close,
            "close_reason": reason,
        }

    def _build_summary(
        self,
        request: Request,
        vendor: VendorProfile,
        offer: Optional[Offer],
        state: VendorNegotiationState,
    ) -> Dict[str, float]:
        tier_key = str(request.quantity)
        list_price = vendor.price_tiers.get(tier_key, offer.components.unit_price if offer else 0.0)
        clearing_price = offer.components.unit_price if offer else list_price
        savings = max((list_price - clearing_price) * request.quantity, 0.0)
        return {
            "rounds_completed": float(state.round),
            "savings": savings,
        }

    def bundle_and_explain(self, offers: Dict[str, Offer]) -> Dict[str, Dict[str, List[str]]]:
        sorted_offers = sorted(offers.values(), key=lambda o: o.score.utility, reverse=True)
        best_value = sorted_offers[0] if sorted_offers else None
        lowest_cost = min(sorted_offers, key=lambda o: o.components.unit_price, default=None)
        lowest_risk = min(sorted_offers, key=lambda o: o.score.risk, default=None)

        bundles: Dict[str, Offer] = {}
        if best_value:
            bundles["best_value"] = best_value
        if lowest_cost and lowest_cost.offer_id not in {offer.offer_id for offer in bundles.values()}:
            bundles["lowest_cost"] = lowest_cost
        if lowest_risk and lowest_risk.offer_id not in {offer.offer_id for offer in bundles.values()}:
            bundles["lowest_risk"] = lowest_risk

        sensitivities = {
            name: self.scoring_service.sensitivity_analysis(offer.score)
            for name, offer in bundles.items()
        }
        return self.explainability_service.bundle_summary(bundles, sensitivities)

    def export_audit(self) -> Optional[Dict[str, dict]]:
        return self._last_audit_export

    def run(self, raw_text: str, policy_summary: str, vendors: Iterable[VendorProfile]) -> Dict[str, Dict[str, List[str]]]:
        request = self.intake_request(raw_text, policy_summary)
        policy_check = self.policy_engine.validate_request(request)
        if not policy_check.valid:
            raise RuntimeError(f"Policy violations: {policy_check.violations}")
        shortlisted = self.shortlist_vendors(request, vendors)
        offers = self.negotiate(request, shortlisted)
        return self.bundle_and_explain(offers)
