"""Vendor matching utilities built on canonical feature/compliance scoring."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from ..models import Request
from ..data.seeds_loader import SeedVendorRecord
from .evaluation import (
    FeatureMatchResult,
    ComplianceScore,
    compute_feature_score,
    compute_compliance_score,
    compute_sla_score,
    normalize_feature_token,
)


CATEGORY_ALIASES: Dict[str, Sequence[str]] = {
    "crm": ("saas/crm", "crm", "customer-relationship-management", "sales"),
    "hr": ("saas/hr", "hr", "human-resources", "payroll", "benefits"),
    "security": ("saas/security", "security", "cybersecurity", "infosec"),
    "analytics": ("saas/analytics", "analytics", "business-intelligence", "bi"),
    "erp": ("saas/erp", "erp", "enterprise-resource-planning", "finance"),
}


CATEGORY_HINTS: Dict[str, Dict[str, Sequence[str]]] = {
    "crm": {
        "description": (
            "crm",
            "customer relationship",
            "sales pipeline",
            "deal desk",
            "account management",
        ),
        "features": (
            "lead management",
            "contact management",
            "pipeline tracking",
            "email integration",
            "deal tracking",
        ),
        "explicit": ("crm",),
    },
    "hr": {
        "description": ("hr", "human resources", "payroll", "benefits"),
        "features": ("payroll", "benefits", "onboarding"),
        "explicit": ("hr", "hcm"),
    },
    "security": {
        "description": ("security", "infosec", "soar", "siem", "threat"),
        "features": ("siem", "soar", "managed services"),
        "explicit": ("security", "infosec"),
    },
    "analytics": {
        "description": ("analytics", "bi", "business intelligence", "dashboards"),
        "features": ("dashboards", "ml", "data warehouse", "reporting"),
        "explicit": ("analytics", "bi"),
    },
    "erp": {
        "description": ("erp", "enterprise resource planning", "finance suite"),
        "features": ("modules-finance", "modules-hr", "workflow"),
        "explicit": ("erp",),
    },
}


def _normalise_category(value: str) -> str:
    return value.strip().lower().replace(" ", "-")


def _category_matches(request_category: str, vendor_category: str) -> bool:
    req = _normalise_category(request_category)
    vend = _normalise_category(vendor_category)
    if req == vend:
        return True
    for aliases in CATEGORY_ALIASES.values():
        norm_aliases = {_normalise_category(alias) for alias in aliases}
        if req in norm_aliases and vend in norm_aliases:
            return True
    return False


def _infer_category(request: Request) -> str:
    specs = getattr(request, "specs", {}) or {}
    override = specs.get("_category_override")
    if override:
        return override

    explicit = getattr(request, "category", None)
    if explicit:
        return explicit  # type: ignore[return-value]

    before_category = specs.get("category") or explicit or "unknown"

    description = (getattr(request, "description", "") or "").lower()
    raw_features = set()
    for feature in request.must_haves:
        raw_features.add(normalize_feature_token(feature))
    for feature in request.specs.get("features", []):
        raw_features.add(normalize_feature_token(feature))

    sanitized_inputs = specs.get("_sanitized_inputs", {})
    sanitized_must = sanitized_inputs.get("must_haves", {}).get("sanitized", [])
    for feature in sanitized_must:
        raw_features.add(normalize_feature_token(feature))

    scores: Dict[str, float] = {key: 0.0 for key in CATEGORY_ALIASES}
    signals: Dict[str, Dict[str, int]] = {
        key: {"description": 0, "features": 0, "explicit": 0}
        for key in CATEGORY_ALIASES
    }

    for category, hints in CATEGORY_HINTS.items():
        desc_hits = sum(1 for phrase in hints.get("description", []) if phrase in description)
        feature_hits = sum(1 for feat in hints.get("features", []) if normalize_feature_token(feat) in raw_features)
        explicit_hits = 0
        explicit_field = specs.get("category") or specs.get("type")
        if explicit_field and any(token in str(explicit_field).lower() for token in hints.get("explicit", [])):
            explicit_hits = 1

        if desc_hits:
            scores[category] += desc_hits * 1.5
        if feature_hits:
            scores[category] += feature_hits * 1.2
        if explicit_hits:
            scores[category] += 2.0

        signals.setdefault(category, {})
        signals[category]["description"] = desc_hits
        signals[category]["features"] = feature_hits
        signals[category]["explicit"] = explicit_hits

    best_category, best_score = _select_best_category(scores)
    final_category = best_category if best_score > 0 else "saas"

    if final_category == "saas" and scores.get("crm", 0.0) > 0:
        final_category = "crm"

    inference_payload = {
        "before": before_category,
        "final": final_category,
        "scores": scores,
        "signals": signals,
        "features_considered": sorted(raw_features),
    }
    specs["_category_inference"] = inference_payload
    return final_category


def _select_best_category(scores: Dict[str, float]) -> Tuple[str, float]:
    sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    if not sorted_scores:
        return "saas", 0.0
    best_category, best_score = sorted_scores[0]
    if len(sorted_scores) > 1 and sorted_scores[1][1] == best_score:
        # Prefer non-generic categories on tie
        if best_category == "saas":
            for category, score in sorted_scores:
                if category != "saas" and score == best_score:
                    return category, score
    return best_category, best_score


@dataclass
class VendorMatchSummary:
    feature: FeatureMatchResult
    compliance: ComplianceScore
    sla_score: float
    category_match: bool
    price_fit: float
    budget_per_unit: Optional[float] = None
    request_category: Optional[str] = None

    def matched_features(self) -> List[str]:
        return self.feature.matched

    def missing_features(self) -> List[str]:
        return self.feature.missing

    def composite_score(self, weights: Optional[Dict[str, float]] = None) -> float:
        weights = weights or {"features": 0.45, "compliance": 0.3, "price": 0.15, "sla": 0.10}
        if not self.category_match or self.compliance.blocking or self.feature.score == 0.0:
            return 0.0
        return (
            weights["features"] * self.feature.score
            + weights["compliance"] * self.compliance.score
            + weights["price"] * self.price_fit
            + weights.get("sla", 0.0) * self.sla_score
        )


def compute_price_fit(budget_per_unit: Optional[float], list_price: float) -> float:
    if not budget_per_unit or budget_per_unit <= 0:
        return 0.0
    ratio = budget_per_unit / list_price
    return max(0.0, min(ratio, 1.2))


def evaluate_vendor_against_request(
    request: Request,
    record: SeedVendorRecord,
    *,
    budget_per_unit: Optional[float] = None,
    optional_features: Optional[Dict[str, float]] = None,
) -> VendorMatchSummary:
    """
    Single authoritative path for vendor evaluation.

    This function unifies category/feature/compliance scoring and should be the
    only method used for vendor matching to ensure consistency.
    """
    category = _infer_category(request)
    category_match = _category_matches(category, record.category)

    feature_result = compute_feature_score(
        must_haves=request.must_haves,
        vendor_features=record.features,
        optional_features=optional_features,
    )

    vendor_evidence = {cert.lower(): "certified" for cert in record.compliance}
    compliance_result = compute_compliance_score(request.compliance_requirements, vendor_evidence)

    sla_percentage = float(record.support.get("sla", 99.0) or 99.0)
    support_tier = str(record.support.get("tier", ""))
    sla_score = compute_sla_score(sla_percentage, support_tier)

    price_fit = compute_price_fit(budget_per_unit, record.list_price)

    return VendorMatchSummary(
        feature=feature_result,
        compliance=compliance_result,
        sla_score=sla_score,
        category_match=category_match,
        price_fit=float(min(price_fit, 1.0)),
        budget_per_unit=budget_per_unit,
        request_category=category,
    )
