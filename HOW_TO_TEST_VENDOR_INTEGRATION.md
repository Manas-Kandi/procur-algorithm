# How to Test the Real Vendor Data Integration System

## Quick Setup

### 1. Install Dependencies
```bash
cd /Users/manaskandimalla/Desktop/Projects/procur-2
pip install requests beautifulsoup4 aiohttp
```

### 2. Run the Standalone Test (No Dependencies Required)
```bash
python src/procur/integrations/standalone_test.py
```
This validates all core algorithms and data structures work correctly.

## Testing Individual Components

### Test 1: Basic Import Check
```bash
python -c "
import sys
sys.path.insert(0, 'src')

try:
    from procur.integrations import G2Scraper, VendorEnrichmentPipeline
    print('✅ Integration system imported successfully')
    print('Available: G2Scraper, PricingScraper, ComplianceScraper')
    print('Available: VendorDataValidator, VendorEnrichmentPipeline')
except ImportError as e:
    print(f'❌ Import failed: {e}')
    print('Run: pip install requests beautifulsoup4 aiohttp')
"
```

### Test 2: G2 Scraper (Live Data)
```python
# Create file: test_g2_scraper.py
import asyncio
import sys
sys.path.insert(0, 'src')

from procur.integrations.g2_scraper import G2Scraper

async def test_g2_scraper():
    print("Testing G2 Scraper with live data...")

    scraper = G2Scraper()

    # Test small batch
    vendors = scraper.scrape_vendor_directory("crm", limit=3)

    print(f"Found {len(vendors)} CRM vendors:")
    for vendor in vendors:
        print(f"- {vendor.name}")
        print(f"  Website: {vendor.website}")
        print(f"  Features: {len(vendor.features)} items")
        print(f"  Rating: {vendor.g2_rating}")
        print(f"  Confidence: {vendor.confidence_score:.2f}")
        print()

if __name__ == "__main__":
    asyncio.run(test_g2_scraper())
```

Run with: `python test_g2_scraper.py`

### Test 3: Complete Enrichment Pipeline
```python
# Create file: test_enrichment.py
import asyncio
import sys
sys.path.insert(0, 'src')

from procur.integrations.enrichment_pipeline import VendorEnrichmentPipeline, EnrichmentConfig

async def test_enrichment_pipeline():
    print("Testing Complete Enrichment Pipeline...")

    # Configure for quick test
    config = EnrichmentConfig(
        max_vendors_per_category=5,
        min_quality_score=50.0,
        require_website=True,
        save_quality_reports=True
    )

    pipeline = VendorEnrichmentPipeline(config)

    # Test single category
    result = await pipeline.enrich_category("crm")

    print(f"Results for CRM:")
    print(f"  Total Found: {result.total_found}")
    print(f"  Enriched: {result.enriched_count}")
    print(f"  High Quality: {result.high_quality_count}")
    print(f"  Processing Time: {result.processing_time:.2f}s")

    if result.errors:
        print(f"  Errors: {result.errors}")

    # Show sample enriched vendors
    print(f"\nSample Enriched Vendors:")
    for i, record in enumerate(result.seed_records[:3]):
        print(f"{i+1}. {record.name}")
        print(f"   Price: ${record.list_price}/month")
        print(f"   Features: {len(record.features or [])} items")
        print(f"   Compliance: {len(record.compliance or [])} certifications")
        print()

    # Save results
    pipeline.save_enrichment_results({"crm": result}, "test_output")
    print("Results saved to test_output/")

if __name__ == "__main__":
    asyncio.run(test_enrichment_pipeline())
```

Run with: `python test_enrichment.py`

### Test 4: Data Quality Validation
```python
# Create file: test_validation.py
import sys
sys.path.insert(0, 'src')

from procur.integrations.data_validator import VendorDataValidator
from procur.integrations.base_scraper import VendorData

def test_data_validation():
    print("Testing Data Quality Validation...")

    validator = VendorDataValidator()

    # Create test vendors with different quality levels
    test_vendors = [
        VendorData(
            name="High Quality CRM",
            website="https://example.com",
            description="Comprehensive CRM solution with advanced features",
            starting_price=29.99,
            features=["api", "reporting", "mobile", "automation"],
            certifications=["SOC2_TYPE2", "ISO27001"],
            compliance_frameworks=["GDPR"],
            scraped_at="2024-01-01T00:00:00"
        ),
        VendorData(
            name="Medium Quality Tool",
            website="https://example.com",
            starting_price=19.99,
            features=["api"],
            scraped_at="2024-01-01T00:00:00"
        ),
        VendorData(
            name="Low Quality Entry"
        )
    ]

    for vendor in test_vendors:
        report = validator.validate_vendor_data(vendor)

        print(f"\n{vendor.name}:")
        print(f"  Overall Score: {report.overall_score:.1f}/100 (Grade: {report.grade})")
        print(f"  Completeness: {report.completeness_score:.1f}%")
        print(f"  Accuracy: {report.accuracy_score:.1f}%")
        print(f"  Freshness: {report.freshness_score:.1f}%")

        if report.errors:
            print(f"  Errors: {len(report.errors)}")
        if report.warnings:
            print(f"  Warnings: {len(report.warnings)}")
        if report.recommendations:
            print(f"  Recommendations: {report.recommendations[0]}")

if __name__ == "__main__":
    test_data_validation()
```

