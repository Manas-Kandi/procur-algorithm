from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Tuple

from ..agents import BuyerAgent, BuyerAgentConfig
from ..data import SeedVendorRecord, load_seed_catalog
from datetime import datetime

from ..models import Offer, OfferComponents, Request, RequestType, VendorProfile
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
from ..services.negotiation_engine import ExchangePolicy
from ..services.vendor_matching import evaluate_vendor_against_request, VendorMatchSummary
from ..services.compliance_service import ComplianceAssessment
from ..services.scoring_service import ScoreWeights
from ..utils.pricing import annualize_value, normalize_budget_total, price_fit_ratio


@dataclass
class PipelineServices:
    audit_service: AuditTrailService
    memory_service: MemoryService
    retrieval_service: RetrievalService
    compliance_service: ComplianceService


@dataclass
class ClarificationQuestion:
    field: str
    question: str
    required: bool = True


@dataclass
class VendorSelection:
    record: SeedVendorRecord
    score: float
    reasons: List[str]
    summary: Optional[VendorMatchSummary] = None


@dataclass
class NegotiationResult:
    selection: VendorSelection
    offer: Offer
    compliance: ComplianceAssessment
    audit_log: Dict[str, object]
    memory_log: Dict[str, object]

    @property
    def vendor_id(self) -> str:
        return self.offer.vendor_id


