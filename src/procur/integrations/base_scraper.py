"""Base scraping infrastructure for vendor data collection."""

from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse

import aiohttp
import requests
from bs4 import BeautifulSoup

from ..models import VendorProfile
from ..data.seeds_loader import SeedVendorRecord


@dataclass
class ScrapingConfig:
    """Configuration for web scraping operations."""

    # Rate limiting
    requests_per_second: float = 2.0
    concurrent_requests: int = 5

    # Retry settings
    max_retries: int = 3
    retry_delay: float = 1.0

    # Request settings
    timeout: int = 30
    user_agent: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    # Caching
    cache_duration_hours: int = 24
    respect_robots_txt: bool = True


@dataclass
class VendorData:
    """Raw vendor data collected from external sources."""

    name: str
    website: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None

    # Pricing information
    pricing_model: Optional[str] = None
    starting_price: Optional[float] = None
    price_tiers: Dict[str, float] = field(default_factory=dict)

    # Features and capabilities
    features: List[str] = field(default_factory=list)
    integrations: List[str] = field(default_factory=list)

    # Compliance and certifications
    certifications: List[str] = field(default_factory=list)
    compliance_frameworks: List[str] = field(default_factory=list)

    # Company information
    headquarters: Optional[str] = None
    founded_year: Optional[int] = None
    employee_count: Optional[str] = None

    # Ratings and reviews
    g2_rating: Optional[float] = None
    g2_reviews_count: Optional[int] = None
    capterra_rating: Optional[float] = None

    # Support information
    support_channels: List[str] = field(default_factory=list)
    sla_guarantee: Optional[float] = None

    # Source tracking
    source_url: Optional[str] = None
    scraped_at: Optional[str] = None
    confidence_score: float = 0.0


