from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Optional

from ..llm.client import LLMClient
from ..orchestration.pipeline import PipelineServices, SaaSProcurementPipeline
from ..services import (
    AuditTrailService,
    ComplianceService,
    ExplainabilityService,
    GuardrailService,
    MemoryService,
    NegotiationEngine,
    PolicyEngine,
    RetrievalService,
    ScoringService,
)
from ..services.scoring_service import ScoreWeights
from ..agents import BuyerAgent, BuyerAgentConfig
from .prompt_manager import PromptManager

# Get absolute path to seed catalog
# __file__ is in src/procur/cli/buyer_console.py
# Need to go up 4 levels: buyer_console.py -> cli -> procur -> src -> project_root
_project_root = Path(__file__).parent.parent.parent.parent
DEFAULT_SEED_PATH = _project_root / "assets" / "seeds.json"


def build_live_pipeline(seeds_path: Path = DEFAULT_SEED_PATH) -> SaaSProcurementPipeline:
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        raise RuntimeError("NVIDIA_API_KEY not found in environment; cannot run live pipeline")

    def factory():
        policy_engine = PolicyEngine()
        compliance_service = ComplianceService(mandatory_certifications=["soc2"])
        guardrail_service = GuardrailService()
        scoring_service = ScoringService(weights=ScoreWeights())
        negotiation_engine = NegotiationEngine(policy_engine, scoring_service)
        explainability_service = ExplainabilityService()
        audit_service = AuditTrailService()
        memory_service = MemoryService()
        retrieval_service = RetrievalService()

        llm_client = LLMClient(api_key=api_key)

        buyer_agent = BuyerAgent(
            policy_engine=policy_engine,
            compliance_service=compliance_service,
            guardrail_service=guardrail_service,
            scoring_service=scoring_service,
            negotiation_engine=negotiation_engine,
            explainability_service=explainability_service,
            llm_client=llm_client,
            config=BuyerAgentConfig(),
            audit_service=audit_service,
            memory_service=memory_service,
            retrieval_service=retrieval_service,
        )

        services = PipelineServices(
            audit_service=audit_service,
            memory_service=memory_service,
            retrieval_service=retrieval_service,
            compliance_service=compliance_service,
        )
        return buyer_agent, services

    return SaaSProcurementPipeline(seeds_path=seeds_path, buyer_agent_factory=factory)

def summarize_results(result: Dict[str, object]) -> None:
    print("\n=== Intake Summary ===")
    print(json.dumps(result["request"], indent=2))

    notice = result.get("shortlist_notice")
    if notice:
        print("\nShortlist note:")
        print(f"- {notice.get('message')}")
    if result["shortlist"]:
        print("\n=== Vendor Shortlist ===")
        for entry in result["shortlist"]:
            print(f"- {entry['name']} (score {entry['score']:.2f})")
            for reason in entry["reasons"]:
                print(f"    • {reason}")

    bundles = result.get("bundles") or {}
    if bundles:
        print("\n=== Recommended Bundles ===")
        print(json.dumps(bundles, indent=2))

    vendors = result.get("vendors") or []
    if vendors:
        print("\n=== Vendor Negotiations ===")
        for vendor in vendors:
            print(f"\nVendor: {vendor['vendor_name']} ({vendor['vendor_id']})")
            print(f"  Final price: ${vendor['final_price']:.2f}")
            print(f"  Term: {vendor['term_months']} months")
            print(f"  Payment terms: {vendor['payment_terms']}")
            print("  Compliance:")
            for item in vendor.get("compliance_status", []):
                print(f"    • {item}")
            transcript = vendor.get("memory_log", {}).get("rounds", [])
            if transcript:
                print("  Transcript:")
                for round_entry in transcript:
                    actor = round_entry.get("actor")
                    round_no = round_entry.get("round_number")
                    strategy = round_entry.get("strategy")
                    decision = round_entry.get("decision")
                    print(f"    - Round {round_no} ({actor}): strategy={strategy}, decision={decision}")
                    selected = round_entry.get("selected", {})
                    rationale = selected.get("rationale", [])
                    for line in rationale:
                        print(f"        · {line}")


def interactive_main() -> None:
    try:
        pipeline = build_live_pipeline()
        manager = PromptManager()
        print("Welcome to Procur CLI! Describe your procurement request below.\n")
        raw_text = manager.prompt("Describe your need: ")
        policy_summary = manager.prompt("Policy summary (enter to skip): ") or ""

        clarification_answers: Dict[str, str] = {}
        manager.status("Processing your request...")
        result = pipeline.run(raw_text, policy_summary, None)
        questions = result.get("clarification_questions", [])

        while questions:
            print("\nWe need a bit more detail:")
            for question in questions:
                value = manager.prompt(f"- {question['question']} ")
                clarification_answers[question["field"]] = value
            manager.status("Processing additional details...")
            result = pipeline.run(raw_text, policy_summary, clarification_answers)
            questions = result.get("clarification_questions", [])

        summarize_results(result)

        print("\nDone. You can review the JSON payload below if needed:\n")
        print(json.dumps(result, indent=2))

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        raise SystemExit(0)
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        print("Please check your network connection and API key configuration.")
        raise SystemExit(1)


if __name__ == "__main__":  # pragma: no cover - entry point
    interactive_main()
