"""Vendor website pricing scraper for detailed pricing intelligence."""

from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

from .base_scraper import BaseScraper, VendorData


class PricingScraper(BaseScraper):
    """Scraper for vendor website pricing pages."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pricing_patterns = self._compile_pricing_patterns()

    def _compile_pricing_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for pricing extraction."""
        return {
            "monthly_price": re.compile(r'\$(\d+(?:\.\d{2})?)\s*(?:/\s*(?:month|mo|user/month|seat/month))', re.IGNORECASE),
            "annual_price": re.compile(r'\$(\d+(?:\.\d{2})?)\s*(?:/\s*(?:year|yr|annually|user/year|seat/year))', re.IGNORECASE),
            "starting_at": re.compile(r'starting\s+(?:at|from)\s*\$(\d+(?:\.\d{2})?)', re.IGNORECASE),
            "per_user": re.compile(r'\$(\d+(?:\.\d{2})?)\s*(?:per\s+(?:user|seat|employee))', re.IGNORECASE),
            "free_tier": re.compile(r'free\s+(?:tier|plan|forever)', re.IGNORECASE),
            "custom_pricing": re.compile(r'(?:custom|enterprise|contact\s+(?:us|sales))\s+pricing', re.IGNORECASE),
        }

    def scrape_vendor_pricing(self, vendor_website: str) -> Optional[Dict]:
        """Scrape pricing information from vendor website."""

        if not vendor_website:
            return None

        # Find pricing page URL
        pricing_url = self._find_pricing_page(vendor_website)
        if not pricing_url:
            return None

        # Scrape pricing page
        response = self._make_request(pricing_url)
        if not response:
            return None

        soup = self._parse_html(response.text)
        pricing_data = self._extract_pricing_data(soup, pricing_url)

        return pricing_data

    def _find_pricing_page(self, website: str) -> Optional[str]:
        """Find the pricing page URL for a vendor website."""

        # Common pricing page paths
        pricing_paths = [
            '/pricing',
            '/plans',
            '/plans-pricing',
            '/pricing-plans',
            '/buy',
            '/subscribe',
            '/packages',
            '/cost',
        ]

        # First try direct pricing page URLs
        for path in pricing_paths:
            pricing_url = urljoin(website, path)
            response = self._make_request(pricing_url)
            if response and response.status_code == 200:
                # Check if this actually contains pricing content
                if self._has_pricing_content(response.text):
                    return pricing_url

        # If no direct pricing page found, scrape main page for pricing links
        response = self._make_request(website)
        if not response:
            return None

        soup = self._parse_html(response.text)
        pricing_links = self._extract_pricing_links(soup, website)

        # Return the first valid pricing link
        for link in pricing_links:
            response = self._make_request(link)
            if response and self._has_pricing_content(response.text):
                return link

        return None

    def _has_pricing_content(self, html: str) -> bool:
        """Check if HTML contains pricing content."""
        pricing_indicators = [
            'pricing', 'plans', 'subscribe', 'buy now',
            '$', 'free', 'trial', 'monthly', 'annually',
            'per user', 'per seat', 'per month'
        ]

        text = html.lower()
        return sum(indicator in text for indicator in pricing_indicators) >= 3

    def _extract_pricing_links(self, soup, base_url: str) -> List[str]:
        """Extract pricing page links from main page."""

        links = []

        # Look for navigation links
        nav_selectors = [
            'nav a', '.navigation a', '.navbar a',
            '.menu a', '.header a', '.top-menu a'
        ]

        pricing_keywords = ['pricing', 'plans', 'buy', 'subscribe', 'cost']

        for selector in nav_selectors:
            elements = soup.select(selector)
            for element in elements:
                href = element.get('href', '')
                text = element.get_text(strip=True).lower()

                if any(keyword in text for keyword in pricing_keywords):
                    full_url = urljoin(base_url, href)
                    if full_url not in links:
                        links.append(full_url)

        # Look for pricing buttons/CTAs
        cta_selectors = [
            'a[class*="pricing"]', 'a[class*="plan"]',
            'a[href*="pricing"]', 'a[href*="plan"]',
            '.cta a', '.button a'
        ]

        for selector in cta_selectors:
            elements = soup.select(selector)
            for element in elements:
                href = element.get('href', '')
                if href:
                    full_url = urljoin(base_url, href)
                    if full_url not in links:
                        links.append(full_url)

        return links

    def _extract_pricing_data(self, soup, url: str) -> Dict:
        """Extract comprehensive pricing data from pricing page."""

        pricing_data = {
            "source_url": url,
            "scraped_at": datetime.now().isoformat(),
            "plans": [],
            "features_by_plan": {},
            "pricing_model": None,
            "billing_cycles": [],
            "free_tier": False,
            "trial_period": None,
            "currency": "USD",
            "additional_fees": {},
            "enterprise_pricing": False,
        }

        # Extract pricing plans
        plans = self._extract_pricing_plans(soup)
        pricing_data["plans"] = plans

        # Extract features by plan
        pricing_data["features_by_plan"] = self._extract_plan_features(soup)

        # Determine pricing model
        pricing_data["pricing_model"] = self._determine_pricing_model(soup)

        # Extract billing cycles
        pricing_data["billing_cycles"] = self._extract_billing_cycles(soup)

        # Check for free tier
        pricing_data["free_tier"] = self._has_free_tier(soup)

        # Extract trial information
        pricing_data["trial_period"] = self._extract_trial_period(soup)

        # Extract additional fees
        pricing_data["additional_fees"] = self._extract_additional_fees(soup)

        # Check for enterprise pricing
        pricing_data["enterprise_pricing"] = self._has_enterprise_pricing(soup)

        return pricing_data

    def _extract_pricing_plans(self, soup) -> List[Dict]:
        """Extract individual pricing plans."""

        plans = []

        # Look for pricing plan containers
        plan_selectors = [
            '.pricing-plan', '.plan', '.price-tier',
            '.pricing-card', '.pricing-column',
            '[class*="plan"]', '[class*="tier"]'
        ]

        plan_elements = []
        for selector in plan_selectors:
            elements = soup.select(selector)
            if elements and len(elements) > 1:  # Multiple plans found
                plan_elements = elements
                break

        for element in plan_elements:
            plan = self._extract_single_plan(element)
            if plan and plan["name"]:
                plans.append(plan)

        # If no structured plans found, try to extract from pricing text
        if not plans:
            plans = self._extract_plans_from_text(soup)

        return plans

    def _extract_single_plan(self, element) -> Dict:
        """Extract data from a single pricing plan element."""

        plan = {
            "name": "",
            "price": None,
            "billing_cycle": "monthly",
            "features": [],
            "recommended": False,
            "description": ""
        }

        # Extract plan name
        name_selectors = [
            'h1', 'h2', 'h3', 'h4',
            '.plan-name', '.tier-name',
            '[class*="title"]', '[class*="name"]'
        ]

        for selector in name_selectors:
            name_element = element.select_one(selector)
            if name_element:
                name = name_element.get_text(strip=True)
                if len(name) < 50:  # Reasonable plan name length
                    plan["name"] = name
                    break

        # Extract price
        price_selectors = [
            '.price', '.amount', '.cost',
            '[class*="price"]', '[class*="amount"]'
        ]

        for selector in price_selectors:
            price_element = element.select_one(selector)
            if price_element:
                price_text = price_element.get_text(strip=True)
                price = self._extract_price(price_text)
                if price:
                    plan["price"] = price

                    # Determine billing cycle from price text
                    if any(term in price_text.lower() for term in ['month', 'mo', '/m']):
                        plan["billing_cycle"] = "monthly"
                    elif any(term in price_text.lower() for term in ['year', 'yr', 'annual']):
                        plan["billing_cycle"] = "annually"
                    break

        # Extract features
        feature_selectors = [
            'ul li', '.features li', '.feature-list li',
            '.checkmark + span', '.check + span'
        ]

        for selector in feature_selectors:
            feature_elements = element.select(selector)
            for feature_elem in feature_elements:
                feature = feature_elem.get_text(strip=True)
                if feature and len(feature) > 3 and feature not in plan["features"]:
                    plan["features"].append(feature)

        # Check if recommended/popular
        element_text = element.get_text().lower()
        if any(term in element_text for term in ['popular', 'recommended', 'best value', 'most popular']):
            plan["recommended"] = True

        # Extract description
        desc_selectors = [
            '.description', '.plan-desc', '.tier-description',
            'p', '.subtitle'
        ]

        for selector in desc_selectors:
            desc_element = element.select_one(selector)
            if desc_element:
                desc = desc_element.get_text(strip=True)
                if 20 < len(desc) < 200:  # Reasonable description length
                    plan["description"] = desc
                    break

        return plan

    def _extract_plans_from_text(self, soup) -> List[Dict]:
        """Extract plans from unstructured pricing text."""

        plans = []
        text = soup.get_text()

        # Look for pricing patterns in text
        for pattern_name, pattern in self.pricing_patterns.items():
            matches = pattern.finditer(text)
            for match in matches:
                price = float(match.group(1))

                # Try to find plan name near the price
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end]

                plan_name = self._extract_plan_name_from_context(context)
                billing_cycle = "monthly" if "month" in pattern_name else "annually"

                plan = {
                    "name": plan_name or f"{pattern_name.replace('_', ' ').title()} Plan",
                    "price": price,
                    "billing_cycle": billing_cycle,
                    "features": [],
                    "recommended": False,
                    "description": ""
                }

                plans.append(plan)

        return plans

    def _extract_plan_name_from_context(self, context: str) -> Optional[str]:
        """Extract plan name from text context around price."""

        # Look for common plan name patterns
        plan_patterns = [
            r'(Basic|Standard|Professional|Premium|Enterprise|Starter|Pro|Business|Team)\s+(?:Plan)?',
            r'(\w+)\s+Plan',
            r'(\w+)\s+Tier',
        ]

        for pattern in plan_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _determine_pricing_model(self, soup) -> Optional[str]:
        """Determine the overall pricing model."""

        text = soup.get_text().lower()

        if any(term in text for term in ['per user', 'per seat', 'per employee']):
            return "per_user"
        elif any(term in text for term in ['flat rate', 'fixed price', 'one price']):
            return "flat_rate"
        elif any(term in text for term in ['usage based', 'pay as you go', 'consumption']):
            return "usage_based"
        elif any(term in text for term in ['freemium', 'free tier']):
            return "freemium"
        elif any(term in text for term in ['subscription', 'monthly', 'annually']):
            return "subscription"

        return None

    def _extract_billing_cycles(self, soup) -> List[str]:
        """Extract available billing cycles."""

        cycles = []
        text = soup.get_text().lower()

        cycle_indicators = {
            "monthly": ["monthly", "per month", "/month", "/mo"],
            "annually": ["annually", "per year", "/year", "/yr", "yearly"],
            "quarterly": ["quarterly", "per quarter", "/quarter"],
            "one_time": ["one time", "lifetime", "perpetual"]
        }

        for cycle, indicators in cycle_indicators.items():
            if any(indicator in text for indicator in indicators):
                cycles.append(cycle)

        return cycles

    def _has_free_tier(self, soup) -> bool:
        """Check if there's a free tier available."""

        text = soup.get_text().lower()
        free_indicators = ["free", "free tier", "free plan", "free forever", "$0"]

        return any(indicator in text for indicator in free_indicators)

    def _extract_trial_period(self, soup) -> Optional[int]:
        """Extract trial period information."""

        text = soup.get_text()
        trial_pattern = re.search(r'(\d+)[\s-]*day(?:s?)?\s+(?:free\s+)?trial', text, re.IGNORECASE)

        if trial_pattern:
            return int(trial_pattern.group(1))

        return None

    def _extract_additional_fees(self, soup) -> Dict[str, float]:
        """Extract additional fees like setup, support, etc."""

        fees = {}
        text = soup.get_text().lower()

        fee_patterns = [
            (r'setup fee[:\s]*\$(\d+(?:\.\d{2})?)', "setup_fee"),
            (r'implementation fee[:\s]*\$(\d+(?:\.\d{2})?)', "implementation_fee"),
            (r'support fee[:\s]*\$(\d+(?:\.\d{2})?)', "support_fee"),
            (r'training fee[:\s]*\$(\d+(?:\.\d{2})?)', "training_fee"),
        ]

        for pattern, fee_type in fee_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fees[fee_type] = float(match.group(1))

        return fees

    def _has_enterprise_pricing(self, soup) -> bool:
        """Check if enterprise/custom pricing is available."""

        text = soup.get_text().lower()
        enterprise_indicators = [
            "enterprise pricing", "custom pricing", "contact sales",
            "contact us for pricing", "quote", "enterprise plan"
        ]

        return any(indicator in text for indicator in enterprise_indicators)

    def _extract_plan_features(self, soup) -> Dict[str, List[str]]:
        """Extract features organized by plan."""

        features_by_plan = {}

        # This is complex to implement generically
        # For now, return empty dict - can be enhanced per vendor
        return features_by_plan

    def scrape_vendor_details(self, vendor_url: str) -> Optional[VendorData]:
        """Not implemented for pricing scraper - use G2Scraper instead."""
        raise NotImplementedError("Use G2Scraper for vendor details")

    def scrape_vendor_directory(self, category: str, limit: int = 50) -> List[VendorData]:
        """Not implemented for pricing scraper - use G2Scraper instead."""
        raise NotImplementedError("Use G2Scraper for vendor directory")


