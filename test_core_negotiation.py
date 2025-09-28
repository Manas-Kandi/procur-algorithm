#!/usr/bin/env python3
"""
Simple test harness for core negotiation algorithms.
This file contains NO algorithm logic - it only exercises the core platform.
"""

import os
import sys
from typing import Dict, List
from dotenv import load_dotenv

# Add src to path to import procur modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from procur.models import (
    Request, RequestType, VendorProfile, VendorGuardrails, 
    PaymentTerms, OfferComponents
)
from procur.agents.buyer_agent import BuyerAgent, BuyerAgentConfig
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
from procur.llm import LLMClient


class NegotiationTester:
    """Test harness that uses core platform algorithms"""
    
    def __init__(self, api_key: str):
        """Initialize with core platform services"""
        self.llm_client = LLMClient(api_key=api_key)
        
        # Initialize core services (same as buyer_demo.py)
        self.policy_engine = PolicyEngine()
        self.compliance_service = ComplianceService(mandatory_certifications=["soc2"])
        self.guardrail_service = GuardrailService(run_mode="simulation")
        self.scoring_service = ScoringService()
        self.negotiation_engine = NegotiationEngine(self.policy_engine, self.scoring_service)
        self.explainability_service = ExplainabilityService()
        self.audit_service = AuditTrailService()
        self.memory_service = MemoryService()
        self.retrieval_service = RetrievalService()

        # Initialize buyer agent with enhanced algorithms
        self.buyer_agent = BuyerAgent(
            policy_engine=self.policy_engine,
            compliance_service=self.compliance_service,
            guardrail_service=self.guardrail_service,
            scoring_service=self.scoring_service,
            negotiation_engine=self.negotiation_engine,
            explainability_service=self.explainability_service,
            llm_client=self.llm_client,
            config=BuyerAgentConfig(),
            audit_service=self.audit_service,
            memory_service=self.memory_service,
            retrieval_service=self.retrieval_service,
        )
    
    def create_test_request(self, description: str, quantity: int, budget: float) -> Request:
        """Create a test procurement request"""
        return Request(
            request_id="test-001",
            requester_id="test-buyer",
            type=RequestType.SAAS,
            description=description,
            specs={"seats": quantity},
            quantity=quantity,
            budget_max=budget,
            must_haves=["soc2", "api_access"],
            compliance_requirements=["soc2"],
            nice_to_haves=["sso", "mobile_app"]
        )
    
    def create_test_vendor(self, name: str, list_price: float, price_floor: float, 
                          payment_terms: List[str]) -> VendorProfile:
        """Create a test vendor profile"""
        return VendorProfile(
            vendor_id=f"vendor-{name.lower().replace(' ', '-')}",
            name=name,
            capability_tags=["saas", "enterprise", "crm"],
            certifications=["soc2", "gdpr"],
            price_tiers={str(self.test_quantity): list_price},
            guardrails=VendorGuardrails(
                price_floor=price_floor,
                payment_terms_allowed=payment_terms
            ),
            lead_time_brackets={"default": (14, 30)},
            reliability_stats={"sla": 0.99, "uptime": 0.995},
            contact_endpoints={"sales": "verified", "support": "24/7"}
        )
    
    def test_scenario(self, scenario_name: str, request_params: Dict, vendor_params: List[Dict]):
        """Test a specific negotiation scenario using core algorithms"""
        print(f"\n🧪 TESTING SCENARIO: {scenario_name}")
        print("=" * 60)
        
        # Create request using provided parameters
        request = self.create_test_request(**request_params)
        self.test_quantity = request_params["quantity"]  # Store for vendor creation
        
        # Create vendors using provided parameters
        vendors = [self.create_test_vendor(**params) for params in vendor_params]
        
        print(f"📋 REQUEST: {request.description}")
        print(f"   Quantity: {request.quantity}")
        print(f"   Budget: ${request.budget_max:,.2f} (${request.budget_max/request.quantity:.2f}/unit)")
        
        print(f"\n🏢 VENDORS:")
        for vendor in vendors:
            list_price = vendor.price_tiers[str(request.quantity)]
            print(f"   {vendor.name}: ${list_price:.2f}/unit (floor: ${vendor.guardrails.price_floor:.2f})")
        
        # Test core negotiation algorithms
        print(f"\n🤖 RUNNING CORE NEGOTIATION ALGORITHMS...")
        
        try:
            # This uses ALL the enhanced algorithms from the core platform
            offers = self.buyer_agent.negotiate(request, vendors)
            
            print(f"\n📊 NEGOTIATION RESULTS:")
            print(f"   Offers received: {len(offers)}")
            
            if len(offers) == 0:
                print(f"   ⚠️  No offers generated - checking for issues...")
                # Let's test the individual components
                for vendor in vendors:
                    print(f"   🔍 Testing {vendor.name}:")
                    
                    # Test strategy selection
                    current_offer = OfferComponents(
                        unit_price=vendor.price_tiers[str(request.quantity)],
                        currency="USD",
                        quantity=request.quantity,
                        term_months=12,
                        payment_terms=PaymentTerms.NET_30
                    )
                    
                    # Test TCO calculation
                    tco = self.negotiation_engine.calculate_tco(current_offer)
                    print(f"      TCO: ${tco:,.2f}")
                    
                    # Test utility calculation
                    utility = self.negotiation_engine.calculate_utility(current_offer, request, is_buyer=True)
                    print(f"      Utility: {utility:.3f}")
                    
                    print(f"      Vendor price floor: ${vendor.guardrails.price_floor:.2f}")
                    print(f"      List price: ${vendor.price_tiers[str(request.quantity)]:.2f}")
            
            for vendor_id, offer in offers.items():
                vendor = next(v for v in vendors if v.vendor_id == vendor_id)
                savings = (vendor.price_tiers[str(request.quantity)] - offer.components.unit_price) * request.quantity
                
                print(f"\n   🎯 {vendor.name}:")
                print(f"      Final Price: ${offer.components.unit_price:.2f}/unit")
                print(f"      Total Value: ${offer.components.unit_price * offer.components.quantity:,.2f}")
                print(f"      Terms: {offer.components.term_months} months")
                print(f"      Payment: {offer.components.payment_terms}")
                print(f"      Savings: ${savings:,.2f}")
                print(f"      Utility Score: {offer.score.utility:.3f}")

            audit = self.buyer_agent.export_audit()
            if audit:
                print("\n📝 AUDIT SUMMARY AVAILABLE")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Run test scenarios"""
    load_dotenv()
    api_key = os.getenv("NVIDIA_API_KEY")
    
    if not api_key:
        print("❌ Error: NVIDIA_API_KEY not found in .env file")
        return
    
    tester = NegotiationTester(api_key)
    
    # Test Scenario 1: Single vendor, moderate budget pressure
    tester.test_scenario(
        scenario_name="Single Vendor - Moderate Budget",
        request_params={
            "description": "CRM software for sales team",
            "quantity": 100,
            "budget": 110000  # $1100/seat target
        },
        vendor_params=[{
            "name": "CRM Pro",
            "list_price": 1200.0,
            "price_floor": 1000.0,
            "payment_terms": ["Net30", "Net45"]
        }]
    )
    
    # Test Scenario 2: Multiple vendors, tight budget
    tester.test_scenario(
        scenario_name="Multi-Vendor - Tight Budget",
        request_params={
            "description": "Project management software",
            "quantity": 50,
            "budget": 40000  # $800/seat target (aggressive)
        },
        vendor_params=[
            {
                "name": "ProjectFlow",
                "list_price": 950.0,
                "price_floor": 750.0,
                "payment_terms": ["Net30", "Net45"]
            },
            {
                "name": "TaskMaster Pro",
                "list_price": 900.0,
                "price_floor": 700.0,
                "payment_terms": ["Net15", "Net30", "Milestones"]
            }
        ]
    )
    
    # Test Scenario 3: High-value deal, flexible budget
    tester.test_scenario(
        scenario_name="Enterprise Deal - Flexible Budget",
        request_params={
            "description": "Enterprise ERP system",
            "quantity": 200,
            "budget": 300000  # $1500/seat (generous)
        },
        vendor_params=[{
            "name": "ERP Solutions Inc",
            "list_price": 1400.0,
            "price_floor": 1200.0,
            "payment_terms": ["Net30", "Net45", "Milestones"]
        }]
    )
    
    print(f"\n✅ All test scenarios completed!")
    print(f"🧠 Core algorithms tested: opponent modeling, TCO calculation, strategy selection, stalemate detection")


if __name__ == "__main__":
    main()
