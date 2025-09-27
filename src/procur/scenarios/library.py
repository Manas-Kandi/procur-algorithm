from __future__ import annotations

from .generator import build_scenario
from .schema import Scenario, ScenarioExchange, ScenarioEvaluationTargets, ScenarioRisk


SCENARIO_LIBRARY: dict[str, Scenario] = {
    "S-12": build_scenario(
        scenario_id="S-12",
        description="Tight ZOPA with term-elastic seller",
        category="saas/crm",
        quantity=150,
        budget_total=150 * 1150.0,
        must_haves=["soc2"],
        seller_name="CRM Pro",
        list_price=1200.0,
        price_floor=1060.0,
        term_options=[12, 24, 36],
        payment_options=["NET30", "NET45", "NET15"],
        behavior_profile="price_sticky_term_elastic",
        exchange=ScenarioExchange(
            term_12m_to_price_drop=0.03,
            pay_NET15_to_price_drop=0.008,
            training_credit_value=1500.0,
        ),
        risk=ScenarioRisk(soc2=True, data_residency="US", exceptions_allowed=False),
        eval_targets=ScenarioEvaluationTargets(close_gap_abs=2500, max_rounds=6, target_savings_pct=7.5),
        tags=["crm", "tight_zopa", "term_trade"],
    ),
    "S-24": build_scenario(
        scenario_id="S-24",
        description="Payment-flexible seller with compliance exception",
        category="saas/security",
        quantity=80,
        budget_total=80 * 900.0,
        must_haves=["gdpr", "soc2"],
        seller_name="SecureSuite",
        list_price=950.0,
        price_floor=820.0,
        term_options=[12, 24],
        payment_options=["NET15", "NET30", "NET45"],
        behavior_profile="payment_flexible",
        exchange=ScenarioExchange(
            term_12m_to_price_drop=0.025,
            pay_NET15_to_price_drop=0.009,
            training_credit_value=1800.0,
        ),
        risk=ScenarioRisk(soc2=False, data_residency="EU", exceptions_allowed=True),
        eval_targets=ScenarioEvaluationTargets(close_gap_abs=3000, max_rounds=7, target_savings_pct=6.0),
        tags=["compliance_exception", "payment_trade"],
    ),
}


def get_scenario(scenario_id: str) -> Scenario:
    return SCENARIO_LIBRARY[scenario_id]


def list_scenarios() -> list[str]:
    return list(SCENARIO_LIBRARY.keys())