class BaseScraper(ABC):
    """Base class for vendor data scrapers."""

    def __init__(self, config: Optional[ScrapingConfig] = None):
        self.config = config or ScrapingConfig()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.config.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': 'https://www.g2.com/',
        })

        # Rate limiting
        self._last_request_time = 0.0
        self._request_count = 0

    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        min_interval = 1.0 / self.config.requests_per_second

        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)

        self._last_request_time = time.time()

    def _make_request(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Make a rate-limited HTTP request with retries."""
        self._rate_limit()

        for attempt in range(self.config.max_retries):
            try:
                response = self.session.get(
                    url,
                    timeout=self.config.timeout,
                    **kwargs
                )
                response.raise_for_status()
                return response

            except requests.RequestException as e:
                if attempt == self.config.max_retries - 1:
                    print(f"Failed to fetch {url} after {self.config.max_retries} attempts: {e}")
                    return None

                time.sleep(self.config.retry_delay * (2 ** attempt))

        return None

    def _parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content using BeautifulSoup."""
        return BeautifulSoup(html, 'html.parser')

    def _extract_text(self, element, selector: str, default: str = "") -> str:
        """Safely extract text from HTML element."""
        if element is None:
            return default

        found = element.select_one(selector)
        return found.get_text(strip=True) if found else default

    def _extract_price(self, text: str) -> Optional[float]:
        """Extract price from text using regex."""
        import re

        # Remove common currency symbols and spaces
        cleaned = re.sub(r'[,$\s]', '', text)

        # Look for price patterns
        price_patterns = [
            r'(\d+(?:\.\d{2})?)',  # Basic price
            r'(\d+)(?:/month|/mo|per month)',  # Monthly pricing
            r'(\d+)(?:/year|/yr|per year|annually)',  # Annual pricing
        ]

        for pattern in price_patterns:
            match = re.search(pattern, cleaned, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue

        return None

    @abstractmethod
    def scrape_vendor_directory(self, category: str, limit: int = 50) -> List[VendorData]:
        """Scrape vendor directory for a specific category."""
        pass

    @abstractmethod
    def scrape_vendor_details(self, vendor_url: str) -> Optional[VendorData]:
        """Scrape detailed information for a specific vendor."""
        pass

    def convert_to_seed_record(self, vendor_data: VendorData) -> SeedVendorRecord:
        """Convert scraped vendor data to seed record format."""

        # Generate seed ID from vendor name
        seed_id = vendor_data.name.lower().replace(' ', '-').replace('_', '-')
        seed_id = ''.join(c for c in seed_id if c.isalnum() or c == '-')

        # Map category
        category_mapping = {
            'crm': 'saas/crm',
            'customer relationship management': 'saas/crm',
            'sales': 'saas/crm',
            'hr': 'saas/hr',
            'human resources': 'saas/hr',
            'analytics': 'saas/analytics',
            'business intelligence': 'saas/analytics',
            'security': 'saas/security',
            'cybersecurity': 'saas/security',
        }

        mapped_category = category_mapping.get(
            vendor_data.category.lower() if vendor_data.category else 'unknown',
            'saas/other'
        )

        # Build pricing tiers
        price_tiers = {}
        if vendor_data.starting_price:
            price_tiers["1"] = vendor_data.starting_price
            price_tiers["10"] = vendor_data.starting_price * 0.95  # Volume discount
            price_tiers["50"] = vendor_data.starting_price * 0.90
            price_tiers["100"] = vendor_data.starting_price * 0.85

        # Add custom tiers if available
        price_tiers.update(vendor_data.price_tiers)

        # Map support tier
        support_tier = "business_hours"
        if any("24/7" in channel.lower() for channel in vendor_data.support_channels):
            support_tier = "24/7"
        elif any("premium" in channel.lower() for channel in vendor_data.support_channels):
            support_tier = "premium"

        # Create seed record
        raw_data = {
            "id": seed_id,
            "name": vendor_data.name,
            "category": mapped_category,
            "description": vendor_data.description or f"{vendor_data.name} software solution",
            "website": vendor_data.website,
            "list_price": vendor_data.starting_price or 100.0,
            "price_tiers": price_tiers,
            "currency": "USD",
            "billing_cadence": "per_seat_per_month",
            "features": vendor_data.features,
            "integrations": vendor_data.integrations,
            "compliance": vendor_data.certifications + vendor_data.compliance_frameworks,
            "guardrails": {
                "price_floor": (vendor_data.starting_price or 100.0) * 0.8,
                "payment_terms_allowed": ["Net30", "Net15", "Net45"],
            },
            "support": {
                "tier": support_tier,
                "sla": vendor_data.sla_guarantee or 99.0,
                "channels": vendor_data.support_channels or ["email", "phone"],
            },
            "lead_time_brackets": {
                "default": [7, 14],
                "enterprise": [14, 30],
            },
            "behavior_profile": {
                "negotiation_style": "moderate",
                "concession_willingness": 0.15,
                "volume_sensitivity": 0.1,
            },
            "exchange_policy": {
                "term_trade": {12: 0.03, 24: 0.05, 36: 0.07},
                "payment_trade": {
                    "Net15": 0.008,
                    "Net30": 0.0,
                    "Net45": -0.004,
                },
                "value_add_offsets": {"training_credits": 1500.0},
            },
            # Metadata
            "_scraped_from": vendor_data.source_url,
            "_scraped_at": vendor_data.scraped_at,
            "_confidence_score": vendor_data.confidence_score,
            "_g2_rating": vendor_data.g2_rating,
            "_review_count": vendor_data.g2_reviews_count,
        }

        return SeedVendorRecord.from_dict(raw_data)


class VendorDataValidator:
    """Validates and cleans scraped vendor data."""

    @staticmethod
    def validate_vendor_data(data: VendorData) -> bool:
        """Check if vendor data meets minimum quality requirements."""

        # Required fields
        if not data.name or len(data.name.strip()) < 2:
            return False

        # Must have some identifying information
        if not any([data.website, data.description, data.features]):
            return False

        # Pricing should be reasonable
        if data.starting_price and (data.starting_price < 1 or data.starting_price > 10000):
            return False

        return True

    @staticmethod
    def clean_vendor_data(data: VendorData) -> VendorData:
        """Clean and normalize vendor data."""

        # Clean name
        if data.name:
            data.name = data.name.strip().title()

        # Normalize website URL
        if data.website and not data.website.startswith(('http://', 'https://')):
            data.website = f"https://{data.website}"

        # Clean features (remove duplicates, normalize case)
        data.features = list(set(feature.lower().strip() for feature in data.features if feature.strip()))

        # Clean certifications
        data.certifications = list(set(cert.upper().strip() for cert in data.certifications if cert.strip()))

        # Normalize compliance frameworks
        compliance_mapping = {
            'soc 2': 'SOC2',
            'soc2': 'SOC2',
            'iso 27001': 'ISO27001',
            'iso27001': 'ISO27001',
            'gdpr': 'GDPR',
            'hipaa': 'HIPAA',
        }

        normalized_compliance = []
        for framework in data.compliance_frameworks:
            normalized = compliance_mapping.get(framework.lower().strip(), framework.upper())
            if normalized not in normalized_compliance:
                normalized_compliance.append(normalized)

        data.compliance_frameworks = normalized_compliance

        return data


async def scrape_multiple_sources(scrapers: List[BaseScraper], category: str, limit: int = 50) -> List[VendorData]:
    """Scrape vendor data from multiple sources concurrently."""

    async def scrape_source(scraper: BaseScraper) -> List[VendorData]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, scraper.scrape_vendor_directory, category, limit)

    # Run all scrapers concurrently
    tasks = [scrape_source(scraper) for scraper in scrapers]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Combine results
    all_vendors = []
    for result in results:
        if isinstance(result, list):
            all_vendors.extend(result)
        else:
            print(f"Scraper failed: {result}")

    # Remove duplicates based on vendor name
    seen_names = set()
    unique_vendors = []
    for vendor in all_vendors:
        if vendor.name.lower() not in seen_names:
            seen_names.add(vendor.name.lower())
            unique_vendors.append(vendor)

    return unique_vendors