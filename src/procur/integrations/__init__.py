"""Integrations with third-party data sources and collaboration tools."""

from .base_scraper import BaseScraper, VendorData, ScrapingConfig
from .g2_scraper import G2Scraper
from .pricing_scraper import PricingScraper
from .compliance_scraper import ComplianceScraper
from .data_validator import VendorDataValidator, QualityReport
from .enrichment_pipeline import VendorEnrichmentPipeline, EnrichmentConfig
from .cache_manager import CacheManager

# Legacy imports (if vendor_scraper and tooling exist)
try:
    from .vendor_scraper import VendorDataScraper
except ImportError:
    VendorDataScraper = None

try:
    from .tooling import DocuSignIntegration, ERPIntegration, SlackIntegration
except ImportError:
    DocuSignIntegration = None
    ERPIntegration = None
    SlackIntegration = None

__all__ = [
    # Core scraping infrastructure
    "BaseScraper",
    "VendorData",
    "ScrapingConfig",

    # Specific scrapers
    "G2Scraper",
    "PricingScraper",
    "ComplianceScraper",

    # Data validation and quality
    "VendorDataValidator",
    "QualityReport",

    # Orchestration and pipeline
    "VendorEnrichmentPipeline",
    "EnrichmentConfig",

    # Caching and performance
    "CacheManager",
]

# Add legacy components if available
if VendorDataScraper is not None:
    __all__.append("VendorDataScraper")
if SlackIntegration is not None:
    __all__.extend(["SlackIntegration", "DocuSignIntegration", "ERPIntegration"])
