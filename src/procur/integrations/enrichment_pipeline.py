"""Vendor data enrichment pipeline that orchestrates all scrapers and validation."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

from .base_scraper import VendorData, ScrapingConfig
from .compliance_scraper import ComplianceScraper
from .data_validator import VendorDataValidator, QualityReport
from .g2_scraper import G2Scraper
from .pricing_scraper import PricingScraper, enrich_vendor_with_pricing
from ..data.seeds_loader import SeedVendorRecord


@dataclass
class EnrichmentConfig:
    """Configuration for vendor data enrichment pipeline."""

    # Data sources to use
    use_g2_scraper: bool = True
    use_pricing_scraper: bool = True
    use_compliance_scraper: bool = True

    # Quality thresholds
    min_quality_score: float = 60.0
    require_website: bool = True
    require_pricing: bool = False

    # Processing limits
    max_vendors_per_category: int = 50
    max_concurrent_enrichments: int = 5

    # Scraping configuration
    scraping_config: Optional[ScrapingConfig] = None

    # Output preferences
    save_raw_data: bool = True
    save_quality_reports: bool = True
    output_format: str = "seed_records"  # "seed_records" or "vendor_data"


@dataclass
class EnrichmentResult:
    """Result of vendor data enrichment process."""

    category: str
    total_found: int
    enriched_count: int
    high_quality_count: int
    seed_records: List[SeedVendorRecord] = field(default_factory=list)
    quality_reports: Dict[str, QualityReport] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    processing_time: float = 0.0


class VendorEnrichmentPipeline:
    """Complete pipeline for discovering, enriching, and validating vendor data."""

    def __init__(self, config: Optional[EnrichmentConfig] = None):
        self.config = config or EnrichmentConfig()

        # Initialize scrapers
        scraping_config = self.config.scraping_config or ScrapingConfig()
        self.g2_scraper = G2Scraper(scraping_config) if self.config.use_g2_scraper else None
        self.pricing_scraper = PricingScraper(scraping_config) if self.config.use_pricing_scraper else None
        self.compliance_scraper = ComplianceScraper(scraping_config) if self.config.use_compliance_scraper else None

        # Initialize validator
        self.validator = VendorDataValidator()

    async def enrich_category(self, category: str) -> EnrichmentResult:
        """Enrich all vendors in a specific category."""

        start_time = datetime.now()
        result = EnrichmentResult(category=category, total_found=0, enriched_count=0, high_quality_count=0)

        try:
            # Step 1: Discover vendors
            vendors = await self._discover_vendors(category)
            result.total_found = len(vendors)

            if not vendors:
                result.errors.append(f"No vendors found for category: {category}")
                return result

            # Step 2: Enrich vendor data
            enriched_vendors = await self._enrich_vendors(vendors)
            result.enriched_count = len(enriched_vendors)

            # Step 3: Validate data quality
            quality_reports = self._validate_vendors(enriched_vendors)
            result.quality_reports = quality_reports

            # Step 4: Filter high-quality vendors
            high_quality_vendors = self._filter_high_quality_vendors(enriched_vendors, quality_reports)
            result.high_quality_count = len(high_quality_vendors)

            # Step 5: Convert to seed records
            result.seed_records = self._convert_to_seed_records(high_quality_vendors)

            # Calculate processing time
            result.processing_time = (datetime.now() - start_time).total_seconds()

        except Exception as e:
            result.errors.append(f"Pipeline error: {str(e)}")

        return result

    async def enrich_multiple_categories(self, categories: List[str]) -> Dict[str, EnrichmentResult]:
        """Enrich vendors across multiple categories concurrently."""

        # Create tasks for each category
        tasks = [self.enrich_category(category) for category in categories]

        # Run concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        enrichment_results = {}
        for category, result in zip(categories, results):
            if isinstance(result, Exception):
                enrichment_results[category] = EnrichmentResult(
                    category=category,
                    total_found=0,
                    enriched_count=0,
                    high_quality_count=0,
                    errors=[f"Category enrichment failed: {str(result)}"]
                )
            else:
                enrichment_results[category] = result

        return enrichment_results

    async def _discover_vendors(self, category: str) -> List[VendorData]:
        """Discover vendors using available scrapers."""

        vendors = []

        if self.g2_scraper:
            try:
                g2_vendors = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.g2_scraper.scrape_vendor_directory,
                    category,
                    self.config.max_vendors_per_category
                )
                vendors.extend(g2_vendors)
            except Exception as e:
                print(f"G2 scraper failed for {category}: {e}")

        # Remove duplicates based on vendor name
        seen_names = set()
        unique_vendors = []
        for vendor in vendors:
            name_key = vendor.name.lower().strip()
            if name_key not in seen_names:
                seen_names.add(name_key)
                unique_vendors.append(vendor)

        return unique_vendors

    async def _enrich_vendors(self, vendors: List[VendorData]) -> List[VendorData]:
        """Enrich vendors with additional data from all sources."""

        # Create semaphore to limit concurrent enrichments
        semaphore = asyncio.Semaphore(self.config.max_concurrent_enrichments)

        async def enrich_single_vendor(vendor: VendorData) -> VendorData:
            async with semaphore:
                return await asyncio.get_event_loop().run_in_executor(
                    None,
                    self._enrich_vendor_sync,
                    vendor
                )

        # Enrich all vendors concurrently
        enriched_vendors = await asyncio.gather(
            *[enrich_single_vendor(vendor) for vendor in vendors],
            return_exceptions=True
        )

        # Filter out exceptions
        valid_vendors = []
        for vendor in enriched_vendors:
            if isinstance(vendor, Exception):
                print(f"Vendor enrichment failed: {vendor}")
            else:
                valid_vendors.append(vendor)

        return valid_vendors

    def _enrich_vendor_sync(self, vendor: VendorData) -> VendorData:
        """Synchronously enrich a single vendor (called from executor)."""

        enriched_vendor = vendor

        try:
            # Enrich with pricing data
            if self.pricing_scraper:
                enriched_vendor = enrich_vendor_with_pricing(enriched_vendor, self.pricing_scraper)

            # Enrich with compliance data
            if self.compliance_scraper:
                enriched_vendor = self.compliance_scraper.enrich_vendor_with_compliance(enriched_vendor)

        except Exception as e:
            print(f"Failed to enrich {vendor.name}: {e}")

        return enriched_vendor

    def _validate_vendors(self, vendors: List[VendorData]) -> Dict[str, QualityReport]:
        """Validate all vendor data and generate quality reports."""

        quality_reports = {}

        for vendor in vendors:
            try:
                report = self.validator.validate_vendor_data(vendor)
                quality_reports[vendor.name] = report
            except Exception as e:
                print(f"Failed to validate {vendor.name}: {e}")

        return quality_reports

    def _filter_high_quality_vendors(
        self,
        vendors: List[VendorData],
        quality_reports: Dict[str, QualityReport]
    ) -> List[VendorData]:
        """Filter vendors based on quality thresholds."""

        high_quality_vendors = []

        for vendor in vendors:
            # Check if we have a quality report
            report = quality_reports.get(vendor.name)
            if not report:
                continue

            # Apply quality threshold
            if report.overall_score < self.config.min_quality_score:
                continue

            # Apply required field checks
            if self.config.require_website and not vendor.website:
                continue

            if self.config.require_pricing and not vendor.starting_price:
                continue

            high_quality_vendors.append(vendor)

        return high_quality_vendors

    def _convert_to_seed_records(self, vendors: List[VendorData]) -> List[SeedVendorRecord]:
        """Convert enriched vendor data to seed records."""

        seed_records = []

        for vendor in vendors:
            try:
                # Use the conversion method from base scraper
                from .base_scraper import BaseScraper
                scraper = BaseScraper()
                seed_record = scraper.convert_to_seed_record(vendor)
                seed_records.append(seed_record)
            except Exception as e:
                print(f"Failed to convert {vendor.name} to seed record: {e}")

        return seed_records

    def save_enrichment_results(self, results: Dict[str, EnrichmentResult], output_dir: str = "output"):
        """Save enrichment results to files."""

        import os
        os.makedirs(output_dir, exist_ok=True)

        # Save summary
        summary = {
            "enrichment_summary": {
                category: {
                    "total_found": result.total_found,
                    "enriched_count": result.enriched_count,
                    "high_quality_count": result.high_quality_count,
                    "processing_time": result.processing_time,
                    "errors": result.errors
                }
                for category, result in results.items()
            },
            "generated_at": datetime.now().isoformat()
        }

        with open(f"{output_dir}/enrichment_summary.json", "w") as f:
            json.dump(summary, f, indent=2)

        # Save seed records by category
        for category, result in results.items():
            if result.seed_records:
                seed_data = [record.to_dict() for record in result.seed_records]
                with open(f"{output_dir}/{category}_vendors.json", "w") as f:
                    json.dump(seed_data, f, indent=2)

        # Save quality reports if requested
        if self.config.save_quality_reports:
            for category, result in results.items():
                if result.quality_reports:
                    quality_data = {}
                    for vendor_name, report in result.quality_reports.items():
                        quality_data[vendor_name] = {
                            "overall_score": report.overall_score,
                            "grade": report.grade,
                            "completeness_score": report.completeness_score,
                            "accuracy_score": report.accuracy_score,
                            "freshness_score": report.freshness_score,
                            "consistency_score": report.consistency_score,
                            "errors": report.errors,
                            "warnings": report.warnings,
                            "recommendations": report.recommendations
                        }

                    with open(f"{output_dir}/{category}_quality_reports.json", "w") as f:
                        json.dump(quality_data, f, indent=2)

    def get_enrichment_statistics(self, results: Dict[str, EnrichmentResult]) -> Dict:
        """Generate statistics from enrichment results."""

        total_found = sum(result.total_found for result in results.values())
        total_enriched = sum(result.enriched_count for result in results.values())
        total_high_quality = sum(result.high_quality_count for result in results.values())
        total_errors = sum(len(result.errors) for result in results.values())

        # Quality distribution
        all_reports = {}
        for result in results.values():
            all_reports.update(result.quality_reports)

        grade_distribution = {}
        if all_reports:
            for report in all_reports.values():
                grade = report.grade
                grade_distribution[grade] = grade_distribution.get(grade, 0) + 1

        return {
            "total_vendors_found": total_found,
            "total_vendors_enriched": total_enriched,
            "total_high_quality_vendors": total_high_quality,
            "enrichment_success_rate": (total_enriched / total_found * 100) if total_found > 0 else 0,
            "quality_pass_rate": (total_high_quality / total_enriched * 100) if total_enriched > 0 else 0,
            "total_errors": total_errors,
            "grade_distribution": grade_distribution,
            "categories_processed": len(results),
        }


# Utility functions for common enrichment scenarios

async def enrich_saas_categories(config: Optional[EnrichmentConfig] = None) -> Dict[str, EnrichmentResult]:
    """Enrich common SaaS categories."""

    pipeline = VendorEnrichmentPipeline(config)

    saas_categories = [
        "crm",
        "hr",
        "analytics",
        "security",
        "marketing",
        "project-management",
        "collaboration",
        "accounting"
    ]

    return await pipeline.enrich_multiple_categories(saas_categories)


async def quick_category_enrichment(category: str, limit: int = 20) -> EnrichmentResult:
    """Quick enrichment for a single category with default settings."""

    config = EnrichmentConfig(
        max_vendors_per_category=limit,
        min_quality_score=50.0,  # Lower threshold for quick results
        require_website=False,
        require_pricing=False
    )

    pipeline = VendorEnrichmentPipeline(config)
    return await pipeline.enrich_category(category)


# Example usage
if __name__ == "__main__":
    import asyncio

    async def main():
        # Configure enrichment
        config = EnrichmentConfig(
            max_vendors_per_category=10,  # Small batch for testing
            min_quality_score=60.0,
            require_website=True,
            save_quality_reports=True
        )

        # Create pipeline
        pipeline = VendorEnrichmentPipeline(config)

        # Enrich a single category
        print("Enriching CRM vendors...")
        result = await pipeline.enrich_category("crm")

        print(f"\nResults for CRM:")
        print(f"  Found: {result.total_found}")
        print(f"  Enriched: {result.enriched_count}")
        print(f"  High Quality: {result.high_quality_count}")
        print(f"  Processing Time: {result.processing_time:.2f}s")

        if result.errors:
            print(f"  Errors: {len(result.errors)}")
            for error in result.errors[:3]:  # Show first 3 errors
                print(f"    - {error}")

        # Show sample vendors
        if result.seed_records:
            print(f"\nSample vendors:")
            for record in result.seed_records[:3]:
                print(f"  - {record.name}: ${record.list_price}")

        # Save results
        pipeline.save_enrichment_results({"crm": result}, "enrichment_output")
        print(f"\nResults saved to enrichment_output/")

    # Run the example
    asyncio.run(main())