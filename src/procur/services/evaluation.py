"""Canonical evaluation utilities: TCO, feature/compliance/SLA scoring, utilities."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, getcontext
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


getcontext().prec = 28


def _d(value: float | int | str | Decimal) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _round_money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class TCOInputs:
    unit_price: Decimal
    seats: int
    term_months: int
    one_time_fees: Decimal = Decimal("0")
    credits: Decimal = Decimal("0")
    payment_prepaid: bool = False
    prepay_discount_rate: Decimal = Decimal("0")


@dataclass(frozen=True)
class TCOBreakdown:
    base: Decimal
    one_time_fees: Decimal
    credits: Decimal
    prepay_adj: Decimal
    total: Decimal

    def as_dict(self) -> Dict[str, float]:
        return {
            "base": float(self.base),
            "one_time_fees": float(self.one_time_fees),
            "credits": float(self.credits),
            "prepay_adj": float(self.prepay_adj),
            "total": float(self.total),
        }


def compute_tco(inputs: TCOInputs) -> TCOBreakdown:
    base = _round_money(inputs.unit_price * _d(inputs.seats) * _d(inputs.term_months) / Decimal("12"))
    one_time = _round_money(inputs.one_time_fees)
    credits = _round_money(inputs.credits)
    prepay_adj = Decimal("0")
    if inputs.payment_prepaid and inputs.prepay_discount_rate:
        prepay_adj = _round_money(-(base * inputs.prepay_discount_rate))
    total = _round_money(base + one_time - credits + prepay_adj)

    if abs((base + one_time - credits + prepay_adj) - total) > Decimal("0.01"):
        raise ValueError("TCO invariant violated: rounding drift exceeds tolerance")

    return TCOBreakdown(base=base, one_time_fees=one_time, credits=credits, prepay_adj=prepay_adj, total=total)


FEATURE_SYNONYMS: Mapping[str, Sequence[str]] = {
    "automation": ("automation", "workflow", "workflows", "rules", "sequences"),
    "lead management": ("lead management", "leads", "lead_routing"),
    "contact management": ("contact management", "contacts", "crm"),
    "pipeline tracking": ("pipeline tracking", "pipeline", "deal tracking"),
    "email integration": ("email integration", "email", "gmail", "outlook"),
}


def _normalise_feature(token: str) -> str:
    lowered = token.lower().strip()
    for canonical, variants in FEATURE_SYNONYMS.items():
        if lowered in variants:
            return canonical
    return lowered


@dataclass(frozen=True)
class FeatureMatchResult:
    score: float
    matched: List[str]
    missing: List[str]


def compute_feature_score(
    must_haves: Sequence[str],
    vendor_features: Iterable[str],
    optional_features: Optional[Mapping[str, float]] = None,
) -> FeatureMatchResult:
    vendor_norm = {_normalise_feature(feat) for feat in vendor_features}
    required_norm = [_normalise_feature(feat) for feat in must_haves]

    matched: List[str] = []
    missing: List[str] = []

    for feature in required_norm:
        if feature in vendor_norm:
            matched.append(feature)
        else:
            missing.append(feature)

    total_required = len(required_norm)
    if total_required == 0:
        base_score = 1.0
    else:
        base_score = len(matched) / total_required

    optional_score = 1.0
    if optional_features:
        total_weight = sum(optional_features.values())
        if total_weight > 0:
            achieved = sum(
                optional_features[key]
                for key in optional_features
                if _normalise_feature(key) in vendor_norm
            )
            optional_score = achieved / total_weight
        else:
            optional_score = 0.0

    if total_required > 0 and optional_features:
        # Weight must-have coverage higher than optional capabilities.
        score = 0.7 * base_score + 0.3 * optional_score
    elif total_required > 0:
        score = base_score
    else:
        score = optional_score

    score = float(max(0.0, min(score, 1.0)))
    return FeatureMatchResult(score=score, matched=matched, missing=missing)


ComplianceEvidence = Mapping[str, str]

COMPLIANCE_WEIGHTS: Dict[str, float] = {
    "certified": 1.0,
    "attested_with_report": 0.85,
    "in_progress": 0.4,
    "roadmap": 0.4,
    "none": 0.0,
}


@dataclass(frozen=True)
class ComplianceFrameworkStatus:
    framework: str
    evidence: str
    score: float
    verified: bool


@dataclass(frozen=True)
class ComplianceScore:
    score: float
    frameworks: List[ComplianceFrameworkStatus]
    blocking: bool


def compute_compliance_score(
    required: Sequence[str],
    vendor_evidence: ComplianceEvidence,
    mandatory_threshold: float = 0.8,
) -> ComplianceScore:
    frameworks: List[ComplianceFrameworkStatus] = []
    scores: List[float] = []
    blocking = False
    for framework in required:
        key = framework.lower()
        evidence = vendor_evidence.get(key, "none")
        score = COMPLIANCE_WEIGHTS.get(evidence, 0.0)
        frameworks.append(
            ComplianceFrameworkStatus(
                framework=framework,
                evidence=evidence,
                score=score,
                verified=evidence in {"certified", "attested_with_report"},
            )
        )
        scores.append(score)
        if score < mandatory_threshold:
            blocking = True

    overall = sum(scores) / len(scores) if scores else 1.0
    return ComplianceScore(score=overall, frameworks=frameworks, blocking=blocking)


SUPPORT_TIER_SCORES = {
    "extended": 1.0,
    "24/7": 1.0,
    "premium": 0.9,
    "business_hours": 0.7,
    "email_only": 0.4,
}


def compute_sla_score(sla_percentage: float, support_tier: Optional[str]) -> float:
    sla_score = min(1.0, max(0.0, sla_percentage / 100.0))
    tier_score = SUPPORT_TIER_SCORES.get((support_tier or "").lower(), 0.5)
    combined = 0.7 * sla_score + 0.3 * tier_score
    return float(max(0.0, min(combined, 1.0)))


@dataclass(frozen=True)
class UtilityBreakdown:
    cost_fit: float
    feature_score: float
    compliance_score: float
    sla_score: float
    buyer_utility: float

    def as_dict(self) -> Dict[str, float]:
        return {
            "cost_fit": self.cost_fit,
            "feature_score": self.feature_score,
            "compliance_score": self.compliance_score,
            "sla_score": self.sla_score,
            "buyer_utility": self.buyer_utility,
        }


def compute_buyer_utility(
    *,
    unit_price: float,
    budget_per_unit: float,
    feature_score: float,
    compliance_score: float,
    sla_score: float,
    weights: Optional[Dict[str, float]] = None,
) -> UtilityBreakdown:
    weights = weights or {"cost": 0.40, "features": 0.35, "compliance": 0.15, "sla": 0.10}
    budget = max(budget_per_unit, 0.0)
    price = max(unit_price, 0.0)
    if budget <= 0:
        cost_fit = 0.0
    elif price <= budget:
        cost_fit = 1.0
    else:
        cost_fit = max(0.0, 1.0 - (price - budget) / (3 * budget))

    buyer_utility = (
        weights["cost"] * cost_fit
        + weights["features"] * feature_score
        + weights["compliance"] * compliance_score
        + weights["sla"] * sla_score
    )
    buyer_utility = float(max(0.0, min(buyer_utility, 1.0)))

    return UtilityBreakdown(
        cost_fit=float(cost_fit),
        feature_score=float(feature_score),
        compliance_score=float(compliance_score),
        sla_score=float(sla_score),
        buyer_utility=buyer_utility,
    )


@dataclass(frozen=True)
class SellerUtility:
    seller_margin: float
    seller_utility: float


def compute_seller_utility(
    *,
    proposed_price: float,
    list_price: float,
    floor_price: float,
    min_accept_threshold: float = 0.2,
    margin_weight: float = 0.9,
) -> SellerUtility:
    price_span = max(list_price - floor_price, 0.01)
    margin = max(0.0, min((proposed_price - floor_price) / price_span, 1.0))
    seller_utility = max(0.0, min(margin_weight * margin + (1 - margin_weight) * 0.5, 1.0))
    if seller_utility < min_accept_threshold:
        seller_utility = max(0.0, min(margin, 1.0))
    return SellerUtility(seller_margin=float(margin), seller_utility=float(seller_utility))


def detect_zopa(
    *,
    buyer_budget_per_unit: float,
    seller_floor: float,
    concessions_min_price: Optional[float] = None,
) -> bool:
    effective_floor = seller_floor
    if concessions_min_price is not None:
        effective_floor = min(effective_floor, concessions_min_price)
    return buyer_budget_per_unit >= effective_floor
