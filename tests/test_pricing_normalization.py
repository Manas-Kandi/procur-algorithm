from __future__ import annotations

from pathlib import Path

import pytest

from procur.models import Request, RequestType
from procur.orchestration.pipeline import BuyerIntakeOrchestrator
from procur.utils.pricing import annualize_value, normalize_budget_total
from procur.data import load_seed_catalog


def test_annualize_value_monthly_to_annual():
    assert annualize_value(195.0, "per_seat_per_month") == pytest.approx(2340.0)


def test_normalize_budget_total_monthly():
    assert normalize_budget_total(39000.0, "per_seat_per_month") == pytest.approx(468000.0)


def test_seed_loader_normalizes_monthly_prices():
    records = load_seed_catalog(Path("assets/seeds.json"))
    zen = next(record for record in records if record.seed_id == "zen-payroll")
    assert zen.list_price == pytest.approx(300.0)
    assert zen.floor_price == pytest.approx(216.0)


def test_request_budget_normalization_idempotent():
    request = Request(
        request_id="req",
        requester_id="user",
        type=RequestType.SAAS,
        description="Test",
        specs={"billing_cadence": "per_seat_per_month"},
        quantity=200,
        budget_max=39000.0,
        billing_cadence="per_seat_per_month",
    )

    orchestrator = BuyerIntakeOrchestrator(buyer_agent=None)  # type: ignore[arg-type]
    normalized = orchestrator.normalize_budget(request)
    assert normalized.budget_max == pytest.approx(468000.0)
    assert normalized.specs.get("_raw_budget_max") == pytest.approx(39000.0)

    normalized_again = orchestrator.normalize_budget(normalized)
    assert normalized_again.budget_max == pytest.approx(468000.0)


def test_parse_budget_answer_per_seat_monthly():
    orchestrator = BuyerIntakeOrchestrator(buyer_agent=None)  # type: ignore[arg-type]
    total, per_unit, cadence = orchestrator._parse_budget_answer(
        "$195 per seat per month", 200
    )
    assert per_unit == pytest.approx(195.0)
    assert total == pytest.approx(39000.0)
    assert cadence == "per_seat_per_month"


def test_parse_budget_answer_total_with_k():
    orchestrator = BuyerIntakeOrchestrator(buyer_agent=None)  # type: ignore[arg-type]
    total, per_unit, cadence = orchestrator._parse_budget_answer("Budget about 39k total", 200)
    assert total == pytest.approx(39000.0)
    assert per_unit == pytest.approx(195.0)
    assert cadence is None
