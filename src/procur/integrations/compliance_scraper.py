"""Compliance certification database scraper for vendor compliance verification."""

from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, quote

from .base_scraper import BaseScraper, VendorData


class ComplianceData:
    """Compliance certification data for a vendor."""

    def __init__(self):
        self.soc2_type1: bool = False
        self.soc2_type2: bool = False
        self.iso27001: bool = False
        self.iso9001: bool = False
        self.pci_dss: bool = False
        self.hipaa_compliant: bool = False
        self.gdpr_compliant: bool = False
        self.fedramp_authorized: bool = False
        self.ccpa_compliant: bool = False

        # Certification details
        self.certifications: Dict[str, Dict] = {}
        self.last_updated: str = datetime.now().isoformat()
        self.confidence_score: float = 0.0


class ComplianceScraper(BaseScraper):
    """Scraper for compliance certification databases and vendor compliance pages."""

    # SOC2 directory sources
    SOC2_SOURCES = [
        "https://www.aicpa.org/",  # AICPA SOC reports
        "https://www.ssae-16.com/",  # SSAE 16 directory
    ]

    # ISO certification databases
    ISO_SOURCES = [
        "https://www.iso.org/",
        "https://www.isoregistry.com/",
    ]

    # Security compliance patterns
    COMPLIANCE_PATTERNS = {
        "soc2_type1": [
            r"soc\s*2\s*type\s*i+",
            r"soc\s*2\s*type\s*1",
            r"service organization control.*type.*1",
        ],
        "soc2_type2": [
            r"soc\s*2\s*type\s*ii+",
            r"soc\s*2\s*type\s*2",
            r"service organization control.*type.*2",
        ],
        "iso27001": [
            r"iso\s*27001",
            r"iso\s*\/\s*iec\s*27001",
            r"information security management",
        ],
        "iso9001": [
            r"iso\s*9001",
            r"quality management system",
        ],
        "pci_dss": [
            r"pci\s*dss",
            r"payment card industry",
            r"pci\s*compliance",
        ],
        "hipaa": [
            r"hipaa",
            r"health insurance portability",
            r"protected health information",
        ],
        "gdpr": [
            r"gdpr",
            r"general data protection regulation",
            r"data protection regulation",
        ],
        "fedramp": [
            r"fedramp",
            r"federal risk and authorization",
            r"fed\s*ramp",
        ],
        "ccpa": [
            r"ccpa",
            r"california consumer privacy act",
        ],
    }

    def scrape_vendor_compliance(self, vendor_data: VendorData) -> ComplianceData:
        """Scrape compliance information for a vendor."""

        compliance = ComplianceData()

        if not vendor_data.website:
            return compliance

        # First check vendor's own compliance pages
        vendor_compliance = self._scrape_vendor_compliance_pages(vendor_data.website)
        self._merge_compliance_data(compliance, vendor_compliance)

        # Check external certification databases
        external_compliance = self._check_certification_databases(vendor_data.name)
        self._merge_compliance_data(compliance, external_compliance)

        # Calculate confidence score
        compliance.confidence_score = self._calculate_compliance_confidence(compliance)

        return compliance

    def _scrape_vendor_compliance_pages(self, website: str) -> ComplianceData:
        """Scrape vendor's own compliance and security pages."""

        compliance = ComplianceData()

        # Common compliance page paths
        compliance_paths = [
            '/security',
            '/compliance',
            '/privacy',
            '/trust',
            '/certifications',
            '/legal/privacy',
            '/legal/security',
            '/about/security',
            '/enterprise/security',
            '/platform/security',
        ]

        # Try to find compliance pages
        compliance_urls = []
        for path in compliance_paths:
            url = urljoin(website, path)
            response = self._make_request(url)
            if response and response.status_code == 200:
                compliance_urls.append(url)

        # If no direct compliance pages, check main page for compliance links
        if not compliance_urls:
            compliance_urls = self._find_compliance_links(website)

        # Scrape compliance information from found pages
        for url in compliance_urls:
            page_compliance = self._extract_compliance_from_page(url)
            self._merge_compliance_data(compliance, page_compliance)

        return compliance

    def _find_compliance_links(self, website: str) -> List[str]:
        """Find compliance-related links on vendor website."""

        links = []
        response = self._make_request(website)
        if not response:
            return links

        soup = self._parse_html(response.text)

        # Look for compliance-related links
        compliance_keywords = [
            'security', 'compliance', 'privacy', 'trust',
            'certifications', 'soc', 'iso', 'gdpr', 'hipaa'
        ]

        # Check navigation links
        nav_selectors = [
            'nav a', '.navigation a', '.navbar a',
            '.menu a', '.header a', 'footer a'
        ]

        for selector in nav_selectors:
            elements = soup.select(selector)
            for element in elements:
                href = element.get('href', '')
                text = element.get_text(strip=True).lower()

                if any(keyword in text for keyword in compliance_keywords):
                    full_url = urljoin(website, href)
                    if full_url not in links:
                        links.append(full_url)

        return links

    def _extract_compliance_from_page(self, url: str) -> ComplianceData:
        """Extract compliance certifications from a single page."""

        compliance = ComplianceData()
        response = self._make_request(url)
        if not response:
            return compliance

        soup = self._parse_html(response.text)
        page_text = soup.get_text().lower()

        # Check for compliance patterns
        for cert_type, patterns in self.COMPLIANCE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, page_text, re.IGNORECASE):
                    setattr(compliance, cert_type, True)

                    # Try to extract certification details
                    details = self._extract_certification_details(soup, cert_type, pattern)
                    if details:
                        compliance.certifications[cert_type] = details

        # Look for certification badges/images
        self._extract_compliance_badges(soup, compliance)

        return compliance

    def _extract_certification_details(self, soup, cert_type: str, pattern: str) -> Optional[Dict]:
        """Extract detailed certification information."""

        details = {}

        # Look for certification dates, numbers, etc.
        text = soup.get_text()

        # Find text around the certification mention
        pattern_matches = list(re.finditer(pattern, text, re.IGNORECASE))
        for match in pattern_matches:
            start = max(0, match.start() - 200)
            end = min(len(text), match.end() + 200)
            context = text[start:end]

            # Extract certification number
            cert_number_match = re.search(r'(?:cert(?:ificate)?|report)?\s*#?\s*([A-Z0-9\-]{6,})', context, re.IGNORECASE)
            if cert_number_match:
                details['certificate_number'] = cert_number_match.group(1)

            # Extract validity dates
            date_patterns = [
                r'valid\s+(?:through|until|to)\s+(\d{1,2}\/\d{1,2}\/\d{4})',
                r'expires?\s+(\d{1,2}\/\d{1,2}\/\d{4})',
                r'issued\s+(\d{1,2}\/\d{1,2}\/\d{4})',
            ]

            for date_pattern in date_patterns:
                date_match = re.search(date_pattern, context, re.IGNORECASE)
                if date_match:
                    if 'valid' in date_pattern or 'expires' in date_pattern:
                        details['valid_until'] = date_match.group(1)
                    else:
                        details['issued_date'] = date_match.group(1)

        return details if details else None

    def _extract_compliance_badges(self, soup, compliance: ComplianceData):
        """Extract compliance information from certification badges/images."""

        # Look for compliance badge images
        badge_selectors = [
            'img[src*="soc"]', 'img[alt*="soc"]',
            'img[src*="iso"]', 'img[alt*="iso"]',
            'img[src*="pci"]', 'img[alt*="pci"]',
            'img[src*="hipaa"]', 'img[alt*="hipaa"]',
            'img[src*="gdpr"]', 'img[alt*="gdpr"]',
            'img[src*="fedramp"]', 'img[alt*="fedramp"]',
        ]

        for selector in badge_selectors:
            elements = soup.select(selector)
            for element in elements:
                src = element.get('src', '').lower()
                alt = element.get('alt', '').lower()
                title = element.get('title', '').lower()

                badge_text = f"{src} {alt} {title}"

                # Check badge text against compliance patterns
                for cert_type, patterns in self.COMPLIANCE_PATTERNS.items():
                    for pattern in patterns:
                        if re.search(pattern, badge_text, re.IGNORECASE):
                            setattr(compliance, cert_type, True)

    def _check_certification_databases(self, vendor_name: str) -> ComplianceData:
        """Check external certification databases for vendor."""

        compliance = ComplianceData()

        # For now, this would require API access to certification databases
        # In a real implementation, you'd integrate with:
        # - AICPA SOC report database
        # - ISO certificate registry
        # - PCI DSS compliant providers list
        # - FedRAMP marketplace

        # Placeholder for future database integration
        return compliance

    def _merge_compliance_data(self, target: ComplianceData, source: ComplianceData):
        """Merge compliance data from multiple sources."""

        # Merge boolean flags (OR operation - if any source says true, result is true)
        bool_fields = [
            'soc2_type1', 'soc2_type2', 'iso27001', 'iso9001',
            'pci_dss', 'hipaa_compliant', 'gdpr_compliant',
            'fedramp_authorized', 'ccpa_compliant'
        ]

        for field in bool_fields:
            if getattr(source, field):
                setattr(target, field, True)

        # Merge certification details
        target.certifications.update(source.certifications)

    def _calculate_compliance_confidence(self, compliance: ComplianceData) -> float:
        """Calculate confidence score for compliance data."""

        score = 0.0

        # Base score for each certification found
        certifications = [
            compliance.soc2_type1, compliance.soc2_type2,
            compliance.iso27001, compliance.iso9001,
            compliance.pci_dss, compliance.hipaa_compliant,
            compliance.gdpr_compliant, compliance.fedramp_authorized,
            compliance.ccpa_compliant
        ]

        cert_count = sum(certifications)
        score += min(cert_count * 0.1, 0.6)  # Max 0.6 for certifications

        # Bonus for certification details
        if compliance.certifications:
            score += min(len(compliance.certifications) * 0.05, 0.2)

        # Bonus for multiple verification sources
        score += 0.2  # Base confidence for vendor page verification

        return min(score, 1.0)

    def enrich_vendor_with_compliance(self, vendor_data: VendorData) -> VendorData:
        """Enrich vendor data with compliance information."""

        compliance = self.scrape_vendor_compliance(vendor_data)

        # Update vendor certifications
        new_certifications = []

        if compliance.soc2_type1:
            new_certifications.append("SOC2_TYPE1")
        if compliance.soc2_type2:
            new_certifications.append("SOC2_TYPE2")
        if compliance.iso27001:
            new_certifications.append("ISO27001")
        if compliance.iso9001:
            new_certifications.append("ISO9001")
        if compliance.pci_dss:
            new_certifications.append("PCI_DSS")
        if compliance.hipaa_compliant:
            new_certifications.append("HIPAA")
        if compliance.fedramp_authorized:
            new_certifications.append("FEDRAMP")

        # Update compliance frameworks
        new_frameworks = []

        if compliance.gdpr_compliant:
            new_frameworks.append("GDPR")
        if compliance.ccpa_compliant:
            new_frameworks.append("CCPA")

        # Merge with existing data
        vendor_data.certifications = list(set(vendor_data.certifications + new_certifications))
        vendor_data.compliance_frameworks = list(set(vendor_data.compliance_frameworks + new_frameworks))

        # Update confidence score
        vendor_data.confidence_score = min(
            vendor_data.confidence_score + (compliance.confidence_score * 0.3),
            1.0
        )

        return vendor_data

    def scrape_vendor_directory(self, category: str, limit: int = 50) -> List[VendorData]:
        """Not implemented for compliance scraper."""
        raise NotImplementedError("Use G2Scraper for vendor directory")

    def scrape_vendor_details(self, vendor_url: str) -> Optional[VendorData]:
        """Not implemented for compliance scraper."""
        raise NotImplementedError("Use G2Scraper for vendor details")


