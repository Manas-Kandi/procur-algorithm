"""Reference catalog for globally recognized SaaS compliance frameworks."""

from __future__ import annotations

from typing import Dict, List

ComplianceEntry = Dict[str, object]


COMPLIANCE_CATALOG: Dict[str, ComplianceEntry] = {
    "soc2": {
        "id": "soc2",
        "name": "SOC 2 Type II",
        "region": "global",
        "category": "security",
        "description": "Service Organization Control audit covering security, availability, processing integrity, confidentiality, and privacy.",
        "aliases": ["soc 2", "soc2 type ii"],
        "blocking": True,
    },
    "iso27001": {
        "id": "iso27001",
        "name": "ISO/IEC 27001",
        "region": "global",
        "category": "security",
        "description": "International standard for information security management systems.",
        "aliases": ["iso 27001", "iso-27001"],
        "blocking": True,
    },
    "gdpr": {
        "id": "gdpr",
        "name": "GDPR Alignment",
        "region": "eu",
        "category": "privacy",
        "description": "Controls for processing personal data of EU residents under the General Data Protection Regulation.",
        "aliases": ["general data protection regulation"],
        "blocking": True,
    },
    "hipaa": {
        "id": "hipaa",
        "name": "HIPAA",
        "region": "us",
        "category": "healthcare",
        "description": "Health Insurance Portability and Accountability Act safeguards for protected health information.",
        "aliases": ["hipaa compliant"],
        "blocking": True,
    },
    "fedramp": {
        "id": "fedramp",
        "name": "FedRAMP Moderate",
        "region": "us",
        "category": "government",
        "description": "US Federal Risk and Authorization Management Program authorization for cloud service providers.",
        "aliases": ["fedramp moderate", "fedramp"],
        "blocking": True,
    },
    "pci-dss": {
        "id": "pci-dss",
        "name": "PCI DSS",
        "region": "global",
        "category": "payments",
        "description": "Payment Card Industry Data Security Standard for handling cardholder data.",
        "aliases": ["pci", "pci dss"],
        "blocking": True,
    },
    "ccpa": {
        "id": "ccpa",
        "name": "CCPA/CPRA",
        "region": "us",
        "category": "privacy",
        "description": "California Consumer Privacy Act and Privacy Rights Act compliance commitments.",
        "aliases": ["ccpa", "cpra"],
        "blocking": False,
    },
}


def normalize_identifier(identifier: str) -> str:
    return identifier.strip().lower()


def lookup_compliance(requirement: str) -> ComplianceEntry | None:
    normalized = normalize_identifier(requirement)
    if normalized in COMPLIANCE_CATALOG:
        return COMPLIANCE_CATALOG[normalized]
    for entry in COMPLIANCE_CATALOG.values():
        aliases: List[str] = [entry["id"], *entry.get("aliases", [])]  # type: ignore
        if normalized in {alias.lower() for alias in aliases}:
            return entry
    return None


__all__ = ["COMPLIANCE_CATALOG", "lookup_compliance", "normalize_identifier"]
