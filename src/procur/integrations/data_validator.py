"""Advanced data validation and quality checks for scraped vendor data."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

from .base_scraper import VendorData


@dataclass
class ValidationRule:
    """Represents a single validation rule."""

    name: str
    description: str
    severity: str  # 'error', 'warning', 'info'
    weight: float = 1.0  # Weight in quality score calculation


@dataclass
class ValidationResult:
    """Result of validating a single rule."""

    rule: ValidationRule
    passed: bool
    message: str
    score_impact: float = 0.0


@dataclass
class QualityReport:
    """Complete quality assessment report for vendor data."""

    vendor_name: str
    overall_score: float
    grade: str  # A, B, C, D, F
    validation_results: List[ValidationResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    # Data completeness metrics
    completeness_score: float = 0.0
    accuracy_score: float = 0.0
    freshness_score: float = 0.0
    consistency_score: float = 0.0


class VendorDataValidator:
    """Advanced validator for vendor data quality and consistency."""

    def __init__(self):
        self.validation_rules = self._initialize_validation_rules()
        self.known_domains = self._load_known_domains()
        self.pricing_ranges = self._load_pricing_ranges()

    def _initialize_validation_rules(self) -> List[ValidationRule]:
        """Initialize all validation rules."""

        return [
            # Critical data rules
            ValidationRule("vendor_name_present", "Vendor name must be present", "error", 1.0),
            ValidationRule("vendor_name_length", "Vendor name should be reasonable length (2-100 chars)", "warning", 0.5),
            ValidationRule("website_format", "Website URL must be properly formatted", "error", 0.8),
            ValidationRule("website_accessible", "Website URL should be accessible", "warning", 0.3),

            # Pricing validation
            ValidationRule("pricing_range", "Pricing should be within reasonable range", "warning", 0.6),
            ValidationRule("pricing_consistency", "Price tiers should be consistent", "warning", 0.4),
            ValidationRule("pricing_model_valid", "Pricing model should be recognized", "info", 0.2),

            # Feature validation
            ValidationRule("features_present", "Should have at least some features listed", "warning", 0.3),
            ValidationRule("features_quality", "Features should be meaningful (not just keywords)", "info", 0.2),
            ValidationRule("features_duplicates", "Should not have duplicate features", "warning", 0.1),

            # Compliance validation
            ValidationRule("compliance_format", "Compliance certifications should follow standard format", "info", 0.2),
            ValidationRule("compliance_consistency", "Compliance data should be internally consistent", "warning", 0.3),

            # Data freshness
            ValidationRule("data_freshness", "Data should be recently scraped", "info", 0.1),
            ValidationRule("source_reliability", "Data source should be reliable", "warning", 0.4),

            # Completeness checks
            ValidationRule("basic_info_complete", "Basic vendor information should be complete", "warning", 0.7),
            ValidationRule("contact_info_present", "Should have some contact information", "info", 0.2),
        ]

    def _load_known_domains(self) -> Set[str]:
        """Load known legitimate domains for validation."""

        # Common SaaS domains - in real implementation, load from external source
        return {
            'salesforce.com', 'hubspot.com', 'slack.com', 'zoom.us',
            'microsoft.com', 'google.com', 'amazon.com', 'oracle.com',
            'sap.com', 'workday.com', 'servicenow.com', 'atlassian.com',
            'dropbox.com', 'box.com', 'docusign.com', 'adobe.com',
            'zendesk.com', 'intercom.com', 'mailchimp.com', 'stripe.com'
        }

    def _load_pricing_ranges(self) -> Dict[str, Tuple[float, float]]:
        """Load expected pricing ranges by category."""

        return {
            'crm': (5.0, 300.0),
            'hr': (3.0, 50.0),
            'analytics': (10.0, 500.0),
            'security': (2.0, 100.0),
            'marketing': (5.0, 200.0),
            'project-management': (5.0, 100.0),
            'collaboration': (3.0, 50.0),
            'accounting': (10.0, 150.0),
            'default': (1.0, 1000.0)
        }

    def validate_vendor_data(self, vendor_data: VendorData) -> QualityReport:
        """Perform comprehensive validation of vendor data."""

        report = QualityReport(
            vendor_name=vendor_data.name or "Unknown",
            overall_score=0.0,
            grade="F"
        )

        # Run all validation rules
        total_weight = 0.0
        total_score = 0.0

        for rule in self.validation_rules:
            result = self._validate_rule(rule, vendor_data)
            report.validation_results.append(result)

            # Categorize results
            if not result.passed:
                if result.rule.severity == "error":
                    report.errors.append(result.message)
                elif result.rule.severity == "warning":
                    report.warnings.append(result.message)

            # Calculate weighted score
            total_weight += rule.weight
            if result.passed:
                total_score += rule.weight
            else:
                total_score += rule.weight * (1.0 - result.score_impact)

        # Calculate overall score
        report.overall_score = (total_score / total_weight) * 100 if total_weight > 0 else 0

        # Calculate component scores
        report.completeness_score = self._calculate_completeness_score(vendor_data)
        report.accuracy_score = self._calculate_accuracy_score(vendor_data)
        report.freshness_score = self._calculate_freshness_score(vendor_data)
        report.consistency_score = self._calculate_consistency_score(vendor_data)

        # Assign grade
        report.grade = self._assign_grade(report.overall_score)

        # Generate recommendations
        report.recommendations = self._generate_recommendations(report, vendor_data)

        return report

    def _validate_rule(self, rule: ValidationRule, vendor_data: VendorData) -> ValidationResult:
        """Validate a single rule against vendor data."""

        if rule.name == "vendor_name_present":
            passed = bool(vendor_data.name and vendor_data.name.strip())
            message = "Vendor name is present" if passed else "Vendor name is missing"
            return ValidationResult(rule, passed, message, 0.0 if passed else 1.0)

        elif rule.name == "vendor_name_length":
            if not vendor_data.name:
                return ValidationResult(rule, False, "No vendor name to check length", 0.5)

            length = len(vendor_data.name.strip())
            passed = 2 <= length <= 100
            message = f"Vendor name length is {length} characters" if passed else f"Vendor name length ({length}) is outside reasonable range (2-100)"
            return ValidationResult(rule, passed, message, 0.0 if passed else 0.3)

        elif rule.name == "website_format":
            if not vendor_data.website:
                return ValidationResult(rule, False, "No website URL provided", 0.8)

            try:
                parsed = urlparse(vendor_data.website)
                passed = bool(parsed.scheme and parsed.netloc)
                message = "Website URL is properly formatted" if passed else "Website URL format is invalid"
                return ValidationResult(rule, passed, message, 0.0 if passed else 0.8)
            except Exception:
                return ValidationResult(rule, False, "Website URL parsing failed", 0.8)

        elif rule.name == "website_accessible":
            if not vendor_data.website:
                return ValidationResult(rule, True, "No website to check accessibility", 0.0)  # Skip if no website

            # In a real implementation, you'd make a HEAD request to check accessibility
            # For now, check if it's a known domain
            try:
                domain = urlparse(vendor_data.website).netloc.lower()
                domain = domain.replace('www.', '')
                passed = domain in self.known_domains or self._is_likely_valid_domain(domain)
                message = "Website appears accessible" if passed else "Website accessibility could not be verified"
                return ValidationResult(rule, passed, message, 0.0 if passed else 0.3)
            except Exception:
                return ValidationResult(rule, False, "Could not check website accessibility", 0.3)

        elif rule.name == "pricing_range":
            if not vendor_data.starting_price:
                return ValidationResult(rule, True, "No pricing to validate", 0.0)  # Skip if no pricing

            category = vendor_data.category or "default"
            category_key = category.lower().replace(' ', '-')
            min_price, max_price = self.pricing_ranges.get(category_key, self.pricing_ranges['default'])

            passed = min_price <= vendor_data.starting_price <= max_price
            message = f"Pricing ${vendor_data.starting_price} is within expected range" if passed else f"Pricing ${vendor_data.starting_price} is outside expected range (${min_price}-${max_price})"
            return ValidationResult(rule, passed, message, 0.0 if passed else 0.4)

        elif rule.name == "pricing_consistency":
            if not vendor_data.price_tiers:
                return ValidationResult(rule, True, "No price tiers to validate", 0.0)

            # Check if price tiers are in ascending order
            prices = list(vendor_data.price_tiers.values())
            if len(prices) < 2:
                return ValidationResult(rule, True, "Insufficient price tiers to check consistency", 0.0)

            passed = all(prices[i] <= prices[i+1] for i in range(len(prices)-1))
            message = "Price tiers are consistent" if passed else "Price tiers are not in ascending order"
            return ValidationResult(rule, passed, message, 0.0 if passed else 0.4)

        elif rule.name == "features_present":
            passed = bool(vendor_data.features and len(vendor_data.features) > 0)
            message = f"Vendor has {len(vendor_data.features)} features listed" if passed else "No features listed"
            return ValidationResult(rule, passed, message, 0.0 if passed else 0.3)

        elif rule.name == "features_duplicates":
            if not vendor_data.features:
                return ValidationResult(rule, True, "No features to check for duplicates", 0.0)

            unique_features = set(vendor_data.features)
            passed = len(unique_features) == len(vendor_data.features)
            duplicates = len(vendor_data.features) - len(unique_features)
            message = "No duplicate features found" if passed else f"Found {duplicates} duplicate features"
            return ValidationResult(rule, passed, message, 0.0 if passed else 0.1)

        elif rule.name == "data_freshness":
            if not vendor_data.scraped_at:
                return ValidationResult(rule, False, "No scraping timestamp available", 0.1)

            try:
                scraped_time = datetime.fromisoformat(vendor_data.scraped_at.replace('Z', '+00:00'))
                hours_old = (datetime.now() - scraped_time.replace(tzinfo=None)).total_seconds() / 3600
                passed = hours_old <= 48  # Within 48 hours
                message = f"Data is {hours_old:.1f} hours old" if passed else f"Data is {hours_old:.1f} hours old (stale)"
                return ValidationResult(rule, passed, message, 0.0 if passed else 0.1)
            except Exception:
                return ValidationResult(rule, False, "Could not parse scraping timestamp", 0.1)

        elif rule.name == "basic_info_complete":
            required_fields = [vendor_data.name, vendor_data.website, vendor_data.description]
            present_fields = sum(1 for field in required_fields if field and field.strip())
            passed = present_fields >= 2  # At least 2 of 3 required fields
            message = f"Basic info completeness: {present_fields}/3 fields present" if passed else f"Basic info incomplete: only {present_fields}/3 fields present"
            return ValidationResult(rule, passed, message, 0.0 if passed else 0.7)

        # Default case for unimplemented rules
        return ValidationResult(rule, True, f"Rule '{rule.name}' not implemented", 0.0)

    def _is_likely_valid_domain(self, domain: str) -> bool:
        """Check if a domain looks legitimate."""

        # Basic domain validation
        domain_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.[a-zA-Z]{2,}$'
        if not re.match(domain_pattern, domain):
            return False

        # Check for suspicious patterns
        suspicious_patterns = [
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',  # IP addresses
            r'localhost',
            r'\.local$',
            r'test\.',
            r'\.test$',
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, domain):
                return False

        return True

    def _calculate_completeness_score(self, vendor_data: VendorData) -> float:
        """Calculate data completeness score."""

        fields_to_check = [
            ('name', 1.0),
            ('website', 0.8),
            ('description', 0.6),
            ('category', 0.4),
            ('starting_price', 0.5),
            ('features', 0.7),
            ('certifications', 0.3),
            ('support_channels', 0.2),
        ]

        total_weight = sum(weight for _, weight in fields_to_check)
        total_score = 0.0

        for field_name, weight in fields_to_check:
            field_value = getattr(vendor_data, field_name, None)
            if field_value:
                if isinstance(field_value, (list, dict)):
                    if len(field_value) > 0:
                        total_score += weight
                elif isinstance(field_value, str) and field_value.strip():
                    total_score += weight
                elif isinstance(field_value, (int, float)) and field_value > 0:
                    total_score += weight

        return (total_score / total_weight) * 100

    def _calculate_accuracy_score(self, vendor_data: VendorData) -> float:
        """Calculate data accuracy score based on validation rules."""

        accuracy_rules = [rule for rule in self.validation_rules if rule.severity == "error"]
        if not accuracy_rules:
            return 100.0

        passed_rules = 0
        for rule in accuracy_rules:
            result = self._validate_rule(rule, vendor_data)
            if result.passed:
                passed_rules += 1

        return (passed_rules / len(accuracy_rules)) * 100

    def _calculate_freshness_score(self, vendor_data: VendorData) -> float:
        """Calculate data freshness score."""

        if not vendor_data.scraped_at:
            return 0.0

        try:
            scraped_time = datetime.fromisoformat(vendor_data.scraped_at.replace('Z', '+00:00'))
            hours_old = (datetime.now() - scraped_time.replace(tzinfo=None)).total_seconds() / 3600

            if hours_old <= 1:
                return 100.0
            elif hours_old <= 24:
                return 90.0
            elif hours_old <= 72:
                return 75.0
            elif hours_old <= 168:  # 1 week
                return 50.0
            else:
                return 25.0
        except Exception:
            return 0.0

    def _calculate_consistency_score(self, vendor_data: VendorData) -> float:
        """Calculate internal consistency score."""

        consistency_checks = []

        # Check pricing consistency
        if vendor_data.starting_price and vendor_data.price_tiers:
            min_tier_price = min(vendor_data.price_tiers.values()) if vendor_data.price_tiers else float('inf')
            consistency_checks.append(vendor_data.starting_price <= min_tier_price)

        # Check category-feature consistency
        if vendor_data.category and vendor_data.features:
            category_keywords = vendor_data.category.lower().split()
            feature_text = ' '.join(vendor_data.features).lower()
            keyword_matches = sum(1 for keyword in category_keywords if keyword in feature_text)
            consistency_checks.append(keyword_matches > 0)

        # Check certification-compliance consistency
        if vendor_data.certifications and vendor_data.compliance_frameworks:
            security_certs = any('soc' in cert.lower() or 'iso' in cert.lower() for cert in vendor_data.certifications)
            security_compliance = any('gdpr' in comp.lower() or 'ccpa' in comp.lower() for comp in vendor_data.compliance_frameworks)
            if security_certs or security_compliance:
                consistency_checks.append(True)  # At least some security focus

        if not consistency_checks:
            return 100.0  # No consistency issues found

        return (sum(consistency_checks) / len(consistency_checks)) * 100

    def _assign_grade(self, score: float) -> str:
        """Assign letter grade based on overall score."""

        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def _generate_recommendations(self, report: QualityReport, vendor_data: VendorData) -> List[str]:
        """Generate actionable recommendations for improving data quality."""

        recommendations = []

        # Based on errors
        if report.errors:
            recommendations.append(f"Fix {len(report.errors)} critical errors to improve data reliability")

        # Based on completeness
        if report.completeness_score < 70:
            recommendations.append("Improve data completeness by filling in missing vendor information")

        # Based on specific missing data
        if not vendor_data.description:
            recommendations.append("Add vendor description for better understanding")

        if not vendor_data.features:
            recommendations.append("Add feature list to help with vendor matching")

        if not vendor_data.starting_price:
            recommendations.append("Add pricing information for cost analysis")

        if not vendor_data.certifications and not vendor_data.compliance_frameworks:
            recommendations.append("Add compliance/certification information for enterprise buyers")

        # Based on freshness
        if report.freshness_score < 50:
            recommendations.append("Update vendor data - current information may be stale")

        return recommendations


def validate_vendor_batch(vendors: List[VendorData], validator: VendorDataValidator) -> Dict[str, QualityReport]:
    """Validate a batch of vendors and return quality reports."""

    reports = {}

    for vendor in vendors:
        try:
            report = validator.validate_vendor_data(vendor)
            reports[vendor.name] = report
        except Exception as e:
            print(f"Failed to validate {vendor.name}: {e}")

    return reports


def filter_high_quality_vendors(vendors: List[VendorData], min_score: float = 70.0) -> List[VendorData]:
    """Filter vendors based on minimum quality score."""

    validator = VendorDataValidator()
    high_quality_vendors = []

    for vendor in vendors:
        try:
            report = validator.validate_vendor_data(vendor)
            if report.overall_score >= min_score:
                high_quality_vendors.append(vendor)
        except Exception as e:
            print(f"Failed to validate {vendor.name}: {e}")

    return high_quality_vendors


# Example usage
if __name__ == "__main__":
    from .g2_scraper import G2Scraper

    # Get some vendors
    scraper = G2Scraper()
    vendors = scraper.scrape_vendor_directory("crm", limit=3)

    # Validate data quality
    validator = VendorDataValidator()

    for vendor in vendors:
        report = validator.validate_vendor_data(vendor)
        print(f"\n--- {vendor.name} ---")
        print(f"Overall Score: {report.overall_score:.1f} (Grade: {report.grade})")
        print(f"Completeness: {report.completeness_score:.1f}")
        print(f"Accuracy: {report.accuracy_score:.1f}")
        print(f"Freshness: {report.freshness_score:.1f}")
        print(f"Consistency: {report.consistency_score:.1f}")

        if report.errors:
            print(f"Errors: {len(report.errors)}")
        if report.warnings:
            print(f"Warnings: {len(report.warnings)}")
        if report.recommendations:
            print("Recommendations:")
            for rec in report.recommendations[:3]:  # Show top 3
                print(f"  - {rec}")