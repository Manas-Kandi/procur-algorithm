"""Integrations with third-party tools.

This module keeps imports lightweight so optional dependencies like ``aiohttp``
or ``slack_sdk`` are only required when the corresponding integrations are used.
"""

__all__: list[str] = []

# Optional data scraper (depends on ``httpx`` & ``beautifulsoup4``)
try:  # pragma: no cover - optional dependency
    from .vendor_scraper import VendorDataScraper

    __all__.append("VendorDataScraper")
except ImportError:  # pragma: no cover - optional dependency
    VendorDataScraper = None  # type: ignore

# Optional collaboration integrations (depend on ``httpx``)
try:  # pragma: no cover - optional dependency
    from .tooling import DocuSignIntegration, ERPIntegration, SlackIntegration

    __all__.extend(["SlackIntegration", "DocuSignIntegration", "ERPIntegration"])
except ImportError:  # pragma: no cover - optional dependency
    SlackIntegration = DocuSignIntegration = ERPIntegration = None  # type: ignore

# New Real Vendor Data Integration System (depends on ``requests`` & ``beautifulsoup4``)
try:  # pragma: no cover - optional dependency
    from .g2_scraper import G2Scraper
    from .pricing_scraper import PricingScraper
    from .compliance_scraper import ComplianceScraper
    from .data_validator import VendorDataValidator
    from .enrichment_pipeline import VendorEnrichmentPipeline, EnrichmentConfig
    from .cache_manager import CacheManager

    __all__.extend([
        "G2Scraper",
        "PricingScraper",
        "ComplianceScraper",
        "VendorDataValidator",
        "VendorEnrichmentPipeline",
        "EnrichmentConfig",
        "CacheManager"
    ])
except ImportError:  # pragma: no cover - optional dependency
    G2Scraper = PricingScraper = ComplianceScraper = None  # type: ignore
    VendorDataValidator = VendorEnrichmentPipeline = None  # type: ignore
    EnrichmentConfig = CacheManager = None  # type: ignore
