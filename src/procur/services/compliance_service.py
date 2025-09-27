from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from ..models import ControlStatus, Request, RiskCard, RiskLevel, VendorProfile


@dataclass
class ComplianceFinding:
    code: str
    message: str
    blocking: bool = True


class ComplianceService:
    """Gates compliance requirements and manages exception workflow."""

    def __init__(self, mandatory_certifications: List[str] | None = None) -> None:
        self.mandatory_certifications = mandatory_certifications or []

    def _missing_tags(self, vendor: VendorProfile, tags: Iterable[str]) -> List[str]:
        missing: List[str] = []
        vendor_tags = {tag.lower() for tag in vendor.capability_tags}
        vendor_certs = {cert.lower() for cert in vendor.certifications}
        for tag in tags:
            normalized = tag.lower()
            if normalized not in vendor_tags and normalized not in vendor_certs:
                missing.append(tag)
        return missing

    def evaluate_vendor(self, request: Request, vendor: VendorProfile) -> List[ComplianceFinding]:
        findings: List[ComplianceFinding] = []

        for cert in self.mandatory_certifications:
            if cert not in vendor.certifications:
                findings.append(
                    ComplianceFinding(
                        code="missing_certification",
                        message=f"Vendor missing required certification {cert}",
                    )
                )

        must_have_missing = set(self._missing_tags(vendor, request.must_haves))
        for tag in must_have_missing:
            findings.append(
                ComplianceFinding(
                    code="missing_must_have",
                    message=f"Vendor lacks required capability or certification '{tag}'",
                )
            )

        residency = request.specs.get("data_residency")
        if residency and residency not in vendor.regions:
            findings.append(
                ComplianceFinding(
                    code="data_residency_mismatch",
                    message=f"Residency requirement {residency} not met by vendor regions {vendor.regions}",
                )
            )

        sensitivity = (request.data_sensitivity or "").lower()
        if sensitivity in {"restricted", "high"} and vendor.risk_level != RiskLevel.LOW:
            findings.append(
                ComplianceFinding(
                    code="risk_too_high",
                    message=f"Vendor risk level {vendor.risk_level.value} incompatible with {sensitivity} data",
                )
            )

        required_value_adds = request.specs.get("value_add_requirements", [])
        missing_value_adds = self._missing_tags(vendor, required_value_adds)
        for value_add in missing_value_adds:
            findings.append(
                ComplianceFinding(
                    code="value_add_missing",
                    message=f"Vendor cannot satisfy required value-add '{value_add}'",
                    blocking=False,
                )
            )

        return findings

    def build_risk_card(self, request: Request, vendor: VendorProfile) -> RiskCard:
        findings = self.evaluate_vendor(request, vendor)
        must_have_missing = set(self._missing_tags(vendor, request.must_haves))
        controls = [
            ControlStatus(
                name=cert,
                compliant=cert in vendor.certifications,
            )
            for cert in self.mandatory_certifications
        ]
        controls.extend(
            ControlStatus(name=tag, compliant=tag not in must_have_missing)
            for tag in request.must_haves
        )
        blocking_messages = [finding.message for finding in findings if finding.blocking]
        non_blocking = [finding.message for finding in findings if not finding.blocking]
        return RiskCard(
            request_id=request.request_id,
            vendor_id=vendor.vendor_id,
            controls=controls,
            exceptions=non_blocking,
            breach_flags=blocking_messages,
        )
