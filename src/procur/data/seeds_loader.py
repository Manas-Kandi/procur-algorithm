from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from ..models import PaymentTerms, VendorGuardrails, VendorProfile
from ..services.negotiation_engine import ExchangePolicy
from ..services.compliance_catalog import normalize_identifier
from ..utils.pricing import annualize_value


@dataclass
class SeedVendorRecord:
    """Canonical representation of a vendor seed entry."""

    seed_id: str
    name: str
    category: str
    list_price: float
    floor_price: float
    payment_terms: List[PaymentTerms]
    compliance: List[str]
    features: List[str]
    regions: List[str]
    support: Dict[str, object]
    behavior_profile: str
    price_tiers: Dict[str, float]
    exchange_policy: ExchangePolicy
    billing_cadence: str
    raw: Dict[str, object]

    def to_vendor_profile(self) -> VendorProfile:
        guardrails = VendorGuardrails(
            price_floor=self.floor_price,
            payment_terms_allowed=[term.value for term in self.payment_terms],
        )
        tiers = {str(key): float(value) for key, value in self.price_tiers.items()}
        if not tiers:
            tiers = {"100": self.list_price}
        capability_tags = {self.category}
        capability_tags.update(self.features)
        certifications = [cert.upper() for cert in self.compliance]
        reliability_stats = {
            "support_tier": self.support.get("tier"),
            "support_sla": self.support.get("sla"),
            "behavior_profile": self.behavior_profile,
        }
        profile = VendorProfile(
            vendor_id=f"seed-{self.seed_id}",
            name=self.name,
            capability_tags=sorted(capability_tags),
            certifications=certifications,
            regions=[region.lower() for region in self.regions],
            lead_time_brackets={"default": (30, 45)},
            price_tiers=tiers,
            guardrails=guardrails,
            reliability_stats=reliability_stats,
            contact_endpoints={"sales": "seed"},
            billing_cadence=self.billing_cadence,
        )
        setattr(profile, "_exchange_policy", self.exchange_policy)
        setattr(profile, "_seed_metadata", self.raw)
        return profile


def _parse_payment_terms(terms: Iterable[str]) -> List[PaymentTerms]:
    parsed: List[PaymentTerms] = []
    for value in terms:
        try:
            parsed.append(PaymentTerms(value))
        except ValueError:
            upper = value.replace("_", "").replace(" ", "").upper()
            for term in PaymentTerms:
                if term.value.replace(" ", "").upper() == upper:
                    parsed.append(term)
                    break
            else:
                raise ValueError(f"Unsupported payment term '{value}' in seed catalog")
    return parsed


def _parse_exchange_policy(exchange_blob: Optional[Dict[str, object]]) -> ExchangePolicy:
    if not exchange_blob:
        return ExchangePolicy()
    term_trade = {}
    for key, value in exchange_blob.get("term_trade", {}).items():
        term_trade[int(key)] = float(value)
    payment_trade = {}
    for key, value in exchange_blob.get("payment_trade", {}).items():
        try:
            payment_trade[PaymentTerms(key)] = float(value)
        except ValueError:
            normalized = key.replace("_", "").replace(" ", "").upper()
            for term in PaymentTerms:
                if term.value.replace(" ", "").upper() == normalized:
                    payment_trade[term] = float(value)
                    break
            else:
                raise ValueError(f"Unsupported payment term '{key}' in exchange configuration")
    value_add_offsets = {
        key: float(value) for key, value in exchange_blob.get("value_add_offsets", {}).items()
    }
    policy = ExchangePolicy()
    if term_trade:
        policy.term_trade = term_trade
    if payment_trade:
        policy.payment_trade = payment_trade
    if value_add_offsets:
        policy.value_add_offsets = value_add_offsets
    return policy


def _build_seed_record(raw: Dict[str, object]) -> SeedVendorRecord:
    seed_id = str(raw.get("id") or raw.get("name"))
    pricing = raw.get("pricing", {})
    list_price = float(pricing.get("list_price"))
    floor_price = float(pricing.get("floor"))
    tiers = {str(k): float(v) for k, v in pricing.get("tiers", {}).items()}
    billing_cadence = str(raw.get("billing_cadence", "per_seat_per_year"))

    list_price = annualize_value(list_price, billing_cadence) or list_price
    floor_price = annualize_value(floor_price, billing_cadence) or floor_price
    tiers = {key: annualize_value(value, billing_cadence) or float(value) for key, value in tiers.items()}

    payment_terms = _parse_payment_terms(raw.get("payment_terms", []))
    compliance = [normalize_identifier(item).upper() for item in raw.get("compliance", [])]
    features = [normalize_identifier(item) for item in raw.get("features", [])]
    regions = [normalize_identifier(item) for item in raw.get("regions", [])]
    support = raw.get("support", {})
    behavior_profile = str(raw.get("behavior_profile", "balanced"))
    exchange_policy = _parse_exchange_policy(raw.get("exchange"))

    return SeedVendorRecord(
        seed_id=seed_id,
        name=str(raw.get("name")),
        category=str(raw.get("category", "saas")),
        list_price=list_price,
        floor_price=floor_price,
        payment_terms=payment_terms,
        compliance=compliance,
        features=features,
        regions=regions,
        support=support,
        behavior_profile=behavior_profile,
        price_tiers=tiers,
        exchange_policy=exchange_policy,
        billing_cadence=billing_cadence,
        raw=raw,
    )


def load_seed_catalog(path: str | Path) -> List[SeedVendorRecord]:
    data_path = Path(path)
    with data_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return [_build_seed_record(entry) for entry in payload]


def build_vendor_profiles(records: Iterable[SeedVendorRecord]) -> List[VendorProfile]:
    return [record.to_vendor_profile() for record in records]


__all__ = ["SeedVendorRecord", "load_seed_catalog", "build_vendor_profiles"]