class BuyerIntakeOrchestrator:
    """Handles intake and clarification loop for buyer requests."""

    def __init__(self, buyer_agent: BuyerAgent) -> None:
        self.buyer_agent = buyer_agent
        self._budget_hint = (
            "Typical CRM pricing ranges from roughly $200 to $1,200 per seat annually."
        )

    def run(
        self,
        raw_text: str,
        policy_summary: str,
        clarification_answers: Optional[Dict[str, str]] = None,
    ) -> Tuple[Request, List[ClarificationQuestion]]:
        request = self.buyer_agent.intake_request(raw_text, policy_summary)

        # Ensure budget_max is never None - apply fallback if LLM didn't set it
        if request.budget_max is None:
            quantity = request.quantity or 100
            request = request.model_copy(update={'budget_max': quantity * 1200.0})  # $1200 per user default

        questions = self.generate_questions(request)
        if clarification_answers:
            request = self.apply_answers(request, clarification_answers)
            questions = []
        return request, questions

    def generate_questions(self, request: Request) -> List[ClarificationQuestion]:
        questions: List[ClarificationQuestion] = []
        if not request.budget_max or request.budget_max <= 0:
            questions.append(
                ClarificationQuestion(
                    field="budget_per_unit",
                    question=(
                        "What's your approximate budget per seat per year (or total)? "
                        f"{self._budget_hint}"
                    ),
                )
            )
        if not request.must_haves:
            questions.append(
                ClarificationQuestion(
                    field="must_haves",
                    question="Which features are absolutely required (comma-separated)?",
                )
            )
        if not request.compliance_requirements:
            questions.append(
                ClarificationQuestion(
                    field="compliance_requirements",
                    question="List any compliance frameworks you must enforce (e.g., SOC2, ISO27001)?",
                )
            )
        if not request.billing_cadence:
            questions.append(
                ClarificationQuestion(
                    field="billing_cadence",
                    question="Is your budget per seat per month or per year? (default: per year)",
                    required=False,
                )
            )
        if "features" not in request.specs:
            questions.append(
                ClarificationQuestion(
                    field="specs.features",
                    question="What functional capabilities do you need (comma-separated)?",
                    required=False,
                )
            )
        return questions

    def apply_answers(self, request: Request, answers: Dict[str, str]) -> Request:
        payload = request.model_dump()
        for field, value in answers.items():
            tokens = [item.strip() for item in value.split(",") if item.strip()]
            if field == "must_haves":
                payload["must_haves"] = tokens
            elif field == "compliance_requirements":
                payload["compliance_requirements"] = [token.upper() for token in tokens]
            elif field == "specs.features":
                specs = dict(payload.get("specs", {}))
                specs["features"] = tokens
                payload["specs"] = specs
            elif field == "billing_cadence":
                cadence = value.strip().lower()
                if cadence in {"monthly", "per month", "month", "per-seat per month", "per seat per month"}:
                    payload["billing_cadence"] = "per_seat_per_month"
                elif cadence in {"yearly", "annual", "per year", "year"}:
                    payload["billing_cadence"] = "per_seat_per_year"
                elif cadence:
                    payload["billing_cadence"] = cadence
                specs = dict(payload.get("specs", {}))
                specs["billing_cadence"] = payload.get("billing_cadence")
                payload["specs"] = specs
            elif field == "budget_per_unit":
                total, per_unit, cadence = self._parse_budget_answer(value, request.quantity)
                specs = dict(payload.get("specs", {}))
                for key in (
                    "_budget_normalized",
                    "_raw_budget_max",
                    "_normalized_cadence",
                    "_raw_billing_cadence",
                    "_raw_budget_min",
                ):
                    specs.pop(key, None)
                if cadence:
                    payload["billing_cadence"] = cadence
                    specs["billing_cadence"] = cadence
                if per_unit is not None and request.quantity:
                    specs["target_unit_budget"] = per_unit
                payload["specs"] = specs
                if total is not None:
                    payload["budget_max"] = total
                if total is not None and total > 0:
                    payload.setdefault("budget_min", None)
        return Request.model_validate(payload)

    def _parse_budget_answer(
        self, value: str, quantity: Optional[int]
    ) -> Tuple[Optional[float], Optional[float], Optional[str]]:
        text = (value or "").strip()
        if not text:
            return None, None, None

        cleaned = text.replace(",", "")
        lower = text.lower()
        search_base = cleaned.lower()
        matches = list(
            re.finditer(r"(\$)?(\d+(?:\.\d+)?)(?:\s*(k|m))?", cleaned, re.IGNORECASE)
        )
        if not matches:
            return None, None, None

        selected_value: Optional[float] = None
        selected_suffix: Optional[str] = None
        for match in reversed(matches):
            number_str = match.group(2)
            suffix = (match.group(3) or "").lower()
            try:
                candidate = float(number_str)
            except ValueError:
                continue

            context = search_base[max(0, match.start() - 12) : match.end() + 12]
            if "month" in context and "per month" not in context and "per-seat" not in context and "per user" not in context:
                # Likely a duration reference (e.g., "12 months")
                continue
            if quantity and suffix == "" and abs(candidate - quantity) < 1e-6:
                # Probably restating seat count, not budget
                continue

            selected_value = candidate
            selected_suffix = suffix
            break

        if selected_value is None:
            number_str, suffix = matches[-1].group(2), (matches[-1].group(3) or "").lower()
            try:
                selected_value = float(number_str)
                selected_suffix = suffix
            except ValueError:
                return None, None, None

        multiplier = 1.0
        if selected_suffix == "k":
            multiplier = 1_000.0
        elif selected_suffix == "m":
            multiplier = 1_000_000.0

        amount = selected_value * multiplier
        if amount <= 0:
            return None, None, None

        cadence: Optional[str] = None
        if "per month" in search_base or "monthly" in search_base or "/mo" in search_base:
            cadence = "per_seat_per_month"
        elif "per year" in search_base or "annual" in search_base or "yearly" in search_base or "/yr" in search_base:
            cadence = "per_seat_per_year"

        seat_phrases = [
            "per seat",
            "per user",
            "per-person",
            "per person",
            "per employee",
            "per licence",
            "per license",
        ]
        is_per_seat = any(phrase in lower for phrase in seat_phrases)
        if not is_per_seat:
            is_per_seat = any(phrase in search_base for phrase in seat_phrases)

        if is_per_seat:
            if cadence is None:
                cadence = "per_seat_per_year"
            total = amount * (quantity or 1)
            per_unit = amount
        else:
            total = amount
            per_unit = (total / quantity) if quantity else None

        return total, per_unit, cadence

    def summarize(self, request: Request) -> Dict[str, object]:
        normalized_total = request.budget_max
        raw_total = request.specs.get("_raw_budget_max", normalized_total)
        quantity = request.quantity or 0

        budget_per_unit_input = raw_total / quantity if raw_total and quantity else None
        budget_per_unit_normalized = (
            normalized_total / quantity if normalized_total and quantity else None
        )
        input_cadence = request.specs.get("_raw_billing_cadence") or request.billing_cadence
        annual_per_unit = annualize_value(budget_per_unit_input, input_cadence)
        return {
            "description": request.description,
            "quantity": request.quantity,
            "budget_total": normalized_total,
            "budget_total_input": raw_total,
            "budget_per_unit": budget_per_unit_input,
            "budget_per_unit_normalized": budget_per_unit_normalized,
            "budget_per_unit_annual": annual_per_unit,
            "budget_per_unit_provided": request.specs.get("target_unit_budget"),
            "billing_cadence": input_cadence,
            "must_haves": request.must_haves,
            "compliance": request.compliance_requirements,
            "specs": request.specs,
        }

    def normalize_budget(self, request: Request) -> Request:
        specs = dict(request.specs)
        if specs.get("_budget_normalized"):
            return request

        cadence = request.billing_cadence or specs.get("billing_cadence")
        if not cadence:
            return request

        normalized_max = normalize_budget_total(request.budget_max, cadence)
        normalized_min = normalize_budget_total(request.budget_min, cadence)

        specs["_budget_normalized"] = True
        specs["_raw_billing_cadence"] = cadence
        if request.budget_max is not None:
            specs.setdefault("_raw_budget_max", request.budget_max)
        if request.budget_min is not None:
            specs.setdefault("_raw_budget_min", request.budget_min)
        specs["_normalized_cadence"] = "per_seat_per_year"
        specs.setdefault("billing_cadence", cadence)

        return request.model_copy(
            update={
                "budget_max": normalized_max,
                "budget_min": normalized_min,
                "specs": specs,
            }
        )


