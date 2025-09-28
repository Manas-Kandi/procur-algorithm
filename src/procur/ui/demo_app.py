from __future__ import annotations

import base64
from pathlib import Path
from typing import Optional

import streamlit as st

from ..config import ProcurementConfig
from ..orchestration.pipeline import SaaSProcurementPipeline


DEFAULT_SEED_PATH = Path(__file__).resolve().parents[2] / "assets" / "seeds.json"


@st.cache_resource(show_spinner=False)
def _build_pipeline(config_path: Optional[str], seed_path: Optional[str]) -> SaaSProcurementPipeline:
    config = ProcurementConfig.from_yaml(config_path) if config_path else ProcurementConfig()
    seeds = Path(seed_path).expanduser() if seed_path else config.seed_path
    return SaaSProcurementPipeline(seeds_path=seeds, config=config)


def _render_shortlist(shortlist):
    st.subheader("Recommended Vendors")
    if not shortlist:
        st.write("No vendors matched the criteria.")
        return
    for entry in shortlist:
        header = f"{entry['name']} (Score: {entry['score']:.2f})"
        with st.expander(header, expanded=False):
            for reason in entry.get("reasons", []):
                st.write(f"- {reason}")


def _render_negotiations(vendors, contracts):
    st.subheader("Negotiation Results")
    if not vendors:
        st.write("Negotiations have not produced any offers yet.")
        return
    for vendor in vendors:
        st.markdown(
            f"**{vendor['vendor_name']}** — ${vendor['final_price']:,.2f} / seat, term {vendor['term_months']} months"
        )
        compliance = vendor.get("compliance_status", [])
        if compliance:
            st.write("Compliance:")
            for item in compliance:
                st.write(f"• {item}")
        vendor_id = vendor.get("vendor_id")
        if vendor_id and vendor_id in contracts:
            contract_bytes = base64.b64decode(contracts[vendor_id])
            st.download_button(
                label=f"Download Contract ({vendor['vendor_name']})",
                data=contract_bytes,
                file_name=f"procur-{vendor_id}.pdf",
                mime="application/pdf",
                key=f"download-{vendor_id}",
            )


def _render_analytics(analytics):
    if not analytics:
        return
    st.subheader("Analytics Highlights")
    savings = analytics.get("savings", {})
    cols = st.columns(3)
    cols[0].metric("Total Savings", f"${savings.get('total_savings', 0):,.2f}")
    cols[1].metric("Avg Rounds", savings.get("avg_rounds", 0))
    cols[2].metric("Success Rate", f"{savings.get('success_rate', 0) * 100:.1f}%")

    if savings.get("top_strategies"):
        st.write("Top Strategies:")
        for strategy in savings["top_strategies"]:
            lever = strategy.get("lever", "unknown")
            count = strategy.get("count", 0)
            st.write(f"- {lever} ({count} uses)")

    compliance = analytics.get("compliance", {})
    if compliance:
        st.write("Compliance Coverage:")
        for name, payload in compliance.items():
            st.write(
                f"- {name}: {payload.get('coverage_pct', 0) * 100:.1f}% coverage "
                f"({payload.get('covered', 0)}/{payload.get('total', 0)})"
            )


def main() -> None:
    st.title("Procur: AI Procurement Assistant")

    with st.sidebar:
        st.header("Configuration")
        config_path = st.text_input("Config YAML", value="")
        seed_path = st.text_input("Seed Catalog", value=str(DEFAULT_SEED_PATH))
        policy_summary = st.text_area(
            "Company policy summary",
            value="Standard procurement policy with SOC2 requirement.",
            height=100,
        )

    request_text = st.text_area(
        "Describe what you need",
        placeholder="We need a CRM tool for 50 sales reps, budget around $50k/year",
        height=180,
    )

    if st.button("Find Solutions", type="primary"):
        if not request_text.strip():
            st.warning("Please describe your procurement need before running the pipeline.")
            return
        try:
            pipeline = _build_pipeline(config_path or None, seed_path or None)
        except Exception as exc:  # pragma: no cover - UI level feedback
            st.error(f"Failed to initialise pipeline: {exc}")
            return

        with st.spinner("Running procurement pipeline..."):
            try:
                results = pipeline.run(request_text, policy_summary)
            except Exception as exc:  # pragma: no cover - UI level feedback
                st.error(f"Pipeline execution failed: {exc}")
                return

        if notice := results.get("shortlist_notice"):
            st.info(notice.get("message", "Shortlist notice"))

        _render_shortlist(results.get("shortlist", []))
        _render_negotiations(results.get("vendors", []), results.get("contracts", {}))
        _render_analytics(results.get("analytics", {}))

        integrations = results.get("integrations", {})
        if integrations:
            st.subheader("Integration Events")
            st.json(integrations)


if __name__ == "__main__":
    main()
