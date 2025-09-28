from __future__ import annotations

import json
import logging
from typing import Dict, List, Optional

import httpx

from ..models import Offer

logger = logging.getLogger(__name__)


class SlackIntegration:
    """Send negotiation updates to Slack channels or users."""

    def __init__(
        self,
        *,
        webhook_url: Optional[str] = None,
        bot_token: Optional[str] = None,
        default_channel: Optional[str] = None,
        timeout: float = 10.0,
    ) -> None:
        self.webhook_url = webhook_url
        self.bot_token = bot_token
        self.default_channel = default_channel or "#procurement"
        self._client = httpx.Client(timeout=timeout)

    def send_approval_request(self, offer: Offer, stakeholders: List[str]) -> None:
        message = self._build_offer_message(
            title="Approval requested",
            offer=offer,
            stakeholders=stakeholders,
        )
        self._dispatch(message)

    def notify_negotiation_complete(self, offer: Offer) -> None:
        message = self._build_offer_message(
            title="Negotiation complete",
            offer=offer,
            stakeholders=[],
        )
        self._dispatch(message)

    def _dispatch(self, payload: Dict[str, object]) -> None:
        if self.webhook_url:
            self._post_webhook(payload)
        elif self.bot_token:
            self._post_chat_api(payload)
        else:
            logger.info("Slack message not sent (no credentials): %s", json.dumps(payload))

    def _post_webhook(self, payload: Dict[str, object]) -> None:
        try:
            response = self._client.post(self.webhook_url, json=payload)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Slack webhook failed: %s", exc)

    def _post_chat_api(self, payload: Dict[str, object]) -> None:
        message = {
            "channel": payload.get("channel", self.default_channel),
            "text": payload.get("text"),
            "blocks": payload.get("blocks"),
        }
        try:
            response = self._client.post(
                "https://slack.com/api/chat.postMessage",
                headers={"Authorization": f"Bearer {self.bot_token}"},
                json=message,
            )
            response.raise_for_status()
            if not response.json().get("ok", False):
                logger.warning("Slack API error: %s", response.text)
        except httpx.HTTPError as exc:
            logger.warning("Slack API request failed: %s", exc)

    def _build_offer_message(
        self,
        *,
        title: str,
        offer: Offer,
        stakeholders: List[str],
    ) -> Dict[str, object]:
        stakeholders_text = ", ".join(stakeholders) if stakeholders else "Team"
        offer_components = offer.components
        text = (
            f"{title} with {offer.vendor_id} for {offer_components.quantity} seats at "
            f"${offer_components.unit_price:,.2f} per {offer_components.term_months}-month term"
        )
        blocks = [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*{title}*\n{stakeholders_text}: {text}"},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Payment Terms:* {offer_components.payment_terms.value}"},
                    {"type": "mrkdwn", "text": f"*Accepted:* {offer.accepted}"},
                ],
            },
        ]
        return {"text": text, "blocks": blocks, "channel": self.default_channel}


class DocuSignIntegration:
    """Minimal DocuSign integration for sending contracts to signers."""

    def __init__(
        self,
        *,
        api_base: Optional[str] = None,
        integration_key: Optional[str] = None,
        auth_token: Optional[str] = None,
        timeout: float = 10.0,
    ) -> None:
        self.api_base = api_base or "https://demo.docusign.net/restapi"
        self.integration_key = integration_key
        self.auth_token = auth_token
        self._client = httpx.Client(timeout=timeout)

    def send_for_signature(self, contract: bytes, signers: List[str]) -> str:
        if not self.integration_key or not self.auth_token:
            logger.info("DocuSign integration disabled; returning mock envelope id")
            return "mock-envelope-id"

        payload = {
            "emailSubject": "Please sign the Procur agreement",
            "documents": [
                {
                    "documentBase64": contract.decode("utf-8") if self._looks_like_html(contract) else contract.decode("latin-1", "ignore"),
                    "name": "Procur-Agreement.pdf",
                    "fileExtension": "pdf",
                    "documentId": "1",
                }
            ],
            "recipients": {
                "signers": [
                    {
                        "email": signer,
                        "name": signer.split("@")[0].title(),
                        "recipientId": str(idx + 1),
                    }
                    for idx, signer in enumerate(signers)
                ]
            },
            "status": "sent",
        }
        try:
            response = self._client.post(
                f"{self.api_base}/v2.1/accounts/{self.integration_key}/envelopes",
                headers={"Authorization": f"Bearer {self.auth_token}"},
                json=payload,
            )
            response.raise_for_status()
            return response.json().get("envelopeId", "unknown-envelope")
        except httpx.HTTPError as exc:
            logger.warning("DocuSign request failed: %s", exc)
            return "error-envelope"

    @staticmethod
    def _looks_like_html(content: bytes) -> bool:
        prefix = content[:64].lower()
        return prefix.strip().startswith(b"<!doctype") or prefix.strip().startswith(b"<html")


class ERPIntegration:
    """Create purchase orders in an ERP system."""

    def __init__(
        self,
        *,
        api_base: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 10.0,
    ) -> None:
        self.api_base = api_base
        self.api_key = api_key
        self._client = httpx.Client(timeout=timeout)

    def create_purchase_order(self, offer: Offer) -> str:
        if not self.api_base or not self.api_key:
            logger.info("ERP integration disabled; returning mock PO id")
            return "PO-MOCK-0001"

        payload = {
            "vendorId": offer.vendor_id,
            "items": [
                {
                    "description": f"{offer.components.quantity} seats",
                    "unitPrice": offer.components.unit_price,
                    "quantity": offer.components.quantity,
                    "termMonths": offer.components.term_months,
                }
            ],
            "currency": offer.components.currency,
            "paymentTerms": offer.components.payment_terms.value,
        }
        try:
            response = self._client.post(
                f"{self.api_base}/purchase-orders",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
            )
            response.raise_for_status()
            return response.json().get("id", "PO-UNKNOWN")
        except httpx.HTTPError as exc:
            logger.warning("ERP request failed: %s", exc)
            return "PO-ERROR"


__all__ = ["SlackIntegration", "DocuSignIntegration", "ERPIntegration"]
