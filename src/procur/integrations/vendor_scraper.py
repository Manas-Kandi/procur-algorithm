from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

import httpx
from bs4 import BeautifulSoup

from ..models import VendorProfile, VendorGuardrails
from ..models.enums import RiskLevel

logger = logging.getLogger(__name__)


@dataclass
class ScrapedVendor:
    vendor_id: str
    name: str
    url: str
    pricing_hint: Optional[float]
    categories: List[str]
    regions: List[str]
    summary: str


class VendorDataScraper:
    """Fetch vendor intelligence from public SaaS directories."""

    USER_AGENT = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    )

    COMPLIANCE_KEYWORDS: Dict[str, List[str]] = {
        "SOC2": ["soc 2", "soc2", "service organization control"],
        "ISO27001": ["iso 27001", "iso/iec 27001"],
        "HIPAA": ["hipaa", "health insurance portability"],
        "GDPR": ["gdpr", "general data protection regulation"],
    }

    def __init__(self, *, timeout: float = 12.0) -> None:
        self._timeout = timeout
        self._client = httpx.Client(timeout=timeout, headers={"User-Agent": self.USER_AGENT})
        self._cache: Dict[str, VendorProfile] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def scrape_g2_data(self, category: str) -> List[VendorProfile]:
        """Scrape vendor listings from the public G2 category page."""
        url = f"https://www.g2.com/categories/{category.strip().lower()}"
        try:
            response = self._client.get(url)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Failed to fetch G2 data for category '%s': %s", category, exc)
            return []

        vendors = self._parse_g2_html(response.text)
        profiles: List[VendorProfile] = [self._to_profile(vendor) for vendor in vendors]
        for profile in profiles:
            self._cache[profile.vendor_id] = profile
        return profiles

    def update_pricing_from_websites(self, vendor_id: str) -> VendorProfile:
        """Fetch a vendor's pricing page and update cached pricing data."""
        base_profile = self._cache.get(vendor_id)
        if base_profile is None:
            raise KeyError(f"Vendor '{vendor_id}' must be scraped before pricing update")

        website = base_profile.contact_endpoints.get("website")
        if not website:
            raise ValueError(f"Vendor '{vendor_id}' does not expose a website endpoint")

        try:
            response = self._client.get(website if website.startswith("http") else f"https://{website}")
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Failed to fetch vendor site '%s': %s", website, exc)
            return base_profile

        prices = self._extract_prices(response.text)
        if not prices:
            return base_profile

        avg_price = sum(prices) / len(prices)
        updated_tiers = dict(base_profile.price_tiers)
        updated_tiers.setdefault("100", round(avg_price, 2))
        updated_guardrails = base_profile.guardrails.model_copy()
        if updated_guardrails.price_floor is None:
            updated_guardrails.price_floor = round(avg_price * 0.7, 2)

        updated = base_profile.model_copy(update={
            "price_tiers": updated_tiers,
            "guardrails": updated_guardrails,
        })
        self._cache[vendor_id] = updated
        return updated

    def enrich_with_compliance_data(self, vendor: VendorProfile) -> VendorProfile:
        """Augment vendor with compliance claims discovered on their site."""
        website = vendor.contact_endpoints.get("website")
        if not website:
            return vendor

        try:
            response = self._client.get(website if website.startswith("http") else f"https://{website}")
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.debug("Compliance enrichment skipped for '%s': %s", vendor.vendor_id, exc)
            return vendor

        text = response.text.lower()
        certifications = {cert.upper() for cert in vendor.certifications}
        for label, keywords in self.COMPLIANCE_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                certifications.add(label)
        return vendor.model_copy(update={"certifications": sorted(certifications)})

    # ------------------------------------------------------------------
    # Parsing helpers
    # ------------------------------------------------------------------
    def _parse_g2_html(self, html: str) -> List[ScrapedVendor]:
        soup = BeautifulSoup(html, "html.parser")
        vendors: List[ScrapedVendor] = []
        json_blobs = soup.find_all("script", attrs={"type": "application/ld+json"})
        for blob in json_blobs:
            try:
                data = json.loads(blob.string or "{}")
            except json.JSONDecodeError:  # pragma: no cover - defensive
                continue
            if isinstance(data, dict) and data.get("@type") == "ItemList":
                for item in data.get("itemListElement", []):
                    vendor = self._extract_vendor(item)
                    if vendor:
                        vendors.append(vendor)
        return vendors

    def _extract_vendor(self, item: Dict[str, object]) -> Optional[ScrapedVendor]:
        if not isinstance(item, dict):
            return None
        entry = item.get("item")
        if not isinstance(entry, dict):
            return None
        name = str(entry.get("name") or "").strip()
        if not name:
            return None
        url = str(entry.get("url") or "").strip()
        description = str(entry.get("description") or "")
        offers = entry.get("offers") or {}
        price = None
        if isinstance(offers, dict):
            price = offers.get("price") or offers.get("priceSpecification", {}).get("price")  # type: ignore[assignment]
        try:
            price_value = float(price) if price is not None else None
        except (TypeError, ValueError):  # pragma: no cover - defensive
            price_value = None
        categories = entry.get("category") or []
        if isinstance(categories, str):
            categories = [categories]
        regions = entry.get("areaServed") or []
        if isinstance(regions, str):
            regions = [regions]
        return ScrapedVendor(
            vendor_id=f"g2::{name.lower().replace(' ', '-')}",
            name=name,
            url=url or f"https://www.g2.com{entry.get('url')}",
            pricing_hint=price_value,
            categories=[str(cat).lower() for cat in categories],
            regions=[str(region).lower() for region in regions],
            summary=description,
        )

    def _to_profile(self, vendor: ScrapedVendor) -> VendorProfile:
        price_tiers = {"100": round(vendor.pricing_hint or 0, 2)} if vendor.pricing_hint else {}
        guardrails = VendorGuardrails(
            price_floor=round((vendor.pricing_hint or 100.0) * 0.7, 2) if vendor.pricing_hint else None
        )
        capability_tags = sorted({*vendor.categories, "saas"})
        contact_endpoints = {"website": vendor.url} if vendor.url else {}
        return VendorProfile(
            vendor_id=vendor.vendor_id,
            name=vendor.name,
            capability_tags=capability_tags,
            certifications=[],
            regions=vendor.regions or ["global"],
            lead_time_brackets={"default": (30, 45)},
            price_tiers=price_tiers,
            guardrails=guardrails,
            reliability_stats={"source": "g2"},
            risk_level=RiskLevel.MEDIUM,
            contact_endpoints=contact_endpoints,
            billing_cadence="per_seat_per_year",
        )

    def _extract_prices(self, html: str) -> List[float]:
        pattern = re.compile(r"\$\s*([0-9]{2,5}(?:,[0-9]{3})?(?:\.[0-9]{2})?)")
        prices: List[float] = []
        for match in pattern.findall(html):
            try:
                prices.append(float(match.replace(",", "")))
            except ValueError:  # pragma: no cover - defensive
                continue
        return prices


__all__ = ["VendorDataScraper"]
