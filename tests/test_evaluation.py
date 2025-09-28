from __future__ import annotations

from decimal import Decimal

import pytest

from procur.services.evaluation import (
    TCOInputs,
    compute_tco,
    compute_buyer_utility,
    compute_seller_utility,
    compute_feature_score,
    compute_compliance_score,
    detect_zopa,
)


def test_tco_case_a_exact():
    breakdown = compute_tco(
        TCOInputs(
            unit_price=Decimal("180"),
            seats=200,
            term_months=12,
        )
    )
    assert breakdown.total == Decimal("36000.00")
    assert breakdown.as_dict()["total"] == pytest.approx(36000.0)


def test_tco_case_b_prepay_discount():
    breakdown = compute_tco(
        TCOInputs(
            unit_price=Decimal("300"),
            seats=10,
            term_months=12,
            payment_prepaid=True,
            prepay_discount_rate=Decimal("0.05"),
        )
    )
    assert breakdown.base == Decimal("3000.00")
    assert breakdown.prepay_adj == Decimal("-150.00")
    assert breakdown.total == Decimal("2850.00")


def test_buyer_utility_increases_when_price_drops():
    util_high = compute_buyer_utility(
        unit_price=1200.0,
        budget_per_unit=900.0,
        feature_score=1.0,
        compliance_score=1.0,
        sla_score=1.0,
    )
    util_low = compute_buyer_utility(
        unit_price=180.0,
        budget_per_unit=900.0,
        feature_score=1.0,
        compliance_score=1.0,
        sla_score=1.0,
    )
    assert util_low.buyer_utility > util_high.buyer_utility


def test_feature_score_requires_all_must_haves():
    result = compute_feature_score(
        must_haves=["email integration", "pipeline tracking"],
        vendor_features=["crm", "lead management"],
    )
    assert result.score == 0.0
    assert sorted(result.missing) == ["email integration", "pipeline tracking"]


def test_feature_score_partial_credit_when_some_match():
    result = compute_feature_score(
        must_haves=["email integration", "pipeline tracking"],
        vendor_features=["crm", "email"],
    )
    assert pytest.approx(result.score, rel=1e-3) == 0.5
    assert result.matched == ["email integration"]
    assert result.missing == ["pipeline tracking"]


def test_compliance_blocking_when_missing():
    score = compute_compliance_score(["SOC2"], {"soc2": "none"})
    assert score.blocking is True
    assert score.score == 0.0


def test_zopa_detection_with_concessions():
    assert not detect_zopa(buyer_budget_per_unit=900.0, seller_floor=1000.0)
    assert detect_zopa(buyer_budget_per_unit=900.0, seller_floor=1000.0, concessions_min_price=880.0)


def test_seller_utility_margin():
    seller = compute_seller_utility(
        proposed_price=900.0,
        list_price=1200.0,
        floor_price=800.0,
    )
    assert 0.0 <= seller.seller_utility <= 1.0
