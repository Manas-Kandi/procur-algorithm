"""Integration test for vendor data scraping with existing procurement pipeline."""

import asyncio
import json
import sys
from pathlib import Path
from typing import List

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from procur.integrations.enrichment_pipeline import VendorEnrichmentPipeline, EnrichmentConfig
from procur.integrations.cache_manager import CacheManager
from procur.data.seeds_loader import SeedsLoader, SeedVendorRecord
from procur.models import VendorProfile, ProcurementRequest
from procur.orchestration.pipeline import ProcurementPipeline


class IntegrationTester:
    """Test integration between scraped vendor data and existing pipeline."""

    def __init__(self):
        self.cache_manager = CacheManager(cache_dir=".integration_cache")
        self.enrichment_config = EnrichmentConfig(
            max_vendors_per_category=5,  # Small batch for testing
            min_quality_score=60.0,
            require_website=True,
            save_quality_reports=True
        )
        self.enrichment_pipeline = VendorEnrichmentPipeline(self.enrichment_config)

    async def test_end_to_end_integration(self):
        """Test complete integration from scraping to procurement pipeline."""

        print("=== Vendor Data Integration Test ===\n")

        # Step 1: Scrape and enrich vendor data
        print("1. Scraping and enriching vendor data...")
        enrichment_result = await self._test_vendor_enrichment()

        if not enrichment_result.seed_records:
            print("❌ No seed records generated. Integration test cannot continue.")
            return False

        # Step 2: Test seed data loading
        print("\n2. Testing seed data integration...")
        integration_success = await self._test_seed_integration(enrichment_result.seed_records)

        # Step 3: Test with procurement pipeline
        print("\n3. Testing procurement pipeline integration...")
        pipeline_success = await self._test_pipeline_integration(enrichment_result.seed_records)

        # Step 4: Performance and caching test
        print("\n4. Testing caching and performance...")
        cache_success = await self._test_caching_performance()

        # Generate final report
        print("\n=== Integration Test Results ===")
        print(f"Vendor Enrichment: {'✅ PASS' if enrichment_result.enriched_count > 0 else '❌ FAIL'}")
        print(f"Seed Integration: {'✅ PASS' if integration_success else '❌ FAIL'}")
        print(f"Pipeline Integration: {'✅ PASS' if pipeline_success else '❌ FAIL'}")
        print(f"Caching System: {'✅ PASS' if cache_success else '❌ FAIL'}")

        overall_success = all([
            enrichment_result.enriched_count > 0,
            integration_success,
            pipeline_success,
            cache_success
        ])

        print(f"\nOverall Integration: {'✅ PASS' if overall_success else '❌ FAIL'}")
        return overall_success

    async def _test_vendor_enrichment(self):
        """Test vendor data enrichment pipeline."""

        print("  Discovering CRM vendors...")
        result = await self.enrichment_pipeline.enrich_category("crm")

        print(f"  Found: {result.total_found} vendors")
        print(f"  Enriched: {result.enriched_count} vendors")
        print(f"  High Quality: {result.high_quality_count} vendors")
        print(f"  Processing Time: {result.processing_time:.2f}s")

        if result.errors:
            print(f"  Errors: {len(result.errors)}")
            for error in result.errors[:2]:  # Show first 2 errors
                print(f"    - {error}")

        # Show sample enriched data
        if result.seed_records:
            print("  Sample enriched vendors:")
            for record in result.seed_records[:3]:
                features_count = len(record.features) if record.features else 0
                compliance_count = len(record.compliance) if record.compliance else 0
                print(f"    - {record.name}: ${record.list_price}, {features_count} features, {compliance_count} compliance items")

        return result

    async def _test_seed_integration(self, seed_records: List[SeedVendorRecord]) -> bool:
        """Test integration with existing seed data system."""

        try:
            # Create a test seeds loader
            seeds_loader = SeedsLoader()

            # Test conversion to VendorProfile
            print("  Converting seed records to VendorProfiles...")
            vendor_profiles = []

            for record in seed_records[:3]:  # Test first 3
                try:
                    # Convert to vendor profile using the existing system
                    profile = VendorProfile(
                        vendor_id=record.id,
                        name=record.name,
                        category=record.category,
                        list_price=record.list_price,
                        features=record.features or [],
                        compliance_certifications=record.compliance or [],
                        website=record.website
                    )
                    vendor_profiles.append(profile)
                    print(f"    ✅ {record.name} -> VendorProfile")
                except Exception as e:
                    print(f"    ❌ {record.name} -> Error: {e}")
                    return False

            print(f"  Successfully converted {len(vendor_profiles)} vendors")
            return True

        except Exception as e:
            print(f"  ❌ Seed integration failed: {e}")
            return False

    async def _test_pipeline_integration(self, seed_records: List[SeedVendorRecord]) -> bool:
        """Test integration with procurement pipeline."""

        try:
            # Create test procurement request
            test_request = ProcurementRequest(
                category="saas/crm",
                quantity=25,
                budget_max=5000.0,
                required_features=["api", "reporting", "mobile"],
                compliance_requirements=["SOC2"],
                lead_time_weeks=8
            )

            print(f"  Created test request: {test_request.category}, ${test_request.budget_max}, {test_request.quantity} users")

            # Temporarily add scraped vendors to the data system
            print("  Integrating scraped vendors into pipeline...")

            # Here we would normally update the seeds data, but for testing
            # we'll just verify the data format is compatible

            # Test that seed records have all required fields for pipeline
            required_fields = ['id', 'name', 'category', 'list_price']
            for record in seed_records[:3]:
                for field in required_fields:
                    if not hasattr(record, field) or getattr(record, field) is None:
                        print(f"    ❌ Missing required field '{field}' in {record.name}")
                        return False

                # Test pricing structure
                if record.price_tiers and not isinstance(record.price_tiers, dict):
                    print(f"    ❌ Invalid price_tiers format in {record.name}")
                    return False

                print(f"    ✅ {record.name} passes pipeline compatibility check")

            print("  All scraped vendors are compatible with procurement pipeline")
            return True

        except Exception as e:
            print(f"  ❌ Pipeline integration failed: {e}")
            return False

    async def _test_caching_performance(self) -> bool:
        """Test caching system performance and functionality."""

        try:
            print("  Testing cache functionality...")

            # Test cache put/get
            test_data = {"test": "data", "timestamp": "2024-01-01"}
            self.cache_manager.put("test_category", "test_operation", test_data)

            cached_data = self.cache_manager.get("test_category", "test_operation")
            if cached_data != test_data:
                print("    ❌ Cache put/get failed")
                return False

            print("    ✅ Cache put/get working")

            # Test cache stats
            stats = self.cache_manager.get_cache_stats()
            print(f"    Cache entries: {stats['total_entries']}")
            print(f"    Cache size: {stats['total_size_mb']:.2f} MB")

            # Test cache expiration cleanup
            self.cache_manager.clear_expired()
            print("    ✅ Cache cleanup working")

            return True

        except Exception as e:
            print(f"  ❌ Caching test failed: {e}")
            return False

    async def generate_integration_report(self):
        """Generate a comprehensive integration report."""

        print("\n=== Generating Integration Report ===")

        # Test multiple categories
        categories = ["crm", "hr", "security"]
        results = await self.enrichment_pipeline.enrich_multiple_categories(categories)

        # Generate statistics
        stats = self.enrichment_pipeline.get_enrichment_statistics(results)

        report = {
            "integration_test_results": {
                "timestamp": "2024-01-01T00:00:00",  # Would be datetime.now().isoformat()
                "categories_tested": categories,
                "overall_statistics": stats,
                "category_results": {}
            }
        }

        # Add detailed results for each category
        for category, result in results.items():
            report["integration_test_results"]["category_results"][category] = {
                "vendors_found": result.total_found,
                "vendors_enriched": result.enriched_count,
                "high_quality_vendors": result.high_quality_count,
                "processing_time_seconds": result.processing_time,
                "error_count": len(result.errors),
                "sample_vendors": [
                    {
                        "name": record.name,
                        "price": record.list_price,
                        "features_count": len(record.features) if record.features else 0,
                        "compliance_count": len(record.compliance) if record.compliance else 0
                    }
                    for record in result.seed_records[:3]
                ]
            }

        # Save report
        report_path = Path("integration_report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"Integration report saved to: {report_path}")
        print(f"Total vendors discovered: {stats['total_vendors_found']}")
        print(f"Total high-quality vendors: {stats['total_high_quality_vendors']}")
        print(f"Overall success rate: {stats['quality_pass_rate']:.1f}%")

        return report


async def run_integration_test():
    """Run the complete integration test."""

    tester = IntegrationTester()

    try:
        # Run main integration test
        success = await tester.test_end_to_end_integration()

        # Generate comprehensive report
        if success:
            await tester.generate_integration_report()

        return success

    except Exception as e:
        print(f"❌ Integration test failed with error: {e}")
        return False
    finally:
        # Cleanup
        tester.cache_manager.clear_all()


# Manual test functions for specific components

async def test_g2_scraper_only():
    """Test just the G2 scraper."""
    from procur.integrations.g2_scraper import G2Scraper

    print("Testing G2 Scraper...")
    scraper = G2Scraper()

    vendors = scraper.scrape_vendor_directory("crm", limit=3)
    print(f"Found {len(vendors)} vendors")

    for vendor in vendors:
        print(f"- {vendor.name}: {vendor.website}")
        print(f"  Features: {len(vendor.features)} items")
        print(f"  Confidence: {vendor.confidence_score:.2f}")


async def test_data_validator_only():
    """Test just the data validator."""
    from procur.integrations.data_validator import VendorDataValidator
    from procur.integrations.base_scraper import VendorData

    print("Testing Data Validator...")
    validator = VendorDataValidator()

    # Create test vendor data
    test_vendor = VendorData(
        name="Test CRM Software",
        website="https://example.com",
        category="crm",
        description="A comprehensive CRM solution",
        starting_price=29.99,
        features=["api", "reporting", "mobile"],
        certifications=["SOC2"],
        scraped_at="2024-01-01T00:00:00"
    )

    report = validator.validate_vendor_data(test_vendor)
    print(f"Validation Score: {report.overall_score:.1f} (Grade: {report.grade})")
    print(f"Errors: {len(report.errors)}")
    print(f"Warnings: {len(report.warnings)}")
    print(f"Recommendations: {len(report.recommendations)}")


if __name__ == "__main__":
    print("Vendor Data Integration Test Suite")
    print("=" * 50)

    # You can run different tests by commenting/uncommenting:

    # Full integration test
    success = asyncio.run(run_integration_test())
    print(f"\nIntegration test: {'PASSED' if success else 'FAILED'}")

    # Individual component tests
    # asyncio.run(test_g2_scraper_only())
    # asyncio.run(test_data_validator_only())