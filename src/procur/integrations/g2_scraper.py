"""G2.com directory scraper for vendor discovery and data collection."""

from __future__ import annotations

import json
import re
from datetime import datetime
from typing import List, Optional
from urllib.parse import urljoin, quote

from .base_scraper import BaseScraper, VendorData, VendorDataValidator


class G2Scraper(BaseScraper):
    """Scraper for G2.com vendor directory."""

    BASE_URL = "https://www.g2.com"

    # Category mappings from search terms to G2 URLs
    CATEGORY_URLS = {
        "crm": "/categories/crm",
        "customer-relationship-management": "/categories/crm",
        "sales": "/categories/sales-force-automation",
        "hr": "/categories/hr",
        "human-resources": "/categories/human-capital-management",
        "payroll": "/categories/payroll",
        "analytics": "/categories/business-intelligence",
        "business-intelligence": "/categories/business-intelligence",
        "bi": "/categories/business-intelligence",
        "security": "/categories/network-security",
        "cybersecurity": "/categories/endpoint-protection",
        "marketing": "/categories/marketing-automation",
        "project-management": "/categories/project-management",
        "collaboration": "/categories/collaboration",
        "accounting": "/categories/accounting",
        "erp": "/categories/erp",
    }

    def scrape_vendor_directory(self, category: str, limit: int = 50) -> List[VendorData]:
        """Scrape G2 vendor directory for a specific category."""

        category_url = self.CATEGORY_URLS.get(category.lower())
        if not category_url:
            print(f"Unknown category: {category}")
            return []

        url = urljoin(self.BASE_URL, category_url)
        response = self._make_request(url)

        if not response:
            return []

        soup = self._parse_html(response.text)
        vendor_links = self._extract_vendor_links(soup, limit)

        vendors = []
        for vendor_url in vendor_links:
            vendor_data = self.scrape_vendor_details(vendor_url)
            if vendor_data and VendorDataValidator.validate_vendor_data(vendor_data):
                vendor_data = VendorDataValidator.clean_vendor_data(vendor_data)
                vendors.append(vendor_data)

        return vendors

    def _extract_vendor_links(self, soup, limit: int) -> List[str]:
        """Extract vendor profile URLs from category page."""

        vendor_links = []

        # Look for vendor cards/tiles
        vendor_selectors = [
            'a[href*="/products/"]',  # Product page links
            '.product-listing a',      # Product listing links
            '.c-midnight-100 a[href*="/products/"]',  # Specific G2 structure
        ]

        for selector in vendor_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href', '')
                if '/products/' in href and href not in vendor_links:
                    full_url = urljoin(self.BASE_URL, href)
                    vendor_links.append(full_url)

                if len(vendor_links) >= limit:
                    break

            if len(vendor_links) >= limit:
                break

        return vendor_links[:limit]

    def scrape_vendor_details(self, vendor_url: str) -> Optional[VendorData]:
        """Scrape detailed information for a specific vendor."""

        response = self._make_request(vendor_url)
        if not response:
            return None

        soup = self._parse_html(response.text)

        # Extract basic vendor information
        name = self._extract_vendor_name(soup)
        if not name:
            return None

        description = self._extract_description(soup)
        website = self._extract_website(soup)
        category = self._extract_category(soup)

        # Extract pricing information
        pricing_data = self._extract_pricing(soup)

        # Extract features and capabilities
        features = self._extract_features(soup)

        # Extract ratings and reviews
        rating_data = self._extract_ratings(soup)

        # Extract company information
        company_info = self._extract_company_info(soup)

        # Extract compliance and certifications
        compliance_data = self._extract_compliance(soup)

        vendor_data = VendorData(
            name=name,
            website=website,
            category=category,
            description=description,
            pricing_model=pricing_data.get("model"),
            starting_price=pricing_data.get("starting_price"),
            price_tiers=pricing_data.get("tiers", {}),
            features=features,
            certifications=compliance_data.get("certifications", []),
            compliance_frameworks=compliance_data.get("frameworks", []),
            headquarters=company_info.get("headquarters"),
            founded_year=company_info.get("founded"),
            employee_count=company_info.get("employees"),
            g2_rating=rating_data.get("rating"),
            g2_reviews_count=rating_data.get("reviews_count"),
            support_channels=self._extract_support_channels(soup),
            source_url=vendor_url,
            scraped_at=datetime.now().isoformat(),
            confidence_score=self._calculate_confidence_score(soup),
        )

        return vendor_data

    def _extract_vendor_name(self, soup) -> Optional[str]:
        """Extract vendor name from product page."""

        selectors = [
            'h1[data-testid="product-name"]',
            'h1.product-head__title',
            '.product-head h1',
            'h1',
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                name = element.get_text(strip=True)
                # Clean up common suffixes
                name = re.sub(r'\s*(Reviews?|Pricing|Features).*$', '', name, flags=re.IGNORECASE)
                if name and len(name) > 1:
                    return name

        return None

    def _extract_description(self, soup) -> Optional[str]:
        """Extract product description."""

        selectors = [
            '[data-testid="product-description"]',
            '.product-head__desc',
            '.product-overview p',
            'meta[name="description"]',
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if selector.startswith('meta'):
                    return element.get('content', '').strip()
                else:
                    text = element.get_text(strip=True)
                    if text and len(text) > 20:
                        return text

        return None

    def _extract_website(self, soup) -> Optional[str]:
        """Extract vendor website URL."""

        selectors = [
            'a[data-testid="visit-website"]',
            'a[href*="website"]',
            '.product-head a[href^="http"]',
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                href = element.get('href', '')
                if href.startswith('http') and 'g2.com' not in href:
                    return href

        return None

    def _extract_category(self, soup) -> Optional[str]:
        """Extract product category."""

        # Look for breadcrumbs or category indicators
        selectors = [
            '.breadcrumbs a',
            '[data-testid="breadcrumb"] a',
            '.category-link',
        ]

        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True).lower()
                if any(cat in text for cat in self.CATEGORY_URLS.keys()):
                    return text

        return None

    def _extract_pricing(self, soup) -> dict:
        """Extract pricing information."""

        pricing_data = {
            "model": None,
            "starting_price": None,
            "tiers": {}
        }

        # Look for pricing section
        pricing_selectors = [
            '[data-testid="pricing-section"]',
            '.pricing-section',
            '.price-point',
            '.pricing-info',
        ]

        for selector in pricing_selectors:
            section = soup.select_one(selector)
            if section:
                # Extract pricing model
                pricing_text = section.get_text().lower()
                if 'subscription' in pricing_text or 'monthly' in pricing_text:
                    pricing_data["model"] = "subscription"
                elif 'one-time' in pricing_text or 'perpetual' in pricing_text:
                    pricing_data["model"] = "one-time"

                # Look for price amounts
                price_elements = section.select('.price, .amount, [class*="price"]')
                for price_elem in price_elements:
                    price_text = price_elem.get_text(strip=True)
                    price = self._extract_price(price_text)
                    if price and not pricing_data["starting_price"]:
                        pricing_data["starting_price"] = price

        # Look for starting price in page text
        if not pricing_data["starting_price"]:
            page_text = soup.get_text()
            price_patterns = [
                r'starting at \$(\d+(?:\.\d{2})?)',
                r'from \$(\d+(?:\.\d{2})?)',
                r'\$(\d+(?:\.\d{2})?)/month',
                r'\$(\d+(?:\.\d{2})?)/user',
            ]

            for pattern in price_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    try:
                        pricing_data["starting_price"] = float(match.group(1))
                        break
                    except ValueError:
                        continue

        return pricing_data

    def _extract_features(self, soup) -> List[str]:
        """Extract product features."""

        features = []

        feature_selectors = [
            '[data-testid="features"] li',
            '.features-list li',
            '.feature-item',
            '.capabilities li',
        ]

        for selector in feature_selectors:
            elements = soup.select(selector)
            for element in elements:
                feature = element.get_text(strip=True)
                if feature and len(feature) > 2:
                    features.append(feature.lower())

        # Also look for feature keywords in text
        feature_keywords = [
            'api', 'mobile', 'analytics', 'reporting', 'dashboard',
            'integration', 'automation', 'workflow', 'collaboration',
            'security', 'sso', 'saml', 'oauth', 'role-based',
            'customization', 'custom fields', 'templates',
            'notifications', 'alerts', 'email', 'sms',
        ]

        page_text = soup.get_text().lower()
        for keyword in feature_keywords:
            if keyword in page_text and keyword not in features:
                features.append(keyword)

        return list(set(features))

    def _extract_ratings(self, soup) -> dict:
        """Extract G2 ratings and review counts."""

        rating_data = {}

        # Look for rating information
        rating_selectors = [
            '[data-testid="rating"]',
            '.rating-score',
            '.stars-wrapper',
        ]

        for selector in rating_selectors:
            element = soup.select_one(selector)
            if element:
                rating_text = element.get_text(strip=True)
                rating_match = re.search(r'(\d+(?:\.\d+)?)', rating_text)
                if rating_match:
                    try:
                        rating_data["rating"] = float(rating_match.group(1))
                    except ValueError:
                        pass

        # Look for review count
        review_selectors = [
            '[data-testid="review-count"]',
            '.review-count',
            'span[class*="review"]',
        ]

        for selector in review_selectors:
            element = soup.select_one(selector)
            if element:
                review_text = element.get_text(strip=True)
                review_match = re.search(r'(\d+(?:,\d+)*)', review_text)
                if review_match:
                    try:
                        count_str = review_match.group(1).replace(',', '')
                        rating_data["reviews_count"] = int(count_str)
                    except ValueError:
                        pass

        return rating_data

    def _extract_company_info(self, soup) -> dict:
        """Extract company information."""

        company_info = {}

        # Look for company details section
        info_selectors = [
            '[data-testid="company-info"]',
            '.company-details',
            '.vendor-info',
        ]

        for selector in info_selectors:
            section = soup.select_one(selector)
            if section:
                text = section.get_text()

                # Extract headquarters
                hq_match = re.search(r'headquarters:?\s*([^,\n]+)', text, re.IGNORECASE)
                if hq_match:
                    company_info["headquarters"] = hq_match.group(1).strip()

                # Extract founded year
                founded_match = re.search(r'founded:?\s*(\d{4})', text, re.IGNORECASE)
                if founded_match:
                    company_info["founded"] = int(founded_match.group(1))

                # Extract employee count
                employee_match = re.search(r'employees?:?\s*([^,\n]+)', text, re.IGNORECASE)
                if employee_match:
                    company_info["employees"] = employee_match.group(1).strip()

        return company_info

    def _extract_compliance(self, soup) -> dict:
        """Extract compliance and certification information."""

        compliance_data = {
            "certifications": [],
            "frameworks": []
        }

        # Look for security/compliance section
        compliance_selectors = [
            '[data-testid="security"]',
            '.compliance-section',
            '.security-features',
        ]

        compliance_keywords = {
            "certifications": ["iso", "soc", "pci", "fips", "fedramp", "hipaa"],
            "frameworks": ["gdpr", "ccpa", "sox", "coso", "nist"]
        }

        page_text = soup.get_text().lower()

        for cert_type, keywords in compliance_keywords.items():
            for keyword in keywords:
                if keyword in page_text:
                    if keyword.upper() not in compliance_data[cert_type]:
                        compliance_data[cert_type].append(keyword.upper())

        return compliance_data

    def _extract_support_channels(self, soup) -> List[str]:
        """Extract support channel information."""

        channels = []

        # Look for support information
        support_text = soup.get_text().lower()

        channel_keywords = {
            "email": ["email", "support@", "contact@"],
            "phone": ["phone", "call", "1-800", "1-888", "1-877"],
            "chat": ["live chat", "chat support", "online chat"],
            "ticket": ["ticket", "help desk", "support portal"],
            "community": ["community", "forum", "knowledge base", "kb"],
        }

        for channel, keywords in channel_keywords.items():
            if any(keyword in support_text for keyword in keywords):
                channels.append(channel)

        return channels

    def _calculate_confidence_score(self, soup) -> float:
        """Calculate confidence score based on available data."""

        score = 0.0

        # Check for presence of key information
        checks = [
            ("name", soup.select_one('h1')),
            ("description", soup.select_one('[data-testid="product-description"]')),
            ("website", soup.select_one('a[data-testid="visit-website"]')),
            ("pricing", 'pricing' in soup.get_text().lower()),
            ("features", soup.select('.features-list li, .feature-item')),
            ("rating", soup.select_one('.rating-score, [data-testid="rating"]')),
        ]

        for check_name, result in checks:
            if result:
                if check_name in ["features"] and isinstance(result, list) and len(result) > 3:
                    score += 0.2
                elif result:
                    score += 0.15

        return min(score, 1.0)


# Example usage and testing
if __name__ == "__main__":
    scraper = G2Scraper()

    # Test scraping CRM category
    vendors = scraper.scrape_vendor_directory("crm", limit=5)
    print(f"Found {len(vendors)} vendors")

    for vendor in vendors:
        print(f"\nVendor: {vendor.name}")
        print(f"Category: {vendor.category}")
        print(f"Price: ${vendor.starting_price}")
        print(f"Features: {vendor.features[:5]}")
        print(f"Rating: {vendor.g2_rating}")
        print(f"Confidence: {vendor.confidence_score:.2f}")