class VendorPicker:
    """Ranks seed vendors against the intake request."""

    def __init__(self, compliance_service: ComplianceService) -> None:
        self.compliance_service = compliance_service
        self._skip_reasons: List[Dict[str, object]] = []

    @property
    def skip_reasons(self) -> List[Dict[str, object]]:
        return list(self._skip_reasons)

    def pick(self, request: Request, records: Iterable[SeedVendorRecord], top_n: int = 5) -> List[VendorSelection]:
        scored: List[VendorSelection] = []
        self._skip_reasons = []

        # Use the normalized budget per-seat that's already annualized
        budget_per_unit_annual = None
        if request.budget_max and request.quantity:
            # request.budget_max is already normalized to per_seat_per_year
            budget_per_unit_annual = request.budget_max / request.quantity

        for record in records:
            # Use only evaluate_vendor_against_request to compute VendorMatchSummary
            summary = evaluate_vendor_against_request(
                request,
                record,
                budget_per_unit=budget_per_unit_annual,
            )

            # Gate vendors: category_match == True, feature.score > 0, compliance.blocking == False
            if not summary.category_match:
                self._skip_reasons.append({
                    "vendor_id": record.seed_id,
                    "name": record.name,
                    "reason": "category_mismatch",
                    "category": record.category,
                    "request_category": summary.request_category,
                })
                continue
            if summary.feature.score == 0.0:
                self._skip_reasons.append({
                    "vendor_id": record.seed_id,
                    "name": record.name,
                    "reason": "features_insufficient",
                    "missing_features": summary.feature.missing,
                })
                continue
            if summary.compliance.blocking:
                self._skip_reasons.append({
                    "vendor_id": record.seed_id,
                    "name": record.name,
                    "reason": "compliance_blocking",
                    "missing_compliance": [
                        {
                            "framework": status.framework,
                            "evidence": status.evidence,
                            "score": status.score,
                            "verified": status.verified,
                        }
                        for status in summary.compliance.frameworks
                    ],
                })
                continue

            # Use summary.composite_score() for ranking
            composite_score = summary.composite_score()
            if composite_score <= 0:
                self._skip_reasons.append({
                    "vendor_id": record.seed_id,
                    "name": record.name,
                    "reason": "score_non_positive",
                    "details": {
                        "composite_score": composite_score,
                        "feature_score": summary.feature.score,
                        "compliance_score": summary.compliance.score,
                        "price_fit": summary.price_fit,
                    },
                })
                continue

            # Build reasons from summary only
            reasons = [
                f"Feature score {summary.feature.score:.2f}",
                f"Compliance score {summary.compliance.score:.2f}",
                f"Price fit {summary.price_fit:.2f} — annual list ${record.list_price:.2f} vs budget ${budget_per_unit_annual or 'n/a'}"
            ]

            if summary.feature.missing:
                reasons.append(f"Missing: {', '.join(summary.feature.missing)}")

            # Check for blocking compliance separately and add warning if needed
            # Append one VendorSelection per vendor, not two
            scored.append(
                VendorSelection(record=record, score=composite_score, reasons=reasons, summary=summary)
            )

        # Sort by score and take top N (deterministic ordering)
        scored.sort(key=lambda entry: (entry.score, entry.record.seed_id), reverse=True)

        # Filter out very low scores (< 0.4) unless we have too few vendors
        viable_vendors = [v for v in scored if v.score >= 0.4]
        if len(viable_vendors) >= 3:
            demoted = [entry for entry in scored if entry.score < 0.4]
            for entry in demoted:
                self._skip_reasons.append({
                    "vendor_id": entry.record.seed_id,
                    "name": entry.record.name,
                    "reason": "score_below_threshold",
                    "details": {"score": entry.score},
                })
            scored = viable_vendors

        return scored[:top_n]