Run with: `python test_validation.py`

## Interactive Testing

### Option 1: Python REPL
```bash
cd /Users/manaskandimalla/Desktop/Projects/procur-2
python
```

```python
import sys
sys.path.insert(0, 'src')

# Quick single vendor test
from procur.integrations.g2_scraper import G2Scraper
scraper = G2Scraper()
vendors = scraper.scrape_vendor_directory("crm", limit=1)
print(f"Found: {vendors[0].name if vendors else 'No vendors'}")

# Quick validation test
from procur.integrations.data_validator import VendorDataValidator
from procur.integrations.base_scraper import VendorData

validator = VendorDataValidator()
test_vendor = VendorData(name="Test", website="https://test.com", starting_price=29.99)
report = validator.validate_vendor_data(test_vendor)
print(f"Quality Score: {report.overall_score:.1f}")
```

### Option 2: Jupyter Notebook
```bash
pip install jupyter
jupyter notebook
```

Create a new notebook and run:
```python
import sys
sys.path.insert(0, 'src')

from procur.integrations import VendorEnrichmentPipeline, EnrichmentConfig

# Configure pipeline
config = EnrichmentConfig(max_vendors_per_category=3)
pipeline = VendorEnrichmentPipeline(config)

# Run enrichment
result = await pipeline.enrich_category("crm")

# Display results
import pandas as pd
df = pd.DataFrame([{
    'name': r.name,
    'price': r.list_price,
    'features': len(r.features or []),
    'compliance': len(r.compliance or [])
} for r in result.seed_records])

df
```

## Production Testing

### Test Real Integration with Pipeline
```python
# Create file: test_pipeline_integration.py
import asyncio
import sys
sys.path.insert(0, 'src')

async def test_pipeline_integration():
    """Test integration with existing procurement pipeline"""

    # 1. Generate real vendor data
    from procur.integrations import VendorEnrichmentPipeline

    pipeline = VendorEnrichmentPipeline()
    result = await pipeline.enrich_category("crm")

    print(f"Generated {len(result.seed_records)} seed records")

    # 2. Test with procurement request (mock)
    print("\nTesting with mock procurement request...")

    for record in result.seed_records[:3]:
        print(f"Vendor: {record.name}")
        print(f"  Category: {record.category}")
        print(f"  Price: ${record.list_price}")
        print(f"  Price Tiers: {list(record.price_tiers.keys())}")
        print(f"  Features: {len(record.features or [])}")
        print(f"  Compliance: {record.compliance}")
        print()

    # 3. Save for pipeline import
    import json
    seed_data = [record.to_dict() for record in result.seed_records]

    with open("real_vendor_seeds.json", "w") as f:
        json.dump(seed_data, f, indent=2)

    print("Real vendor data saved to: real_vendor_seeds.json")
    print("This can be imported into your procurement pipeline!")

if __name__ == "__main__":
    asyncio.run(test_pipeline_integration())
```

## Performance Testing

### Test Caching System
```python
# Create file: test_caching.py
import sys
sys.path.insert(0, 'src')

from procur.integrations.cache_manager import CacheManager
import time

def test_caching():
    cache = CacheManager(cache_dir=".test_cache")

    # Test cache performance
    test_data = {"vendors": ["vendor1", "vendor2"], "timestamp": time.time()}

    # Test put/get
    start = time.time()
    cache.put("test", "vendors", test_data)
    put_time = time.time() - start

    start = time.time()
    cached_data = cache.get("test", "vendors")
    get_time = time.time() - start

    print(f"Cache put time: {put_time*1000:.2f}ms")
    print(f"Cache get time: {get_time*1000:.2f}ms")
    print(f"Data matches: {cached_data == test_data}")

    # Test cache stats
    stats = cache.get_cache_stats()
    print(f"Cache entries: {stats['total_entries']}")
    print(f"Cache size: {stats['total_size_mb']:.2f} MB")

    # Cleanup
    cache.clear_all()

if __name__ == "__main__":
    test_caching()
```

## Troubleshooting

### Common Issues

1. **ImportError: No module named 'requests'**
   ```bash
   pip install requests beautifulsoup4 aiohttp
   ```

2. **No vendors found**
   - Check internet connection
   - G2.com may have changed structure
   - Try different category: "hr", "security", "analytics"

3. **Rate limiting errors**
   - Reduce `max_vendors_per_category` in config
   - Increase delays in `ScrapingConfig`

4. **Low quality scores**
   - Reduce `min_quality_score` threshold
   - Check validation rules in `data_validator.py`

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run any test with verbose output
```

## Next Steps

After testing, you can:

1. **Generate Production Data**:
   ```bash
   python -c "
   import asyncio
   from procur.integrations import enrich_saas_categories
   results = asyncio.run(enrich_saas_categories())
   print(f'Generated data for {len(results)} categories')
   "
   ```

2. **Replace Mock Seeds**: Use generated `real_vendor_seeds.json` to replace toy data

3. **Schedule Regular Updates**: Set up cron job to refresh vendor data weekly

4. **Monitor Quality**: Track validation scores and error rates

5. **Expand Categories**: Add more SaaS categories or new data sources

The system is now ready for production use! Start with the standalone test to verify everything works, then progress to live data testing based on your needs.