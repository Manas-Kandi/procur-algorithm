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
from ..services.vendor_matching import VendorMatcher
from ..services.compliance_service import ComplianceAssessment
from ..services.scoring_service import ScoreWeights


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
        return Request.model_validate(payload)

    def summarize(self, request: Request) -> Dict[str, object]:
        budget_per_unit = (
            request.budget_max / request.quantity if request.budget_max and request.quantity else None
        )
        return {
            "description": request.description,
            "quantity": request.quantity,
            "budget_total": request.budget_max,
            "budget_per_unit": budget_per_unit,
            "must_haves": request.must_haves,
            "compliance": request.compliance_requirements,
            "specs": request.specs,
        }


class VendorPicker:
    """Ranks seed vendors against the intake request."""

    def __init__(self, compliance_service: ComplianceService) -> None:
        self.compliance_service = compliance_service
        self.matcher = VendorMatcher()

    def pick(self, request: Request, records: Iterable[SeedVendorRecord], top_n: int = 5) -> List[VendorSelection]:
        scored: List[VendorSelection] = []
        budget_per_unit = request.budget_max / request.quantity if request.budget_max and request.quantity > 0 else None

        for record in records:
            # Use enhanced matching with category gating
            match_result = self.matcher.evaluate_vendor(request, record)

            # Skip vendors that don't match category
            if not match_result.category_match:
                continue

            # Skip vendors with very poor feature scores
            if match_result.feature_score < 0.3:
                continue

            vendor_profile = record.to_vendor_profile()
            assessment = self.compliance_service.assess_vendor(request, vendor_profile)

            # Price scoring
            if budget_per_unit:
                price_target = budget_per_unit
                list_price = record.list_price
                price_score = max(0.0, min(price_target / list_price, 1.2))
                price_score = min(price_score, 1.0)
            else:
                price_score = 0.6

            # Enhanced scoring with proper weights
            score = (
                0.5 * match_result.feature_score +      # Feature match is most important
                0.3 * match_result.compliance_score +   # Compliance is critical
                0.2 * price_score                       # Price fit
            )

            # Heavy penalty for blocking compliance issues
            if assessment.blocking:
                score *= 0.1

            reasons = [
                f"Compliance match {int(match_result.compliance_score * len(request.compliance_requirements))}/{len(request.compliance_requirements) or 1}",
                f"Feature match {match_result.feature_hits}/{match_result.total_features}",
                f"List price ${record.list_price:.2f} vs budget {budget_per_unit or 'n/a'}",
            ]

            if match_result.missing_features:
                reasons.append(f"Missing: {', '.join(match_result.missing_features[:2])}")

            if assessment.blocking:
                reasons.append("⚠️ Missing blocking compliance requirement")

            scored.append(VendorSelection(record=record, score=score, reasons=reasons))

        # Sort by score and take top N
        scored.sort(key=lambda entry: entry.score, reverse=True)

        # Filter out very low scores (< 0.4) unless we have too few vendors
        viable_vendors = [v for v in scored if v.score >= 0.4]
        if len(viable_vendors) >= 3:
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