# Utility function for batch compliance enrichment
def enrich_vendors_with_compliance(
    vendors: List[VendorData],
    compliance_scraper: ComplianceScraper
) -> List[VendorData]:
    """Enrich multiple vendors with compliance data."""

    enriched_vendors = []

    for vendor in vendors:
        try:
            enriched_vendor = compliance_scraper.enrich_vendor_with_compliance(vendor)
            enriched_vendors.append(enriched_vendor)
        except Exception as e:
            print(f"Failed to enrich compliance for {vendor.name}: {e}")
            enriched_vendors.append(vendor)  # Keep original data

    return enriched_vendors


# Example usage
if __name__ == "__main__":
    from .g2_scraper import G2Scraper

    # Initialize scrapers
    g2_scraper = G2Scraper()
    compliance_scraper = ComplianceScraper()

    # Get some vendors
    vendors = g2_scraper.scrape_vendor_directory("security", limit=3)

    # Enrich with compliance data
    enriched_vendors = enrich_vendors_with_compliance(vendors, compliance_scraper)

    for vendor in enriched_vendors:
        print(f"\nVendor: {vendor.name}")
        print(f"Certifications: {vendor.certifications}")
        print(f"Compliance: {vendor.compliance_frameworks}")
        print(f"Confidence: {vendor.confidence_score:.2f}")