#!/usr/bin/env python3
"""
Simple test runner for the G2Scraper integration.

Usage:
  source venv/bin/activate
  python examples/test_g2_scraper.py --category crm --limit 3
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, List

# Ensure local package is importable when run from repo root
sys.path.insert(0, "src")

from procur.integrations import G2Scraper  # type: ignore
from procur.integrations.cache_manager import (
    CacheManager,
    get_cached_vendor_data,
    cache_vendor_data,
)
from procur.integrations.base_scraper import VendorData


def _fallback_from_seeds(category: str, limit: int) -> List[VendorData]:
    seeds_path = Path("assets/seeds.json")
    if not seeds_path.exists():
        return []

    try:
        with open(seeds_path, "r") as f:
            data = json.load(f)
    except Exception:
        return []

    # Map category input (e.g., "crm") to seed category paths (e.g., "saas/crm")
    cat_map = {
        "crm": "saas/crm",
        "analytics": "saas/analytics",
        "security": "saas/security",
        "hr": "saas/hr",
        "erp": "saas/erp",
        "marketing": "saas/marketing",
        "project-management": "saas/project-management",
    }
    target = cat_map.get(category.lower())

    vendors: List[VendorData] = []
    for item in data:
        try:
            if target and item.get("category") != target:
                continue
            vendors.append(
                VendorData(
                    name=item.get("name", "Unknown Vendor"),
                    website=item.get("website"),
                    category=item.get("category"),
                    description=item.get("description"),
                    starting_price=item.get("list_price"),
                    price_tiers=item.get("price_tiers", {}),
                    features=item.get("features", []),
                    certifications=item.get("compliance", []),
                    compliance_frameworks=item.get("compliance", []),
                    support_channels=(item.get("support", {}) or {}).get("channels", []),
                    source_url=f"seed://{item.get('id', 'unknown')}",
                    confidence_score=0.9,
                )
            )
            if len(vendors) >= limit:
                break
        except Exception:
            continue

    return vendors


def run(category: str, limit: int) -> int:
    print(f"Testing G2 Scraper with live data... (category='{category}', limit={limit})")

    scraper = G2Scraper()
    cache = CacheManager()

    # Try cache first
    cached = get_cached_vendor_data(category, cache)
    if cached:
        vendors = cached[:limit]
        print("\nLoaded vendors from cache.")
    else:
        # Try live scrape
        try:
            vendors = scraper.scrape_vendor_directory(category, limit=limit)
        except Exception as e:
            print(f"❌ Scrape failed: {e}")
            vendors = []

        # Cache on success
        if vendors:
            try:
                cache_vendor_data(vendors, category, cache)
            except Exception:
                pass

    # Fallback to seeds if nothing found
    if not vendors:
        vendors = _fallback_from_seeds(category, limit)
        if vendors:
            print("\nUsing fallback data from assets/seeds.json (offline mode).")

    if not vendors:
        print("⚠️ No vendors found (this can happen if the category is unknown or site structure changed).")
        return 1

    print(f"\nFound {len(vendors)} {category.upper()} vendors:")
    for i, vendor in enumerate(vendors, start=1):
        print(f"\n{i}. {vendor.name}")
        print(f"   Website: {vendor.website}")
        print(f"   Category: {vendor.category}")
        print(f"   Features: {len(vendor.features)} items")
        print(f"   Starting price: {vendor.starting_price}")
        print(f"   Rating: {vendor.g2_rating} ({vendor.g2_reviews_count} reviews)")
        print(f"   Confidence: {vendor.confidence_score:.2f}")
        print(f"   Source: {vendor.source_url}")

    return 0


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Test the G2Scraper integration")
    parser.add_argument("--category", default="crm", help="G2 category to scrape (e.g., crm, hr, analytics)")
    parser.add_argument("--limit", type=int, default=3, help="Number of vendors to fetch")

    args = parser.parse_args(argv)
    return run(args.category, args.limit)


if __name__ == "__main__":
    raise SystemExit(main())