class NegotiationManager:
    """Executes negotiations for selected vendors using the buyer agent."""

    def __init__(
        self,
        buyer_agent: BuyerAgent,
        services: PipelineServices,
    ) -> None:
        self.buyer_agent = buyer_agent
        self.services = services

    def run(
        self,
        request: Request,
        selections: List[VendorSelection],
    ) -> Dict[str, NegotiationResult]:
        vendor_profiles: List[VendorProfile] = []
        record_map: Dict[str, VendorSelection] = {}
        profile_map: Dict[str, VendorProfile] = {}
        for selection in selections:
            vendor_profile = selection.record.to_vendor_profile()
            # Attach per-seed metadata for downstream plan adjustments
            setattr(vendor_profile, "_exchange_policy", selection.record.exchange_policy)
            setattr(vendor_profile, "_seed_metadata", selection.record.raw)
            if selection.summary:
                setattr(vendor_profile, "_match_summary", selection.summary)

            exchange_policy = getattr(vendor_profile, "_exchange_policy", None)
            if not self.buyer_agent.negotiation_engine.feasible_with_trades(
                request, vendor_profile, exchange_policy or ExchangePolicy()
            ):
                note = "No viable price band under current budget — negotiation skipped"
                if note not in selection.reasons:
                    selection.reasons.append(note)
                continue

            vendor_profiles.append(vendor_profile)
            record_map[vendor_profile.vendor_id] = selection
            profile_map[vendor_profile.vendor_id] = vendor_profile

        offers = self.buyer_agent.negotiate(request, vendor_profiles)
        results: Dict[str, NegotiationResult] = {}
        audit_payload = self.services.audit_service.export_sessions(request.request_id)

        for vendor_id, offer in offers.items():
            selection = record_map.get(vendor_id)
            if not selection:
                continue
            vendor_profile = profile_map.get(vendor_id, selection.record.to_vendor_profile())
            compliance = self.services.compliance_service.assess_vendor(
                request, vendor_profile
            )
            memory = self.services.memory_service.get_memory(request.request_id, vendor_id)
            memory_dump = memory.model_dump() if memory else {}
            vendor_audit = audit_payload["round_logs"].get(vendor_id, {}) if audit_payload else {}
            results[vendor_id] = NegotiationResult(
                selection=selection,
                offer=offer,
                compliance=compliance,
                audit_log=vendor_audit,
                memory_log=memory_dump,
            )
        return results


