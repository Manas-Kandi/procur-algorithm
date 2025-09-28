from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

try:  # pragma: no cover - optional dependency
    from jinja2 import Template  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    Template = None  # type: ignore[assignment]

from ..models import Offer, Request

try:  # pragma: no cover - optional dependency
    import pdfkit  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    pdfkit = None


class ContractGenerationError(RuntimeError):
    """Raised when a contract cannot be generated."""


@dataclass(slots=True)
class ContractGenerator:
    """Generate deal-ready contract artefacts from offers and buyer context."""

    template_path: Optional[Path] = None
    template_variables: Optional[Dict[str, object]] = None

    def generate_contract(self, offer: Offer, request: Request) -> bytes:
        """Render a PDF contract for the negotiated offer."""
        components = offer.components
        context = {
            "vendor_name": offer.vendor_id,
            "customer_name": request.requester_id,
            "price": components.unit_price,
            "billing_cycle": request.billing_cadence or "annual",
            "term_months": components.term_months,
            "payment_terms": components.payment_terms.value,
            "sla_terms": components.warranty_support.get("sla", "Standard enterprise SLA"),
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "quantity": components.quantity,
            "currency": components.currency,
            "request_id": request.request_id,
            "notes": components.notes or "",
        }
        if self.template_variables:
            context.update(self.template_variables)

        html = self._render_html(context)
        return self._render_pdf(html)

    def _render_html(self, context: Dict[str, object]) -> str:
        if Template is not None:
            template = self._load_template()
            return template.render(**context)
        if self.template_path:
            raise ContractGenerationError(
                "Custom contract templates require the 'jinja2' package to be installed"
            )
        return self._basic_html(context)

    def _load_template(self) -> Template:
        if Template is None:  # pragma: no cover - guarded by caller
            raise ContractGenerationError("jinja2 is not installed")
        if self.template_path:
            template_text = self.template_path.read_text(encoding="utf-8")
        else:
            template_text = self._default_template()
        return Template(template_text)

    def _render_pdf(self, html: str) -> bytes:
        if pdfkit is None:
            # Fallback to returning HTML bytes so the caller can handle conversion externally
            return html.encode("utf-8")
        try:
            return pdfkit.from_string(html, False)
        except Exception as exc:  # pragma: no cover - pdfkit internal errors
            raise ContractGenerationError("Failed to render contract PDF") from exc

    def _basic_html(self, context: Dict[str, object]) -> str:
        return (
            "<!DOCTYPE html><html lang=\"en\">"
            "<head><meta charset=\"utf-8\" /><title>Software License Agreement</title></head>"
            "<body>"
            f"<h1>Software License Agreement</h1>"
            f"<p><strong>Vendor:</strong> {context.get('vendor_name')}</p>"
            f"<p><strong>Customer:</strong> {context.get('customer_name')}</p>"
            f"<p><strong>Agreement Date:</strong> {context.get('date')}</p>"
            "<hr />"
            f"<p><strong>Price:</strong> ${context.get('price', 0):,.2f} per {context.get('billing_cycle')}</p>"
            f"<p><strong>Term:</strong> {context.get('term_months')} months</p>"
            f"<p><strong>Quantity:</strong> {context.get('quantity')}</p>"
            f"<p><strong>Currency:</strong> {context.get('currency')}</p>"
            f"<p><strong>Payment Terms:</strong> {context.get('payment_terms')}</p>"
            f"<p><strong>SLA:</strong> {context.get('sla_terms')}</p>"
            f"<p>This agreement was generated for request {context.get('request_id')}.</p>"
            f"<p>{context.get('notes', '')}</p>"
            "</body></html>"
        )

    @staticmethod
    def _default_template() -> str:
        return (
            """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="utf-8" />
                <title>Software License Agreement</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 1.5rem; line-height: 1.6; }
                    h1 { text-transform: uppercase; letter-spacing: 0.1em; }
                    section { margin-bottom: 1.25rem; }
                    .summary { background: #f5f7fa; padding: 1rem; border-radius: 6px; }
                    table { width: 100%; border-collapse: collapse; }
                    td { padding: 0.35rem 0; }
                    strong { font-weight: 600; }
                </style>
            </head>
            <body>
                <h1>Software License Agreement</h1>
                <section class="summary">
                    <p><strong>Vendor:</strong> {{ vendor_name }}</p>
                    <p><strong>Customer:</strong> {{ customer_name }}</p>
                    <p><strong>Agreement Date:</strong> {{ date }}</p>
                </section>
                <section>
                    <table>
                        <tr><td><strong>Price</strong></td><td>${{ "%.2f" % price }} per {{ billing_cycle }}</td></tr>
                        <tr><td><strong>Term</strong></td><td>{{ term_months }} months</td></tr>
                        <tr><td><strong>Quantity</strong></td><td>{{ quantity }}</td></tr>
                        <tr><td><strong>Currency</strong></td><td>{{ currency }}</td></tr>
                        <tr><td><strong>Payment Terms</strong></td><td>{{ payment_terms }}</td></tr>
                        <tr><td><strong>SLA</strong></td><td>{{ sla_terms }}</td></tr>
                    </table>
                </section>
                <section>
                    <p>This agreement was generated by Procur AI for request {{ request_id }}. Any negotiated notes:</p>
                    <p>{{ notes }}</p>
                </section>
            </body>
            </html>
            """
        )


__all__ = ["ContractGenerator", "ContractGenerationError"]
