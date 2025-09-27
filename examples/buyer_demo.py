"""Example wiring for the buyer agent using mock vendors."""

from procur.agents import BuyerAgent, BuyerAgentConfig
from procur.llm.client import LLMClient
from procur.models import VendorGuardrails, VendorProfile
from procur.services import (
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
from procur.services.scoring_service import ScoreWeights


def build_mock_vendor(vendor_id: str, name: str) -> VendorProfile:
    return VendorProfile(
        vendor_id=vendor_id,
        name=name,
        capability_tags=["crm", "automation"],
        certifications=["soc2"],
        regions=["us-east"],
        lead_time_brackets={"default": (15, 30)},
        price_tiers={"100": 100.0},
        guardrails=VendorGuardrails(price_floor=85.0, payment_terms_allowed=["Net30"]),
        reliability_stats={"sla": 0.98},
        contact_endpoints={"bank_account": "verified"},
    )


def main() -> None:
    llm_client = LLMClient(api_key="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")
    policy_engine = PolicyEngine()
    compliance_service = ComplianceService(mandatory_certifications=["soc2"])
    guardrail_service = GuardrailService()
    scoring_service = ScoringService(weights=ScoreWeights())
    negotiation_engine = NegotiationEngine(policy_engine, scoring_service)
    explainability_service = ExplainabilityService()
    audit_service = AuditTrailService()
    memory_service = MemoryService()
    retrieval_service = RetrievalService()

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

    raw_text = "We need a CRM for 100 seats with SOC2 compliance under $120k."
    policy_summary = "Budget cap 120000 USD, risk threshold 0.7"
    vendors = [
        build_mock_vendor("vendor-a", "AcmeCRM"),
        build_mock_vendor("vendor-b", "BetaCRM"),
    ]

    bundles = buyer_agent.run(raw_text, policy_summary, vendors)
    print(bundles)

    audit_payload = buyer_agent.export_audit()
    if audit_payload:
        print("\n-- Audit Trail --")
        print(audit_payload)

    memories = memory_service.all_memories()
    if memories:
        print("\n-- Structured Memories --")
        for memory in memories:
            print({
                "vendor_id": memory.vendor_id,
                "outcome": memory.outcome,
                "rounds": len(memory.rounds),
                "savings": memory.savings,
            })


if __name__ == "__main__":
    main()
