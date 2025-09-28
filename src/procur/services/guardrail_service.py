from __future__ import annotations

from dataclasses import dataclass
from typing import List

from ..models import OfferComponents, PaymentTerms, VendorProfile


@dataclass
class GuardrailAlert:
    code: str
    message: str
    blocking: bool = True


class GuardrailService:
    """Detects anomalies, verifies counterparties, and enforces safety stops."""

    def __init__(self, price_outlier_threshold: float = 0.3, *, run_mode: str = "production") -> None:
        self.price_outlier_threshold = price_outlier_threshold
        self.run_mode = run_mode

    def verify_counterparty(self, vendor: VendorProfile) -> List[GuardrailAlert]:
        alerts: List[GuardrailAlert] = []
        if self.run_mode == "simulation":
            return alerts
        if "bank_account" not in vendor.contact_endpoints:
            alerts.append(
                GuardrailAlert(
                    code="missing_bank_verification",
                    message="Vendor bank verification pending",
                    blocking=False,
                )
            )
        return alerts

    def detect_price_outlier(
        self,
        vendor: VendorProfile,
        offer: OfferComponents,
    ) -> List[GuardrailAlert]:
        alerts: List[GuardrailAlert] = []
        tier_key = str(offer.quantity)
        historical = vendor.price_tiers.get(tier_key)
        if historical is None:
            return alerts
        deviation = abs(offer.unit_price - historical) / max(historical, 1.0)
        if deviation > self.price_outlier_threshold:
            alerts.append(
                GuardrailAlert(
                    code="price_outlier",
                    message=f"Offer price deviates {deviation:.2%} from tier {historical}",
                    blocking=False,
                )
            )
        return alerts

    def vet_offer(self, vendor: VendorProfile, offer: OfferComponents) -> List[GuardrailAlert]:
        alerts = self.verify_counterparty(vendor)
        alerts.extend(self.detect_price_outlier(vendor, offer))
        if offer.payment_terms == PaymentTerms.DEPOSIT and "deposit_policy" not in vendor.contact_endpoints:
            alerts.append(
                GuardrailAlert(
                    code="deposit_terms_unverified",
                    message="Deposit requested without verified deposit policy",
                )
            )
        return alerts
