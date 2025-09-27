from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from ..models import ControlStatus, Request, RiskCard, RiskLevel, VendorProfile
from .compliance_catalog import lookup_compliance, normalize_identifier


@dataclass
class ComplianceFinding:
    code: str
    message: str
    blocking: bool = True


@dataclass
class ComplianceStatus:
    requirement: str
    name: str
    status: str
    blocking: bool
    reason: str

    def summary(self) -> str:
        label = "BLOCKING" if self.blocking and self.status != "compliant" else "INFO"
        return f"[{label}] {self.name}: {self.status.upper()} — {self.reason}"


@dataclass
class ComplianceAssessment:
    statuses: List[ComplianceStatus]

    @property
    def blocking(self) -> bool:
        return any(status.blocking and status.status != "compliant" for status in self.statuses)

    @property
    def missing(self) -> List[str]:
        return [status.name for status in self.statuses if status.status != "compliant"]

    def summaries(self) -> List[str]:
        return [status.summary() for status in self.statuses]


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

    def assess_vendor(self, request: Request, vendor: VendorProfile) -> ComplianceAssessment:
        statuses: List[ComplianceStatus] = []
        vendor_certs = {normalize_identifier(cert) for cert in vendor.certifications}
        vendor_regions = {normalize_identifier(region) for region in vendor.regions}

        for requirement in request.compliance_requirements:
            entry = lookup_compliance(requirement)
            if entry:
                tokens = {normalize_identifier(entry["id"]) }
                tokens.update(normalize_identifier(alias) for alias in entry.get("aliases", []))
                name = entry["name"]  # type: ignore[index]
                blocking = bool(entry.get("blocking", True))
                region = entry.get("region")
            else:
                tokens = {normalize_identifier(requirement)}
                name = requirement.upper()
                blocking = True
                region = None

            compliant = bool(tokens & vendor_certs)
            if not compliant and region == "eu" and "eu" in vendor_regions:
                compliant = True
            if not compliant and region == "us" and "us" in vendor_regions:
                compliant = True

            if compliant:
                status = ComplianceStatus(
                    requirement=requirement,
                    name=name,
                    status="compliant",
                    blocking=blocking,
                    reason="Vendor attests requirement via certifications",
                )
            else:
                status = ComplianceStatus(
                    requirement=requirement,
                    name=name,
                    status="missing",
                    blocking=blocking,
                    reason=f"Vendor lacks documented {name} coverage",
                )
            statuses.append(status)

        return ComplianceAssessment(statuses=statuses)

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

        assessment = self.assess_vendor(request, vendor)
        for status in assessment.statuses:
            if status.status != "compliant":
                findings.append(
                    ComplianceFinding(
                        code="compliance_missing",
                        message=status.reason,
                        blocking=status.blocking,
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
        assessment = self.assess_vendor(request, vendor)
        controls.extend(
            ControlStatus(name=status.name, compliant=status.status == "compliant", notes=status.reason)
            for status in assessment.statuses
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

    def summarize_assessment(self, request: Request, vendor: VendorProfile) -> List[str]:
        return self.assess_vendor(request, vendor).summaries()