# Utility function to combine pricing data with vendor data
def enrich_vendor_with_pricing(vendor_data: VendorData, pricing_scraper: PricingScraper) -> VendorData:
    """Enrich vendor data with detailed pricing information."""

    if not vendor_data.website:
        return vendor_data

    pricing_data = pricing_scraper.scrape_vendor_pricing(vendor_data.website)
    if not pricing_data:
        return vendor_data

    # Update vendor data with pricing information
    if pricing_data["plans"]:
        # Use the cheapest non-free plan as starting price
        paid_plans = [p for p in pricing_data["plans"] if p["price"] and p["price"] > 0]
        if paid_plans:
            cheapest_plan = min(paid_plans, key=lambda x: x["price"])
            vendor_data.starting_price = cheapest_plan["price"]

            # Build price tiers from plans
            for plan in paid_plans:
                tier_name = plan["name"].lower().replace(" ", "_")
                vendor_data.price_tiers[tier_name] = plan["price"]

    # Update pricing model
    if pricing_data["pricing_model"]:
        vendor_data.pricing_model = pricing_data["pricing_model"]

    # Add trial information to features
    if pricing_data["trial_period"]:
        vendor_data.features.append(f"{pricing_data['trial_period']}_day_trial")

    if pricing_data["free_tier"]:
        vendor_data.features.append("free_tier")

    # Update confidence score
    vendor_data.confidence_score = min(vendor_data.confidence_score + 0.2, 1.0)

    return vendor_data


# Example usage
if __name__ == "__main__":
    scraper = PricingScraper()

    # Test with a known SaaS pricing page
    test_websites = [
        "https://slack.com",
        "https://zoom.us",
        "https://salesforce.com"
    ]

    for website in test_websites:
        print(f"\nScraping pricing for: {website}")
        pricing_data = scraper.scrape_vendor_pricing(website)

        if pricing_data:
            print(f"Found {len(pricing_data['plans'])} plans")
            print(f"Pricing model: {pricing_data['pricing_model']}")
            print(f"Free tier: {pricing_data['free_tier']}")
            print(f"Trial: {pricing_data['trial_period']} days")
        else:
            print("No pricing data found")