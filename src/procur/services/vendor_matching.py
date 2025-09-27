"""Enhanced vendor matching with category gating and feature synonyms."""

from typing import Dict, List, Set
from dataclasses import dataclass

# Category mapping - normalize categories and their synonyms
ALLOWED_CATEGORIES = {
    "crm": {"saas/crm", "crm", "customer-relationship-management", "sales"},
    "hr": {"saas/hr", "hr", "human-resources", "payroll", "benefits"},
    "security": {"saas/security", "security", "cybersecurity", "infosec"},
    "analytics": {"saas/analytics", "analytics", "business-intelligence", "bi"},
    "erp": {"saas/erp", "erp", "enterprise-resource-planning", "finance"},
}

# Feature synonyms for better matching
FEATURE_SYNONYMS = {
    "lead management": {"leads", "lead_routing", "prospecting", "lead_capture"},
    "contact management": {"contacts", "address_book", "customer_data", "crm"},
    "pipeline tracking": {"pipeline", "opportunity", "stages", "deal_tracking", "sales_pipeline"},
    "email integration": {"email", "gmail", "outlook", "imap", "smtp", "email_sync"},
    "api": {"api", "rest_api", "webhook", "integration", "developer_tools"},
    "mobile": {"mobile", "ios", "android", "mobile_app"},
    "analytics": {"analytics", "reporting", "dashboard", "insights", "metrics"},
    "sso": {"sso", "saml", "single_sign_on", "active_directory", "oauth"},
    "automation": {"automation", "workflow", "triggers", "rules"},
    "compliance": {"compliance", "audit", "gdpr", "hipaa", "soc2"},
}

@dataclass
class MatchResult:
    """Result of feature/category matching."""
    category_match: bool
    feature_score: float
    feature_hits: int
    total_features: int
    missing_features: List[str]
    compliance_score: float

    @property
    def is_viable(self) -> bool:
        """Check if vendor is viable (category match + reasonable feature score)."""
        return self.category_match and self.feature_score >= 0.6


class VendorMatcher:
    """Enhanced vendor matching with category gating and feature synonyms."""

    def __init__(self):
        self.category_map = ALLOWED_CATEGORIES
        self.feature_synonyms = FEATURE_SYNONYMS

    def normalize_category(self, category: str) -> str:
        """Normalize category string."""
        return category.strip().lower().replace(" ", "-")

    def category_matches(self, request_category: str, vendor_category: str) -> bool:
        """Check if vendor category matches request category using synonyms."""
        norm_request = self.normalize_category(request_category)
        norm_vendor = self.normalize_category(vendor_category)

        # Direct match
        if norm_request == norm_vendor:
            return True

        # Synonym match
        for category_group, synonyms in self.category_map.items():
            if norm_request in synonyms and norm_vendor in synonyms:
                return True

        return False

    def infer_category_from_features(self, features: List[str]) -> str:
        """Infer category from must-have features."""
        norm_features = {f.lower().replace(" ", "_") for f in features}

        crm_indicators = {"lead_management", "contact_management", "pipeline_tracking", "crm", "sales"}
        hr_indicators = {"payroll", "benefits", "hr", "human_resources"}
        security_indicators = {"security", "cybersecurity", "firewall", "antivirus"}

        if norm_features & crm_indicators:
            return "crm"
        elif norm_features & hr_indicators:
            return "hr"
        elif norm_features & security_indicators:
            return "security"
        else:
            return "saas"  # generic fallback

    def feature_match_score(self, requested_features: List[str], vendor_features: List[str]) -> tuple[float, int, List[str]]:
        """Calculate feature match score with synonyms."""
        if not requested_features:
            return 1.0, 0, []

        norm_vendor = {f.lower().replace(" ", "_") for f in vendor_features}
        hits = 0
        missing = []

        for req_feature in requested_features:
            req_norm = req_feature.lower().replace(" ", "_")

            # Get synonyms for this feature
            synonyms = self.feature_synonyms.get(req_feature.lower(), {req_norm})

            # Check if any synonym matches
            if any(syn in norm_vendor for syn in synonyms):
                hits += 1
            else:
                missing.append(req_feature)

        score = hits / len(requested_features)
        return score, hits, missing

    def compliance_match_score(self, requested_compliance: List[str], vendor_compliance: List[str]) -> float:
        """Calculate compliance match score."""
        if not requested_compliance:
            return 1.0

        norm_requested = {c.lower() for c in requested_compliance}
        norm_vendor = {c.lower() for c in vendor_compliance}

        matches = len(norm_requested & norm_vendor)
        return matches / len(norm_requested)

    def evaluate_vendor(self, request, vendor_record) -> MatchResult:
        """Evaluate if vendor matches request requirements."""
        # Infer request category from features if not explicit
        request_category = getattr(request, 'category', None)
        if not request_category:
            request_category = self.infer_category_from_features(request.must_haves)

        # Check category match
        category_match = self.category_matches(request_category, vendor_record.category)

        # Get requested features
        requested_features = request.specs.get("features", request.must_haves)

        # Calculate feature score
        feature_score, feature_hits, missing_features = self.feature_match_score(
            requested_features, vendor_record.features
        )

        # Calculate compliance score
        compliance_score = self.compliance_match_score(
            request.compliance_requirements, vendor_record.compliance
        )

        return MatchResult(
            category_match=category_match,
            feature_score=feature_score,
            feature_hits=feature_hits,
            total_features=len(requested_features),
            missing_features=missing_features,
            compliance_score=compliance_score
        )