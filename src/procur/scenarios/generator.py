from __future__ import annotations

from typing import Iterable, List, Optional

from .schema import Scenario, ScenarioExchange, ScenarioEvaluationTargets, ScenarioRequest, ScenarioRisk, ScenarioSeller


def build_scenario(
    *,
    scenario_id: str,
    description: str,
    category: str,
    quantity: int,
    budget_total: float,
    must_haves: Optional[Iterable[str]] = None,
    compliance_requirements: Optional[Iterable[str]] = None,
    seller_name: str,
    list_price: float,
    price_floor: float,
    term_options: Iterable[int],
    payment_options: Iterable[str],
    behavior_profile: str,
    non_negotiables: Optional[Iterable[str]] = None,
    exchange: ScenarioExchange | None = None,
    risk: ScenarioRisk | None = None,
    eval_targets: ScenarioEvaluationTargets | None = None,
    tags: Optional[List[str]] = None,
) -> Scenario:
    return Scenario(
        scenario_id=scenario_id,
        description=description,
        request=ScenarioRequest(
            category=category,
            quantity=quantity,
            budget_total=budget_total,
            must_haves=list(must_haves or []),
            compliance_requirements=list(compliance_requirements or []),
        ),
        seller=ScenarioSeller(
            name=seller_name,
            list_price=list_price,
            price_floor=price_floor,
            term_options=list(term_options),
            payment_options=list(payment_options),
            non_negotiables=list(non_negotiables or []),
            behavior_profile=behavior_profile,
        ),
        exchange_table=exchange or ScenarioExchange(),
        risk=risk or ScenarioRisk(),
        eval_targets=eval_targets or ScenarioEvaluationTargets(),
        tags=tags or [],
    )


def scenario_from_ratio(
    base_id: str,
    description: str,
    *,
    category: str,
    quantity: int,
    list_price: float,
    floor_ratio: float,
    budget_ratio: float,
    term_options: Iterable[int] = (12, 24, 36),
    payment_options: Iterable[str] = ("NET30", "NET15", "NET45"),
    tags: Optional[List[str]] = None,
    compliance_requirements: Optional[Iterable[str]] = None,
) -> Scenario:
    price_floor = round(list_price * floor_ratio, 2)
    budget_total = round(list_price * budget_ratio * quantity, 2)
    return build_scenario(
        scenario_id=base_id,
        description=description,
        category=category,
        quantity=quantity,
        budget_total=budget_total,
        compliance_requirements=compliance_requirements,
        seller_name="Vendor",
        list_price=list_price,
        price_floor=price_floor,
        term_options=term_options,
        payment_options=payment_options,
        behavior_profile="auto_generated",
        tags=tags or [],
    )
