from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple

from ..agents import BuyerAgent, BuyerAgentConfig
from ..models import (
    ActorRole,
    Offer,
    OfferComponents,
    OfferScore,
    PaymentTerms,
    Request,
    RequestPolicyContext,
    RequestType,
    RiskLevel,
    VendorGuardrails,
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
from ..services.scoring_service import ScoreWeights
from ..scenarios import Scenario, ScenarioEvaluationTargets, ScenarioRequest, ScenarioSeller
from ..scenarios.library import get_scenario


@dataclass
class ScenarioResult:
    scenario_id: str
    passed: bool
    outcome: str
    savings_amount: float
    savings_pct: float
    rounds: int
    final_offer: Offer
    notes: List[str] = field(default_factory=list)


@dataclass
class RegressionReport:
    results: List[ScenarioResult]

    def passed(self) -> bool:
        return all(result.passed for result in self.results)

    def summary(self) -> Dict[str, object]:
        total = len(self.results)
        passed = sum(1 for result in self.results if result.passed)
        avg_savings_pct = (
            sum(result.savings_pct for result in self.results) / total if total else 0.0
        )
        avg_rounds = sum(result.rounds for result in self.results) / total if total else 0.0
        return {
            "scenarios": total,
            "passed": passed,
            "pass_rate": passed / total if total else 0.0,
            "avg_savings_pct": avg_savings_pct,
            "avg_rounds": avg_rounds,
        }


class RegressionHarness:
    """Executes scenario-driven regression evaluations."""

    def __init__(
        self,
        buyer_agent_factory: Optional[
            Callable[[], tuple[BuyerAgent, "RegressionHarness._Services"]]
        ] = None,
    ) -> None:
        self._buyer_agent_factory = buyer_agent_factory or self._default_buyer_agent_factory

    # region public API
    def run(self, scenario_ids: Sequence[str]) -> RegressionReport:
        results: List[ScenarioResult] = []
        for scenario_id in scenario_ids:
            scenario = get_scenario(scenario_id)
            result = self._run_single_scenario(scenario)
            results.append(result)
        return RegressionReport(results=results)

    def run_curriculum(
        self, phases: Sequence["CurriculumPhase"]
    ) -> Dict[str, RegressionReport]:
        from .curriculum import CurriculumPhase

        reports: Dict[str, RegressionReport] = {}
        for phase in phases:
            if not isinstance(phase, CurriculumPhase):
                raise TypeError("run_curriculum expects CurriculumPhase objects")
            reports[phase.name] = self.run(phase.scenario_ids)
        return reports

    # endregion

    # region scenario execution
    def _run_single_scenario(self, scenario: Scenario) -> ScenarioResult:
        buyer_agent, services = self._buyer_agent_factory()
        request, vendor = self._adapt_scenario(scenario)

        offers = buyer_agent.negotiate(request, [vendor])

        memory = (
            services.memory_service.get_memory(request.request_id, vendor.vendor_id)
            if services.memory_service
            else None
        )
        outcome = memory.outcome if memory else "unknown"
        rounds = self._count_rounds(memory)
        final_offer = offers.get(vendor.vendor_id)
        if not final_offer:
            notes = ["No offer generated"]
            return ScenarioResult(
                scenario_id=scenario.scenario_id,
                passed=False,
                outcome=outcome,
                savings_amount=0.0,
                savings_pct=0.0,
                rounds=rounds,
                final_offer=self._fallback_offer(vendor, request),
                notes=notes,
            )

        metrics = self._calculate_metrics(scenario, final_offer, rounds)
        passed, notes = self._evaluate_thresholds(metrics, scenario.eval_targets, outcome)
        return ScenarioResult(
            scenario_id=scenario.scenario_id,
            passed=passed,
            outcome=outcome,
            savings_amount=metrics["savings_amount"],
            savings_pct=metrics["savings_pct"],
            rounds=rounds,
            final_offer=final_offer,
            notes=notes,
        )

    # endregion

    # region helpers
    @dataclass
    class _Services:
        audit_service: AuditTrailService
        memory_service: MemoryService
        retrieval_service: RetrievalService

    def _default_buyer_agent_factory(self) -> tuple[BuyerAgent, _Services]:
        policy_engine = PolicyEngine()
        compliance_service = ComplianceService(mandatory_certifications=["soc2"])
        guardrail_service = GuardrailService()
        scoring_service = ScoringService(weights=ScoreWeights())
        negotiation_engine = NegotiationEngine(policy_engine, scoring_service)
        explainability_service = ExplainabilityService()
        audit_service = AuditTrailService()
        memory_service = MemoryService()
        retrieval_service = RetrievalService()

        llm_client = self._mock_llm_client()

        buyer_agent = BuyerAgent(
            policy_engine=policy_engine,
            compliance_service=compliance_service,
            guardrail_service=guardrail_service,
            scoring_service=scoring_service,
            negotiation_engine=negotiation_engine,
            explainability_service=explainability_service,
            llm_client=llm_client,
            config=BuyerAgentConfig(),
            audit_service=audit_service,
            memory_service=memory_service,
            retrieval_service=retrieval_service,
        )
        services = self._Services(
            audit_service=audit_service,
            memory_service=memory_service,
            retrieval_service=retrieval_service,
        )
        return buyer_agent, services

    def _mock_llm_client(self):
        class _MockLLMClient:
            def complete(self, messages: List[dict], **kwargs) -> dict:
                import json

                user_message = messages[-1]["content"] if messages else ""
                target_price = 0.0
                if "Target:" in user_message:
                    try:
                        target_price = float(user_message.split("Target: $")[1].split("/unit")[0])
                    except Exception:
                        target_price = 0.0
                proposal = {
                    "unit_price": target_price or 1000.0,
                    "currency": "USD",
                    "quantity": 1,
                    "term_months": 12,
                    "payment_terms": "Net30",
                }
                payload = {
                    "actor": "buyer_agent",
                    "round": 1,
                    "proposal": proposal,
                    "justification_bullets": ["Deterministic mock response"],
                    "machine_rationale": {
                        "score_components": {"price": 0.9},
                        "constraints_respected": ["mock"],
                        "concession_taken": "price",
                    },
                    "next_step_hint": "counter",
                }
                return {"content": json.dumps(payload)}

        return _MockLLMClient()

    def _adapt_scenario(self, scenario: Scenario) -> tuple[Request, VendorProfile]:
        request = self._build_request(scenario.scenario_id, scenario.request)
        vendor = self._build_vendor(scenario.scenario_id, scenario.request, scenario.seller)
        return request, vendor

    def _build_request(self, scenario_id: str, data: ScenarioRequest) -> Request:
        request_type = RequestType.SAAS if "saas" in data.category.lower() else RequestType.GOODS
        budget_per_unit = data.budget_total / max(data.quantity, 1)
        policy_context = RequestPolicyContext(budget_cap=data.budget_total)
        specs = {
            "category": data.category,
            "budget_per_unit": budget_per_unit,
        }
        timeline = f"{data.timeline_days} days" if data.timeline_days else None
        return Request(
            request_id=f"scenario-{scenario_id}",
            requester_id="regression",
            type=request_type,
            description=f"Scenario {scenario_id}",
            specs=specs,
            quantity=data.quantity,
            budget_max=data.budget_total,
            must_haves=data.must_haves,
            compliance_requirements=data.compliance_requirements,
            policy_context=policy_context,
            timeline=timeline,
        )

    def _build_vendor(
        self,
        scenario_id: str,
        request: ScenarioRequest,
        seller: ScenarioSeller,
    ) -> VendorProfile:
        tier_key = str(request.quantity)
        guardrails = VendorGuardrails(
            price_floor=seller.price_floor,
            payment_terms_allowed=list(seller.payment_options),
        )
        capability_tags = [request.category]
        certifications = ["soc2"] if seller.name.lower().startswith("crm") else []
        if "soc2" in request.must_haves and "soc2" not in certifications:
            certifications.append("soc2")
        price_tiers = {tier_key: seller.list_price}
        vendor = VendorProfile(
            vendor_id=f"vendor-{scenario_id.lower()}",
            name=seller.name,
            capability_tags=capability_tags,
            certifications=certifications,
            regions=["us"],
            lead_time_brackets={"default": (30, 45)},
            price_tiers=price_tiers,
            guardrails=guardrails,
            reliability_stats={"sla": 0.99},
            risk_level=RiskLevel.MEDIUM,
            contact_endpoints={"sales": "simulated"},
        )
        return vendor

    def _calculate_metrics(self, scenario: Scenario, offer: Offer, rounds: int) -> Dict[str, float]:
        list_price_total = scenario.seller.list_price * scenario.request.quantity
        final_price_total = offer.components.unit_price * offer.components.quantity
        savings_amount = max(0.0, list_price_total - final_price_total)
        savings_pct = (savings_amount / list_price_total * 100.0) if list_price_total else 0.0
        gap_to_floor = max(
            0.0,
            (offer.components.unit_price - scenario.seller.price_floor) * offer.components.quantity,
        )
        return {
            "savings_amount": savings_amount,
            "savings_pct": savings_pct,
            "gap_to_floor": gap_to_floor,
            "rounds": float(rounds),
        }

    def _evaluate_thresholds(
        self,
        metrics: Dict[str, float],
        targets: ScenarioEvaluationTargets,
        outcome: str,
    ) -> tuple[bool, List[str]]:
        notes: List[str] = []
        passed = True
        if metrics["savings_pct"] < targets.target_savings_pct:
            passed = False
            notes.append(
                f"Savings {metrics['savings_pct']:.2f}% below target {targets.target_savings_pct:.2f}%"
            )
        if metrics["rounds"] > targets.max_rounds:
            passed = False
            notes.append(f"Rounds {metrics['rounds']} exceed max {targets.max_rounds}")
        if metrics["gap_to_floor"] > targets.close_gap_abs:
            passed = False
            notes.append(
                f"Gap to floor ${metrics['gap_to_floor']:.2f} exceeds allowed ${targets.close_gap_abs:.2f}"
            )
        if outcome not in {"accepted", "in_progress"}:
            passed = False
            notes.append(f"Outcome '{outcome}' not successful")
        return passed, notes

    def _count_rounds(self, memory) -> int:
        if not memory:
            return 0
        round_numbers: Set[int] = {round_memory.round_number for round_memory in memory.rounds if round_memory.actor == ActorRole.BUYER_AGENT}
        return len(round_numbers)

    def _fallback_offer(self, vendor: VendorProfile, request: Request) -> Offer:
        components = OfferComponents(
            unit_price=vendor.price_tiers.get(str(request.quantity), vendor.guardrails.price_floor or 0.0),
            currency=request.currency,
            quantity=request.quantity,
            term_months=12,
            payment_terms=PaymentTerms.NET_30,
        )
        dummy_score = OfferScore(spec_match=0, tco=0, risk=0, time=0, utility=0)
        return Offer(
            offer_id="fallback",
            request_id=request.request_id,
            vendor_id=vendor.vendor_id,
            components=components,
            score=dummy_score,
        )

    # endregion


__all__ = ["RegressionHarness", "RegressionReport", "ScenarioResult"]


if __name__ == "__main__":  # pragma: no cover - convenience CLI
    import json

    from ..scenarios import list_scenarios
    from .reporting import build_dashboard

    harness = RegressionHarness()
    report = harness.run(list_scenarios())
    print(json.dumps(build_dashboard(report), indent=2))
