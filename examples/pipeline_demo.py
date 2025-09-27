"""Demonstration of the SaaS procurement pipeline."""

from __future__ import annotations

import json
from pathlib import Path

from procur.orchestration import SaaSProcurementPipeline


def main() -> None:
    pipeline = SaaSProcurementPipeline(seeds_path=Path("assets/seeds.json"))

    raw_request = (
        "Need a CRM platform for 120 sales reps with analytics and mobile access. "
        "Budget around $135k annually. Must handle GDPR data and integrate with our SSO."
    )
    policy_summary = "Budget cap 140000 USD; risk threshold medium"

    result = pipeline.run(
        raw_text=raw_request,
        policy_summary=policy_summary,
        clarification_answers=None,
        top_n=5,
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
