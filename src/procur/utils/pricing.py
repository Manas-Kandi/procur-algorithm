"""Helpers for normalizing price and budget cadence."""

from __future__ import annotations

from typing import Optional


CADENCE_FACTORS = {
    "per_seat_per_year": 1.0,
    "per_seat_per_month": 12.0,
    "per_unit_per_year": 1.0,
    "per_unit_per_month": 12.0,
}


def annualize_value(amount: Optional[float], cadence: Optional[str]) -> Optional[float]:
    """Convert a unit amount into an annual figure based on cadence."""
    if amount is None:
        return None
    if cadence is None:
        return amount
    factor = CADENCE_FACTORS.get(cadence.lower())
    if factor is None:
        return amount
    return amount * factor


def normalize_budget_total(budget_total: Optional[float], cadence: Optional[str]) -> Optional[float]:
    """Normalize an aggregate budget into an annual amount."""
    return annualize_value(budget_total, cadence)


def price_fit_ratio(budget_unit_annual: Optional[float], list_price_annual: Optional[float]) -> float:
    """Return a 0..1 ratio expressing how well a price fits the budget."""
    if not budget_unit_annual or not list_price_annual or list_price_annual <= 0:
        return 0.0
    ratio = budget_unit_annual / list_price_annual
    if ratio >= 1.0:
        return 1.0
    return max(0.0, ratio)


__all__ = [
    "annualize_value",
    "normalize_budget_total",
    "price_fit_ratio",
    "CADENCE_FACTORS",
]