class PresentationBuilder:
    """Creates human-friendly summaries from negotiation results."""

    def __init__(self, buyer_agent: BuyerAgent) -> None:
        self.buyer_agent = buyer_agent

    def build(self, offers: Dict[str, Offer]) -> Dict[str, Dict[str, List[str]]]:
        if not offers:
            return {}
        return self.buyer_agent.bundle_and_explain(offers)

    def compile_vendor_summary(
        self,
        negotiations: Dict[str, NegotiationResult],
    ) -> List[Dict[str, object]]:
        summaries: List[Dict[str, object]] = []
        for vendor_id, result in negotiations.items():
            offer_components = result.offer.components
            summaries.append(
                {
                    "vendor_id": vendor_id,
                    "vendor_name": result.selection.record.name,
                    "final_price": offer_components.unit_price,
                    "term_months": offer_components.term_months,
                    "payment_terms": offer_components.payment_terms.value,
                    "compliance_status": result.compliance.summaries(),
                    "support": result.selection.record.support,
                    "behavior_profile": result.selection.record.behavior_profile,
                    "audit_summary": result.audit_log,
                    "memory_log": result.memory_log,
                }
            )
        return summaries


class SaaSProcurementPipeline:
    """High-level pipeline that goes from intake to shortlisting and negotiation."""

    def __init__(
        self,
        seeds_path: str | Path,
        buyer_agent_factory: Optional[Callable[[], Tuple[BuyerAgent, PipelineServices]]] = None,
    ) -> None:
        self.seeds_path = Path(seeds_path)
        self._buyer_agent_factory = buyer_agent_factory or self._default_buyer_agent_factory

    def run(
        self,
        raw_text: str,
        policy_summary: str,
        clarification_answers: Optional[Dict[str, str]] = None,
        top_n: int = 5,
    ) -> Dict[str, object]:
        buyer_agent, services = self._buyer_agent_factory()

        intake = BuyerIntakeOrchestrator(buyer_agent)
        request, questions = intake.run(raw_text, policy_summary, clarification_answers)
        request = intake.normalize_budget(request)

        selections, negotiation_results, audit_payload, offers = self._execute(
            buyer_agent, services, request, top_n=top_n
        )

        presentation = PresentationBuilder(buyer_agent)
        bundles = presentation.build(offers)
        vendor_summary = presentation.compile_vendor_summary(negotiation_results)
        vendor_summary = [self._json_safe(summary) for summary in vendor_summary]
        bundles = self._json_safe(bundles)

        return {
            "request": intake.summarize(request),
            "clarification_questions": [
                {
                    "field": question.field,
                    "question": question.question,
                    "required": question.required,
                }
                for question in questions
            ],
            "shortlist": [
                {
                    "vendor_id": selection.record.seed_id,
                    "name": selection.record.name,
                    "score": selection.score,
                    "reasons": selection.reasons,
                }
                for selection in selections
            ],
            "bundles": bundles,
            "vendors": vendor_summary,
            "audit": self._json_safe(audit_payload),
        }

    def _execute(
        self,
        buyer_agent: BuyerAgent,
        services: PipelineServices,
        request: Request,
        *,
        top_n: int,
    ) -> Dict[str, NegotiationResult]:
        seed_records = load_seed_catalog(self.seeds_path)
        picker = VendorPicker(services.compliance_service)
        selections = picker.pick(request, seed_records, top_n=top_n)
        if not selections:
            services.audit_service.record_event(
                request.request_id,
                "shortlist_empty",
                {
                    "skipped_vendors": picker.skip_reasons,
                    "request_must_haves": request.must_haves,
                    "request_compliance": request.compliance_requirements,
                },
            )
        negotiation_manager = NegotiationManager(buyer_agent, services)
        negotiation_results = negotiation_manager.run(request, selections)
        audit_payload = services.audit_service.export_sessions(request.request_id)
        return selections, negotiation_results, audit_payload, {
            vendor_id: result.offer for vendor_id, result in negotiation_results.items()
        }

    # region factories
    def _default_buyer_agent_factory(self) -> Tuple[BuyerAgent, PipelineServices]:
        policy_engine = PolicyEngine()
        compliance_service = ComplianceService(mandatory_certifications=["soc2"])
        guardrail_service = GuardrailService(run_mode="simulation")
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
        services = PipelineServices(
            audit_service=audit_service,
            memory_service=memory_service,
            retrieval_service=retrieval_service,
            compliance_service=compliance_service,
        )
        return buyer_agent, services

    def _mock_llm_client(self):
        class _MockLLMClient:
            def complete(self, messages: List[dict], **kwargs) -> dict:
                content_blob = " ".join(msg.get("content", "") for msg in messages)
                if "procurement intake assistant" in content_blob.lower():
                    user_message = messages[-1]["content"] if messages else ""
                    quantity = self._extract_quantity(user_message)
                    budget_total = self._extract_budget(user_message)
                    features = self._extract_tokens(user_message, ["analytics", "mobile", "api", "sso", "crm"])
                    payload = {
                        "request_id": "req-demo",
                        "requester_id": "user-demo",
                        "type": RequestType.SAAS.value,
                        "description": user_message[:200],
                        "specs": {"features": features},
                        "quantity": quantity,
                        "budget_max": budget_total,
                        "currency": "USD",
                        "billing_cadence": "per_seat_per_year",
                        "must_haves": [],
                        "compliance_requirements": [],
                    }
                    return {"content": json.dumps(payload)}

                user_message = messages[-1]["content"] if messages else ""
                target_price = 0.0
                match = re.search(r"Target: \$(\d+(?:\.\d+)?)", user_message)
                if match:
                    target_price = float(match.group(1))
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

            @staticmethod
            def _extract_quantity(text: str) -> int:
                match = re.search(r"(\d{2,4})\s*(?:users|seats|reps|employees|staff)", text, re.IGNORECASE)
                if match:
                    return int(match.group(1))
                default_match = re.search(r"(\d{2,4})", text)
                if default_match:
                    return int(default_match.group(1))
                return 100

            @staticmethod
            def _extract_budget(text: str) -> float:
                match = re.search(r"\$([\d,]+)(?:\s*k)?", text, re.IGNORECASE)
                if match:
                    value = match.group(1).replace(",", "")
                    amount = float(value)
                    if re.search(r"k\b", text.lower()):
                        amount *= 1000
                    return amount
                return 120000.0

            @staticmethod
            def _extract_tokens(text: str, candidates: List[str]) -> List[str]:
                lowered = text.lower()
                return [token for token in candidates if token in lowered]

        return _MockLLMClient()

    # endregion

    def _json_safe(self, payload):
        if isinstance(payload, dict):
            return {key: self._json_safe(value) for key, value in payload.items()}
        if isinstance(payload, list):
            return [self._json_safe(item) for item in payload]
        if isinstance(payload, datetime):
            return payload.isoformat()
        if isinstance(payload, Enum):
            return payload.value
        return payload


__all__ = ["SaaSProcurementPipeline", "BuyerIntakeOrchestrator", "VendorPicker", "NegotiationManager", "PresentationBuilder"]
