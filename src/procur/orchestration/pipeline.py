from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Tuple
from base64 import b64encode
import logging

from ..agents import BuyerAgent, BuyerAgentConfig
from ..data import SeedVendorRecord, load_seed_catalog

from ..analytics import ProcurementAnalytics
from ..config import ProcurementConfig
from ..integrations import (
    DocuSignIntegration,
    ERPIntegration,
    SlackIntegration,
    VendorDataScraper,
)
from ..models import Offer, OfferComponents, Request, RequestType, VendorProfile
from ..models.enums import PaymentTerms
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
from ..services.negotiation_engine import ExchangePolicy, ConcessionEngine
from ..services.contract_generator import ContractGenerator, ContractGenerationError
from ..services.vendor_matching import evaluate_vendor_against_request, VendorMatchSummary
from ..services.compliance_service import ComplianceAssessment
from ..services.scoring_service import ScoreWeights
from ..utils.pricing import annualize_value, normalize_budget_total, price_fit_ratio
from ..utils.input_sanitizer import (
    collect_allowed_feature_canonicals,
    sanitize_comma_separated_features,
    sanitize_simple_list,
)
logger = logging.getLogger(__name__)

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
        self._input_prefixes = ("processing your request...",)
        self._allowed_features = collect_allowed_feature_canonicals()

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
        sanitized_inputs = dict(payload.get("specs", {}).get("_sanitized_inputs", {}))
        for field, value in answers.items():
            if field == "must_haves":
                tokens, metadata = sanitize_comma_separated_features(
                    value,
                    remove_prefixes=self._input_prefixes,
                    allowed_features=self._allowed_features,
                )
                payload["must_haves"] = tokens
                sanitized_inputs["must_haves"] = metadata
                continue
            tokens = [item.strip() for item in value.split(",") if item.strip()]
            if field == "must_haves":
                payload["must_haves"] = tokens
            elif field == "compliance_requirements":
                cleaned, metadata = sanitize_simple_list(
                    value, remove_prefixes=self._input_prefixes
                )
                payload["compliance_requirements"] = [token.upper() for token in cleaned]
                if metadata["removed_prefixes"] or metadata["dropped_tokens"]:
                    sanitized_inputs["compliance_requirements"] = metadata
            elif field == "specs.features":
                features, metadata = sanitize_comma_separated_features(
                    value,
                    remove_prefixes=self._input_prefixes,
                    allowed_features=self._allowed_features,
                )
                specs = dict(payload.get("specs", {}))
                specs["features"] = features
                payload["specs"] = specs
                sanitized_inputs["specs.features"] = metadata
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
        if sanitized_inputs:
            specs = dict(payload.get("specs", {}))
            specs["_sanitized_inputs"] = sanitized_inputs
            payload["specs"] = specs
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
            policy = exchange_policy or ExchangePolicy()
            if not self.buyer_agent.negotiation_engine.feasible_with_trades(
                request, vendor_profile, policy
            ):
                budget_per_unit = (
                    (request.budget_max / request.quantity)
                    if request.budget_max and request.quantity
                    else None
                )
                seller_floor = vendor_profile.guardrails.price_floor
                estimated_min_price = None
                if request.quantity:
                    concessions = ConcessionEngine(
                        {
                            "term_trade": policy.term_trade,
                            "payment_trade": {
                                term.value: pct for term, pct in policy.payment_trade.items()
                            },
                            "value_add_offsets": policy.value_add_offsets,
                        }
                    )
                    list_price = selection.record.list_price
                    floor_price = seller_floor or list_price
                    estimated_min_price, _ = concessions.best_effective_price(
                        list_price=list_price,
                        floor_price=floor_price,
                        seats=request.quantity,
                    )

                if seller_floor and budget_per_unit and seller_floor > budget_per_unit:
                    note = (
                        f"Seller floor ${seller_floor:.2f} exceeds budget ${budget_per_unit:.2f} — negotiation skipped"
                    )
                elif estimated_min_price and budget_per_unit and estimated_min_price > budget_per_unit:
                    note = (
                        f"Best projected price with concessions ${estimated_min_price:.2f} exceeds budget ${budget_per_unit:.2f}"
                    )
                else:
                    note = "No evidence of viable price band under current budget"
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
        seeds_path: str | Path | None = None,
        *,
        config: ProcurementConfig | None = None,
        vendor_scraper: VendorDataScraper | None = None,
        analytics: ProcurementAnalytics | None = None,
        contract_generator: ContractGenerator | None = None,
        slack_integration: SlackIntegration | None = None,
        docusign_integration: DocuSignIntegration | None = None,
        erp_integration: ERPIntegration | None = None,
        buyer_agent_factory: Optional[Callable[[], Tuple[BuyerAgent, PipelineServices]]] = None,
    ) -> None:
        self.config = config or ProcurementConfig()
        resolved_path = Path(seeds_path) if seeds_path else self.config.seed_path
        self.seeds_path = resolved_path.expanduser().resolve()
        self.vendor_scraper = vendor_scraper or (
            VendorDataScraper() if self.config.enable_live_enrichment else None
        )
        self.analytics = analytics if analytics is not None else (
            ProcurementAnalytics() if self.config.analytics_enabled else None
        )
        self.contract_generator = contract_generator or ContractGenerator(
            template_path=Path(self.config.contract_template_path).expanduser().resolve()
            if self.config.contract_template_path
            else None
        )
        self.slack_integration = slack_integration or (
            SlackIntegration(
                webhook_url=self.config.slack_webhook_url,
                bot_token=self.config.slack_bot_token,
            )
            if (self.config.slack_webhook_url or self.config.slack_bot_token)
            else None
        )
        self.docusign_integration = docusign_integration or (
            DocuSignIntegration(
                api_base=self.config.docusign_api_base,
                integration_key=self.config.docusign_integration_key,
            )
            if self.config.docusign_integration_key
            else None
        )
        self.erp_integration = erp_integration or (
            ERPIntegration(
                api_base=self.config.erp_api_base,
                api_key=self.config.erp_api_key,
            )
            if self.config.erp_api_base and self.config.erp_api_key
            else None
        )
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

        (
            selections,
            negotiation_results,
            audit_payload,
            offers,
            shortlist_notice,
        ) = self._execute(
            buyer_agent, services, request, top_n=top_n
        )

        presentation = PresentationBuilder(buyer_agent)
        bundles = presentation.build(offers)
        vendor_summary = presentation.compile_vendor_summary(negotiation_results)
        vendor_summary = [self._json_safe(summary) for summary in vendor_summary]
        bundles = self._json_safe(bundles)

        contracts = self._generate_contracts(request, negotiation_results)
        encoded_contracts = {
            vendor_id: b64encode(content).decode("utf-8")
            for vendor_id, content in contracts.items()
        }
        analytics_payload = self._build_analytics_payload(negotiation_results)
        integration_report = self._dispatch_integrations(request, negotiation_results, contracts)

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
            "shortlist_notice": shortlist_notice,
            "contracts": encoded_contracts,
            "analytics": analytics_payload,
            "integrations": integration_report,
        }

    def _execute(
        self,
        buyer_agent: BuyerAgent,
        services: PipelineServices,
        request: Request,
        *,
        top_n: int,
    ) -> Tuple[List[VendorSelection], Dict[str, NegotiationResult], Dict[str, dict], Dict[str, Offer], Optional[Dict[str, object]]]:
        seed_records = load_seed_catalog(self.seeds_path)
        if self.vendor_scraper and self.config.enable_live_enrichment:
            category = self._resolve_category(request)
            scraped_profiles = self.vendor_scraper.scrape_g2_data(category)
            enriched_profiles = [
                self.vendor_scraper.enrich_with_compliance_data(profile)
                for profile in scraped_profiles
            ]
            refreshed_profiles: List[VendorProfile] = []
            for profile in enriched_profiles:
                try:
                    refreshed_profiles.append(
                        self.vendor_scraper.update_pricing_from_websites(profile.vendor_id)
                    )
                except Exception:
                    refreshed_profiles.append(profile)
            enriched_records = self._profiles_to_seed_records(refreshed_profiles)
            if enriched_records:
                existing_ids = {record.seed_id for record in seed_records}
                for record in enriched_records:
                    if record.seed_id in existing_ids:
                        continue
                    seed_records.append(record)
                    existing_ids.add(record.seed_id)
        picker = VendorPicker(services.compliance_service)
        selections = picker.pick(request, seed_records, top_n=top_n)
        shortlist_notice: Optional[Dict[str, object]] = None

        if not selections and picker.skip_reasons and all(
            reason.get("reason") == "category_mismatch" for reason in picker.skip_reasons
        ):
            category_inference = request.specs.get("_category_inference", {}) if request.specs else {}
            suggested = category_inference.get("final")
            before = category_inference.get("before")
            if suggested and suggested != before:
                specs = dict(request.specs)
                specs["_category_override"] = suggested
                request = request.model_copy(update={"specs": specs})
                services.audit_service.record_event(
                    request.request_id,
                    "category_autocorrected",
                    {
                        "from": before,
                        "to": suggested,
                        "signals": category_inference.get("signals", {}),
                    },
                )
                shortlist_notice = {
                    "message": f"Category auto-corrected from '{before}' to '{suggested}' based on feature signals",
                    "from": before,
                    "to": suggested,
                }
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
        return (
            selections,
            negotiation_results,
            audit_payload,
            {vendor_id: result.offer for vendor_id, result in negotiation_results.items()},
            shortlist_notice,
        )

    # region factories
    def _default_buyer_agent_factory(self) -> Tuple[BuyerAgent, PipelineServices]:
        policy_engine = PolicyEngine()
        compliance_service = ComplianceService(
            mandatory_certifications=[cert.lower() for cert in self.config.mandatory_certifications]
        )
        guardrail_service = GuardrailService(run_mode="simulation")
        scoring_service = ScoringService(weights=self.config.to_score_weights())
        stalled_rounds = max(2, min(self.config.max_negotiation_rounds // 2, 5))
        negotiation_engine = NegotiationEngine(
            policy_engine,
            scoring_service,
            buyer_accept_threshold=self.config.buyer_accept_threshold,
            seller_accept_threshold=self.config.seller_accept_threshold,
            max_stalled_rounds=stalled_rounds,
        )
        explainability_service = ExplainabilityService()
        audit_service = AuditTrailService()
        memory_service = MemoryService()
        retrieval_service = RetrievalService()

        llm_client = self._mock_llm_client()

        buyer_config = BuyerAgentConfig()
        setattr(buyer_config, "max_rounds", self.config.max_negotiation_rounds)

        buyer_agent = BuyerAgent(
            policy_engine=policy_engine,
            compliance_service=compliance_service,
            guardrail_service=guardrail_service,
            scoring_service=scoring_service,
            negotiation_engine=negotiation_engine,
            explainability_service=explainability_service,
            llm_client=llm_client,
            config=buyer_config,
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

    def _generate_contracts(
        self,
        request: Request,
        negotiations: Dict[str, NegotiationResult],
    ) -> Dict[str, bytes]:
        if not self.contract_generator:
            return {}
        contracts: Dict[str, bytes] = {}
        for vendor_id, result in negotiations.items():
            offer = result.offer
            if not offer or not offer.accepted:
                continue
            try:
                contracts[vendor_id] = self.contract_generator.generate_contract(offer, request)
            except ContractGenerationError as exc:
                logger.warning("Contract generation failed for %s: %s", vendor_id, exc)
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("Unexpected contract error for %s: %s", vendor_id, exc)
        return contracts

    def _build_analytics_payload(self, negotiations: Dict[str, NegotiationResult]) -> Dict[str, object]:
        if not negotiations or not self.analytics:
            return {}
        values = list(negotiations.values())
        payload = {
            "savings": self.analytics.generate_savings_report(values),
            "compliance": self.analytics.compliance_coverage_analysis(values),
            "performance_by_category": self.analytics.negotiation_performance_by_category(values),
        }
        return self._json_safe(payload)

    def _dispatch_integrations(
        self,
        request: Request,
        negotiations: Dict[str, NegotiationResult],
        contracts: Dict[str, bytes],
    ) -> Dict[str, object]:
        report: Dict[str, object] = {}
        if not negotiations:
            return report

        if self.slack_integration:
            events: List[Dict[str, object]] = []
            for result in negotiations.values():
                offer = result.offer
                if offer.accepted:
                    try:
                        self.slack_integration.notify_negotiation_complete(offer)
                        events.append({"vendor_id": offer.vendor_id, "status": "sent"})
                    except Exception as exc:  # pragma: no cover - network issues
                        events.append({"vendor_id": offer.vendor_id, "error": str(exc)})
            if events:
                report["slack"] = events

        if self.erp_integration:
            purchase_orders: List[Dict[str, object]] = []
            for result in negotiations.values():
                offer = result.offer
                if offer.accepted:
                    try:
                        po_id = self.erp_integration.create_purchase_order(offer)
                        purchase_orders.append({"vendor_id": offer.vendor_id, "po_id": po_id})
                    except Exception as exc:  # pragma: no cover - network issues
                        purchase_orders.append({"vendor_id": offer.vendor_id, "error": str(exc)})
            if purchase_orders:
                report["erp"] = purchase_orders

        if self.docusign_integration:
            envelopes: List[Dict[str, object]] = []
            signers = request.policy_context.approval_chain if request.policy_context else []
            for vendor_id, content in contracts.items():
                if not signers:
                    continue
                try:
                    envelope_id = self.docusign_integration.send_for_signature(content, signers)
                    envelopes.append({"vendor_id": vendor_id, "envelope_id": envelope_id})
                except Exception as exc:  # pragma: no cover - network issues
                    envelopes.append({"vendor_id": vendor_id, "error": str(exc)})
            if envelopes:
                report["docusign"] = envelopes

        return report

    def _resolve_category(self, request: Request) -> str:
        specs = request.specs or {}
        if "_category_override" in specs:
            return str(specs["_category_override"])
        if "category" in specs:
            return str(specs["category"])
        if "type" in specs:
            return str(specs["type"])
        if request.must_haves:
            return request.must_haves[0].lower()
        return "saas"

    def _profiles_to_seed_records(self, profiles: Iterable[VendorProfile]) -> List[SeedVendorRecord]:
        records: List[SeedVendorRecord] = []
        for profile in profiles:
            tiers = {str(key): float(value) for key, value in profile.price_tiers.items()}
            list_price = min(tiers.values()) if tiers else profile.guardrails.price_floor or 0.0
            if list_price <= 0:
                list_price = 100.0
            floor_price = profile.guardrails.price_floor or max(list_price * 0.7, 1.0)
            payment_terms = self._normalize_payment_terms(profile.guardrails.payment_terms_allowed)
            behavior = "balanced"
            if profile.reliability_stats:
                behavior = str(profile.reliability_stats.get("behavior_profile", "balanced"))
            record = SeedVendorRecord(
                seed_id=profile.vendor_id,
                name=profile.name,
                category=next(iter(profile.capability_tags), "saas"),
                list_price=float(list_price),
                floor_price=float(floor_price),
                payment_terms=payment_terms,
                compliance=[cert.lower() for cert in profile.certifications],
                features=[tag.lower() for tag in profile.capability_tags],
                regions=list(profile.regions),
                support=profile.reliability_stats or {"tier": "standard"},
                behavior_profile=behavior,
                price_tiers=tiers or {"100": float(list_price)},
                exchange_policy=ExchangePolicy(),
                billing_cadence=profile.billing_cadence or "per_seat_per_year",
                raw={"source": "scraped", "vendor_id": profile.vendor_id},
            )
            records.append(record)
        return records

    def _normalize_payment_terms(self, terms: Iterable[str]) -> List[PaymentTerms]:
        normalized: List[PaymentTerms] = []
        for value in terms:
            try:
                normalized.append(PaymentTerms(value))
            except ValueError:
                cleaned = value.replace(" ", "").replace("-", "").upper()
                for candidate in PaymentTerms:
                    if candidate.value.replace(" ", "").replace("-", "").upper() == cleaned:
                        normalized.append(candidate)
                        break
                else:
                    normalized.append(PaymentTerms.NET_30)
        if not normalized:
            normalized.append(PaymentTerms.NET_30)
        return normalized

    def _json_safe(self, payload):
        if isinstance(payload, dict):
            return {key: self._json_safe(value) for key, value in payload.items()}
        if isinstance(payload, list):
            return [self._json_safe(item) for item in payload]
        if isinstance(payload, datetime):
            return payload.isoformat()
        if isinstance(payload, Enum):
            return payload.value
        if isinstance(payload, bytes):
            return b64encode(payload).decode("utf-8")
        return payload


__all__ = ["SaaSProcurementPipeline", "BuyerIntakeOrchestrator", "VendorPicker", "NegotiationManager", "PresentationBuilder"]
