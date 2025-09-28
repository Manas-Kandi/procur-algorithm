"""Vendor matching utilities built on canonical feature/compliance scoring."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence

from ..models import Request
from ..data.seeds_loader import SeedVendorRecord
from .evaluation import (
    FeatureMatchResult,
    ComplianceScore,
    compute_feature_score,
    compute_compliance_score,
    compute_sla_score,
)


CATEGORY_ALIASES: Dict[str, Sequence[str]] = {
    "crm": ("saas/crm", "crm", "customer-relationship-management", "sales"),
    "hr": ("saas/hr", "hr", "human-resources", "payroll", "benefits"),
    "security": ("saas/security", "security", "cybersecurity", "infosec"),
    "analytics": ("saas/analytics", "analytics", "business-intelligence", "bi"),
    "erp": ("saas/erp", "erp", "enterprise-resource-planning", "finance"),
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
    if getattr(request, "category", None):
        return request.category  # type: ignore[return-value]
    features = {feature.lower() for feature in request.must_haves}
    if {"lead management", "crm"} & features:
        return "crm"
    if {"payroll", "benefits"} & features:
        return "hr"
    if {"siem", "security"} & features:
        return "security"
    return "saas"


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
