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
