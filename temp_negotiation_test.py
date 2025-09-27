"""
TEMPORARY TEST FILE - Advanced Buyer vs Seller Negotiation Simulation
Implements sophisticated bargaining with opponent modeling, multi-issue trades, and TCO optimization.
DELETE THIS FILE WHEN DONE TESTING.
"""

import os
import time
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from procur.agents import BuyerAgent, BuyerAgentConfig, SellerAgent, SellerAgentConfig
from procur.llm.client import LLMClient
from procur.llm.prompts import negotiation_prompt
from procur.llm.validators import guarded_completion, parse_negotiation_message
from procur.models import (
    VendorGuardrails, VendorProfile, Request, RequestType, 
    NegotiationMessage, OfferComponents, PaymentTerms, ActorRole, NextStepHint,
    MachineRationale
)
from procur.services import (
    ComplianceService, ExplainabilityService, GuardrailService,
    NegotiationEngine, PolicyEngine, ScoringService
)
from procur.services.scoring_service import ScoreWeights


@dataclass
class OpponentModel:
    """Track opponent's behavior and preferences"""
    price_floor_estimate: float
    price_ceiling_estimate: float
    price_elasticity: float = 0.5  # 0=rigid, 1=flexible
    term_elasticity: float = 0.5
    payment_elasticity: float = 0.5
    consecutive_no_price_moves: int = 0
    last_offers: List[OfferComponents] = None
    
    def __post_init__(self):
        if self.last_offers is None:
            self.last_offers = []


@dataclass
class NegotiationState:
    """Track negotiation progress and strategy"""
    round_num: int = 0
    target_price: float = 0
    target_tco: float = 0
    min_acceptable_utility: float = 0.7
    concession_schedule: List[str] = None
    stalemate_rounds: int = 0
    last_buyer_offer: Optional[OfferComponents] = None
    last_seller_offer: Optional[OfferComponents] = None
    
    def __post_init__(self):
        if self.concession_schedule is None:
            self.concession_schedule = ["price_anchor", "term_trade", "payment_trade", "value_add", "ultimatum"]


@dataclass
class OfferBundle:
    """Multi-dimensional offer with utility calculation"""
    price: float
    term_months: int
    payment_terms: PaymentTerms
    value_adds: Dict[str, float]  # training_credits, support_upgrade, etc.
    tco: float = 0
    utility: float = 0


class NegotiationSimulator:
    def __init__(self, api_key: str):
        self.llm_client = LLMClient(api_key=api_key)
        self.vendor = self.create_test_vendor()
        self.buyer_model = OpponentModel(
            price_floor_estimate=self.vendor.guardrails.price_floor * 0.8,  # Conservative estimate
            price_ceiling_estimate=self.vendor.price_tiers["150"] * 1.1
        )
        self.seller_model = OpponentModel(
            price_floor_estimate=900,  # Seller estimates buyer's budget floor
            price_ceiling_estimate=1200  # Seller knows buyer's max
        )
        self.negotiation_state = NegotiationState()
        self.negotiation_history: List[NegotiationMessage] = []
        
    def calculate_tco(self, offer: OfferComponents, discount_rate: float = 0.05) -> float:
        """Calculate Total Cost of Ownership with time value of money"""
        monthly_cost = offer.unit_price * offer.quantity
        
        # Payment terms adjustment (cash flow impact)
        payment_multiplier = {
            PaymentTerms.NET_15: 0.995,  # Small discount for fast payment
            PaymentTerms.NET_30: 1.0,    # Baseline
            PaymentTerms.NET_45: 1.015,  # Premium for delayed payment
            PaymentTerms.MILESTONES: 0.99,
            PaymentTerms.DEPOSIT: 0.985
        }.get(offer.payment_terms, 1.0)
        
        # Discount future payments
        total_tco = 0
        for month in range(offer.term_months):
            monthly_payment = monthly_cost * payment_multiplier
            discounted_payment = monthly_payment / ((1 + discount_rate/12) ** month)
            total_tco += discounted_payment
            
        return total_tco
        
    def calculate_utility(self, offer: OfferComponents, request: Request, is_buyer: bool = True) -> float:
        """Calculate utility score for an offer"""
        tco = self.calculate_tco(offer)
        
        if is_buyer:
            # Buyer utility: lower cost = higher utility
            cost_utility = max(0, 1 - (tco / (request.budget_max * 1.2)))
            
            # Term preference (shorter terms preferred)
            term_utility = max(0, 1 - (offer.term_months - 12) / 24)
            
            # Payment terms utility
            payment_utility = {
                PaymentTerms.NET_15: 0.9,
                PaymentTerms.NET_30: 1.0,
                PaymentTerms.NET_45: 0.8,
                PaymentTerms.MILESTONES: 0.95,
                PaymentTerms.DEPOSIT: 0.85
            }.get(offer.payment_terms, 0.8)
            
            return 0.6 * cost_utility + 0.25 * term_utility + 0.15 * payment_utility
        else:
            # Seller utility: higher margin = higher utility
            margin = offer.unit_price - self.vendor.guardrails.price_floor
            max_margin = self.vendor.price_tiers["150"] - self.vendor.guardrails.price_floor
            margin_utility = margin / max_margin if max_margin > 0 else 0
            
            # Longer terms preferred (predictable revenue)
            term_utility = min(1.0, offer.term_months / 36)
            
            # Payment terms utility (faster payment preferred)
            payment_utility = {
                PaymentTerms.NET_15: 1.0,
                PaymentTerms.NET_30: 0.9,
                PaymentTerms.NET_45: 0.7,
                PaymentTerms.MILESTONES: 0.95,
                PaymentTerms.DEPOSIT: 1.0
            }.get(offer.payment_terms, 0.7)
            
            return 0.7 * margin_utility + 0.2 * term_utility + 0.1 * payment_utility
            
    def update_opponent_model(self, model: OpponentModel, new_offer: OfferComponents, previous_offer: Optional[OfferComponents]):
        """Update beliefs about opponent based on their moves"""
        if previous_offer is None:
            model.last_offers.append(new_offer)
            return
            
        # Track price movement
        price_change = new_offer.unit_price - previous_offer.unit_price
        if abs(price_change) < 1:  # No significant price movement
            model.consecutive_no_price_moves += 1
            model.price_elasticity = max(0.1, model.price_elasticity - 0.1)
        else:
            model.consecutive_no_price_moves = 0
            model.price_elasticity = min(0.9, model.price_elasticity + 0.1)
            
        # Update price bounds
        if price_change < 0:  # Price decreased
            model.price_floor_estimate = max(model.price_floor_estimate, new_offer.unit_price - 50)
        
        # Track term flexibility
        term_change = new_offer.term_months - previous_offer.term_months
        if abs(term_change) > 0:
            model.term_elasticity = min(0.9, model.term_elasticity + 0.1)
            
        model.last_offers.append(new_offer)
        if len(model.last_offers) > 3:
            model.last_offers.pop(0)
            
    def generate_iso_utility_bundles(self, current_utility: float, request: Request, is_buyer: bool = True) -> List[OfferBundle]:
        """Generate multiple offers with similar utility but different trade-offs"""
        bundles = []
        base_price = request.budget_max / request.quantity if is_buyer else self.vendor.price_tiers["150"]
        
        # Price-focused bundle
        bundles.append(OfferBundle(
            price=base_price * 0.92,
            term_months=12,
            payment_terms=PaymentTerms.NET_30,
            value_adds={}
        ))
        
        # Term-trade bundle (longer term for lower price)
        bundles.append(OfferBundle(
            price=base_price * 0.95,
            term_months=24,
            payment_terms=PaymentTerms.NET_30,
            value_adds={}
        ))
        
        # Payment-trade bundle (faster payment for lower price)
        bundles.append(OfferBundle(
            price=base_price * 0.94,
            term_months=12,
            payment_terms=PaymentTerms.NET_15,
            value_adds={}
        ))
        
        # Value-add bundle
        bundles.append(OfferBundle(
            price=base_price * 0.98,
            term_months=12,
            payment_terms=PaymentTerms.NET_30,
            value_adds={"training_credits": 5000, "premium_support": 1}
        ))
        
        return bundles
        
    def detect_stalemate(self) -> bool:
        """Detect if negotiation is stuck"""
        if len(self.negotiation_history) < 4:
            return False
            
        # Check if last 2 rounds had no meaningful progress
        recent_offers = self.negotiation_history[-4:]
        buyer_offers = [msg for msg in recent_offers if msg.actor == ActorRole.BUYER_AGENT]
        seller_offers = [msg for msg in recent_offers if msg.actor == ActorRole.SELLER_AGENT]
        
        if len(buyer_offers) >= 2 and len(seller_offers) >= 2:
            buyer_price_change = abs(buyer_offers[-1].proposal.unit_price - buyer_offers[-2].proposal.unit_price)
            seller_price_change = abs(seller_offers[-1].proposal.unit_price - seller_offers[-2].proposal.unit_price)
            
            return buyer_price_change < 10 and seller_price_change < 10
            
        return False
        
    def create_test_request(self) -> Request:
        """Create a realistic procurement request"""
        return Request(
            request_id="test-req-001",
            requester_id="buyer-001",
            type=RequestType.SAAS,
            description="Enterprise CRM software for 150 sales team members",
            specs={
                "seats": 150,
                "features": ["lead_management", "pipeline_tracking", "reporting", "api_access"],
                "integrations": ["salesforce", "hubspot"],
                "storage": "unlimited",
                "support": "24/7"
            },
            quantity=150,
            budget_max=180000,  # $180k budget
            currency="USD",
            must_haves=["soc2", "gdpr_compliance", "api_access"]
        )
        
    def create_test_vendor(self) -> VendorProfile:
        """Create a realistic vendor profile"""
        return VendorProfile(
            vendor_id="vendor-crm-pro",
            name="CRM Pro Solutions",
            capability_tags=["crm", "enterprise", "api", "integrations"],
            certifications=["soc2", "gdpr", "iso27001"],
            regions=["us-east", "eu-west"],
            lead_time_brackets={"standard": (30, 45), "enterprise": (45, 60)},
            price_tiers={"150": 1200.0},  # $1200 per seat
            guardrails=VendorGuardrails(
                price_floor=1000.0,  # Won't go below $1000/seat
                payment_terms_allowed=["Net30", "Net45", "Milestones"]
            ),
            reliability_stats={"sla": 0.995, "uptime": 0.999},
            contact_endpoints={"sales": "verified", "support": "24/7"},
        )
        
    def generate_buyer_message(self, request: Request, current_offer: OfferComponents, round_num: int) -> NegotiationMessage:
        """Generate sophisticated buyer negotiation message with dynamic strategy"""
        self.negotiation_state.round_num = round_num
        
        # Determine strategy based on round and opponent model
        strategy = self.get_buyer_strategy(current_offer, round_num)
        target_bundle = self.get_target_bundle_for_buyer(request, current_offer, strategy)
        
        # Update opponent model
        if round_num > 1 and len(self.negotiation_history) >= 2:
            previous_seller_offer = None
            for msg in reversed(self.negotiation_history):
                if msg.actor == ActorRole.SELLER_AGENT:
                    previous_seller_offer = msg.proposal
                    break
            if previous_seller_offer:
                self.update_opponent_model(self.buyer_model, current_offer, previous_seller_offer)
        
        # Generate justification based on strategy
        justification = self.generate_buyer_justification(strategy, target_bundle, current_offer)
        concession_type = self.get_concession_type(strategy)
        
        messages = [
            {
                "role": "system",
                "content": f"""You are a sophisticated procurement buyer using strategy: {strategy}.
                
                Current seller offer: ${current_offer.unit_price}/seat, {current_offer.term_months}mo, {current_offer.payment_terms}
                Your target: ${target_bundle.price}/seat, {target_bundle.term_months}mo, {target_bundle.payment_terms}
                Estimated seller price floor: ${self.buyer_model.price_floor_estimate}/seat
                
                Strategy details:
                - {strategy}: {self.get_strategy_description(strategy)}
                
                Respond with JSON matching this schema: {{
                    "actor": "buyer_agent",
                    "round": {round_num},
                    "proposal": {{
                        "unit_price": {target_bundle.price},
                        "currency": "USD",
                        "quantity": {request.quantity},
                        "term_months": {target_bundle.term_months},
                        "payment_terms": "{target_bundle.payment_terms.value}"
                    }},
                    "justification_bullets": {justification},
                    "machine_rationale": {{
                        "score_components": {{"tco": 0.8, "terms": 0.9, "risk": 0.7}},
                        "constraints_respected": ["budget_cap", "policy_compliance"],
                        "concession_taken": "{concession_type}"
                    }},
                    "next_step_hint": "counter"
                }}"""
            },
            {
                "role": "user",
                "content": f"Execute {strategy} strategy. Current offer: ${current_offer.unit_price}/seat. Target: ${target_bundle.price}/seat. Round {round_num}."
            }
        ]
        
        return guarded_completion(
            lambda: self.llm_client.complete(messages),
            parser=parse_negotiation_message
        )
        
    def get_buyer_strategy(self, current_offer: OfferComponents, round_num: int) -> str:
        """Determine buyer strategy based on round and situation"""
        if round_num == 1:
            return "price_anchor"
        elif round_num == 2 and self.buyer_model.consecutive_no_price_moves > 0:
            return "term_trade"
        elif round_num == 3 and current_offer.payment_terms == PaymentTerms.NET_45:
            return "payment_trade"
        elif self.detect_stalemate():
            return "ultimatum"
        elif round_num >= 4:
            return "value_add"
        else:
            return "price_pressure"
            
    def get_target_bundle_for_buyer(self, request: Request, current_offer: OfferComponents, strategy: str) -> OfferBundle:
        """Generate target bundle based on strategy"""
        base_price = request.budget_max / request.quantity
        
        if strategy == "price_anchor":
            return OfferBundle(
                price=base_price * 0.88,  # Aggressive anchor
                term_months=12,
                payment_terms=PaymentTerms.NET_30,
                value_adds={}
            )
        elif strategy == "term_trade":
            return OfferBundle(
                price=current_offer.unit_price * 0.95,  # 5% price reduction
                term_months=24,  # Offer longer term
                payment_terms=PaymentTerms.NET_30,
                value_adds={}
            )
        elif strategy == "payment_trade":
            return OfferBundle(
                price=current_offer.unit_price * 0.97,  # 3% price reduction
                term_months=current_offer.term_months,
                payment_terms=PaymentTerms.NET_15,  # Faster payment
                value_adds={}
            )
        elif strategy == "value_add":
            return OfferBundle(
                price=current_offer.unit_price * 0.98,
                term_months=current_offer.term_months,
                payment_terms=PaymentTerms.NET_30,
                value_adds={"training_budget": 3000, "implementation_support": 1}
            )
        elif strategy == "ultimatum":
            return OfferBundle(
                price=max(self.buyer_model.price_floor_estimate + 25, base_price * 0.92),
                term_months=12,
                payment_terms=PaymentTerms.NET_30,
                value_adds={}
            )
        else:  # price_pressure
            return OfferBundle(
                price=current_offer.unit_price * 0.96,
                term_months=current_offer.term_months,
                payment_terms=current_offer.payment_terms,
                value_adds={}
            )
            
    def generate_buyer_justification(self, strategy: str, target_bundle: OfferBundle, current_offer: OfferComponents) -> List[str]:
        """Generate contextual justification bullets"""
        justifications = {
            "price_anchor": [
                "Market research shows competitive pricing at this level",
                "Volume purchase of 150 seats warrants significant discount",
                "Budget constraints require aggressive cost management"
            ],
            "term_trade": [
                "Willing to commit to longer term for better pricing",
                "Extended contract provides vendor revenue predictability",
                "Multi-year agreement reduces administrative overhead"
            ],
            "payment_trade": [
                "Accelerated payment terms improve vendor cash flow",
                "NET15 payment reduces vendor financing costs",
                "Fast payment justifies price concession"
            ],
            "value_add": [
                "Training investment ensures successful implementation",
                "Professional services reduce deployment risk",
                "Value-added services justify premium pricing"
            ],
            "ultimatum": [
                "Final offer based on comprehensive market analysis",
                "This represents our maximum budget allocation",
                "Decision timeline requires immediate resolution"
            ],
            "price_pressure": [
                "Continued price reduction needed for approval",
                "Competitive alternatives available at lower cost",
                "Budget approval requires additional savings"
            ]
        }
        return justifications.get(strategy, ["Seeking mutually beneficial agreement"])
        
    def get_strategy_description(self, strategy: str) -> str:
        """Get description of strategy for LLM context"""
        descriptions = {
            "price_anchor": "Set aggressive low price anchor to establish negotiation range",
            "term_trade": "Offer longer contract term in exchange for lower unit price",
            "payment_trade": "Offer faster payment terms for price concession",
            "value_add": "Request additional services/training to justify higher price",
            "ultimatum": "Final best offer with clear decision deadline",
            "price_pressure": "Continue pushing for incremental price reductions"
        }
        return descriptions.get(strategy, "Standard price negotiation")
        
    def get_concession_type(self, strategy: str) -> str:
        """Map strategy to concession type"""
        mapping = {
            "price_anchor": "price",
            "term_trade": "term",
            "payment_trade": "payment",
            "value_add": "value_add",
            "ultimatum": "price",
            "price_pressure": "price"
        }
        return mapping.get(strategy, "price")
        
    def generate_seller_message(self, request: Request, buyer_offer: OfferComponents, round_num: int) -> NegotiationMessage:
        """Generate sophisticated seller negotiation message with dynamic strategy"""
        self.negotiation_state.round_num = round_num
        
        # Determine seller strategy
        strategy = self.get_seller_strategy(buyer_offer, round_num)
        target_bundle = self.get_target_bundle_for_seller(request, buyer_offer, strategy)
        
        # Update opponent model
        if round_num > 1 and len(self.negotiation_history) >= 1:
            previous_buyer_offer = None
            for msg in reversed(self.negotiation_history):
                if msg.actor == ActorRole.BUYER_AGENT:
                    previous_buyer_offer = msg.proposal
                    break
            if previous_buyer_offer:
                self.update_opponent_model(self.seller_model, buyer_offer, previous_buyer_offer)
        
        # Generate justification and decision
        justification = self.generate_seller_justification(strategy, target_bundle, buyer_offer)
        decision = self.get_seller_decision(buyer_offer, target_bundle)
        
        messages = [
            {
                "role": "system",
                "content": f"""You are a sophisticated vendor sales agent using strategy: {strategy}.
                
                Buyer's offer: ${buyer_offer.unit_price}/seat, {buyer_offer.term_months}mo, {buyer_offer.payment_terms}
                Your target: ${target_bundle.price}/seat, {target_bundle.term_months}mo, {target_bundle.payment_terms}
                Your price floor: ${self.vendor.guardrails.price_floor}/seat (NEVER go below this)
                Estimated buyer budget ceiling: ${self.seller_model.price_ceiling_estimate}/seat
                
                Strategy details:
                - {strategy}: {self.get_seller_strategy_description(strategy)}
                
                Decision: {decision}
                
                Respond with JSON matching this schema: {{
                    "actor": "seller_agent",
                    "round": {round_num},
                    "proposal": {{
                        "unit_price": {target_bundle.price},
                        "currency": "USD",
                        "quantity": {request.quantity},
                        "term_months": {target_bundle.term_months},
                        "payment_terms": "{target_bundle.payment_terms.value}"
                    }},
                    "justification_bullets": {justification},
                    "machine_rationale": {{
                        "score_components": {{"margin": 0.8, "terms": 0.7, "risk": 0.9}},
                        "constraints_respected": ["price_floor", "payment_terms_allowed"],
                        "concession_taken": "{self.get_seller_concession_type(strategy)}"
                    }},
                    "next_step_hint": "{decision}"
                }}"""
            },
            {
                "role": "user",
                "content": f"Execute {strategy} strategy. Buyer offer: ${buyer_offer.unit_price}/seat. Your target: ${target_bundle.price}/seat. Decision: {decision}. Round {round_num}."
            }
        ]
        
        return guarded_completion(
            lambda: self.llm_client.complete(messages),
            parser=parse_negotiation_message
        )
        
    def get_seller_strategy(self, buyer_offer: OfferComponents, round_num: int) -> str:
        """Determine seller strategy based on buyer offer and round"""
        price_floor = self.vendor.guardrails.price_floor
        
        if buyer_offer.unit_price < price_floor:
            return "reject_below_floor"
        elif buyer_offer.unit_price < price_floor * 1.05:  # Very close to floor
            return "minimal_concession"
        elif round_num == 1:
            return "anchor_high"
        elif buyer_offer.term_months > 12:
            return "term_value"
        elif buyer_offer.payment_terms == PaymentTerms.NET_15:
            return "payment_premium"
        elif round_num >= 4:
            return "close_deal"
        else:
            return "gradual_concession"
            
    def get_target_bundle_for_seller(self, request: Request, buyer_offer: OfferComponents, strategy: str) -> OfferBundle:
        """Generate seller target bundle based on strategy"""
        price_floor = self.vendor.guardrails.price_floor
        list_price = self.vendor.price_tiers["150"]
        
        if strategy == "reject_below_floor":
            return OfferBundle(
                price=price_floor * 1.1,  # 10% above floor
                term_months=12,
                payment_terms=PaymentTerms.NET_30,
                value_adds={}
            )
        elif strategy == "minimal_concession":
            return OfferBundle(
                price=price_floor * 1.02,  # Minimal margin
                term_months=buyer_offer.term_months,
                payment_terms=buyer_offer.payment_terms,
                value_adds={}
            )
        elif strategy == "anchor_high":
            return OfferBundle(
                price=list_price * 0.95,  # 5% off list
                term_months=12,
                payment_terms=PaymentTerms.NET_45,  # Favorable to seller
                value_adds={}
            )
        elif strategy == "term_value":
            # Reward longer term with better price
            term_discount = min(0.08, (buyer_offer.term_months - 12) * 0.02)
            return OfferBundle(
                price=list_price * (0.95 - term_discount),
                term_months=buyer_offer.term_months,
                payment_terms=PaymentTerms.NET_30,
                value_adds={}
            )
        elif strategy == "payment_premium":
            # Reward fast payment with price concession
            return OfferBundle(
                price=list_price * 0.92,  # 8% off for NET15
                term_months=buyer_offer.term_months,
                payment_terms=PaymentTerms.NET_15,
                value_adds={}
            )
        elif strategy == "close_deal":
            # Final concession to close
            return OfferBundle(
                price=max(price_floor * 1.05, buyer_offer.unit_price * 1.02),
                term_months=buyer_offer.term_months,
                payment_terms=buyer_offer.payment_terms,
                value_adds={"implementation_support": 1, "training_credits": 2000}
            )
        else:  # gradual_concession
            current_price = list_price * 0.95  # Start from 5% off
            concession = (round(self.negotiation_state.round_num) - 1) * 0.02  # 2% per round
            return OfferBundle(
                price=max(price_floor * 1.1, current_price * (1 - concession)),
                term_months=buyer_offer.term_months,
                payment_terms=PaymentTerms.NET_30,
                value_adds={}
            )
            
    def generate_seller_justification(self, strategy: str, target_bundle: OfferBundle, buyer_offer: OfferComponents) -> List[str]:
        """Generate contextual seller justification bullets"""
        justifications = {
            "reject_below_floor": [
                "Offer below minimum viable pricing for sustainable service",
                "Quality and support standards require minimum margin",
                "Alternative pricing options available with adjusted terms"
            ],
            "minimal_concession": [
                "Pricing at absolute minimum for enterprise-grade solution",
                "Comprehensive support and SLA included at this level",
                "Limited flexibility due to cost structure constraints"
            ],
            "anchor_high": [
                "Premium enterprise solution with proven ROI",
                "Comprehensive feature set justifies market positioning",
                "Industry-leading support and reliability included"
            ],
            "term_value": [
                "Extended term commitment enables better pricing",
                "Multi-year agreement provides mutual value and stability",
                "Long-term partnership discount applied"
            ],
            "payment_premium": [
                "Accelerated payment terms enable competitive pricing",
                "Cash flow optimization allows for price concession",
                "NET15 terms provide mutual benefit"
            ],
            "close_deal": [
                "Final competitive offer with maximum value",
                "Additional services included to ensure success",
                "Best available pricing for immediate decision"
            ],
            "gradual_concession": [
                "Competitive adjustment based on volume commitment",
                "Market-aligned pricing for enterprise deployment",
                "Balanced approach considering mutual value"
            ]
        }
        return justifications.get(strategy, ["Competitive market pricing for enterprise solution"])
        
    def get_seller_strategy_description(self, strategy: str) -> str:
        """Get description of seller strategy for LLM context"""
        descriptions = {
            "reject_below_floor": "Firmly reject offers below minimum viable price",
            "minimal_concession": "Offer smallest possible concession near price floor",
            "anchor_high": "Start with high anchor to establish value perception",
            "term_value": "Reward longer contract terms with better pricing",
            "payment_premium": "Offer price concession for faster payment terms",
            "close_deal": "Make final concession with value-adds to close",
            "gradual_concession": "Make incremental price concessions each round"
        }
        return descriptions.get(strategy, "Standard competitive pricing")
        
    def get_seller_concession_type(self, strategy: str) -> str:
        """Map seller strategy to concession type"""
        mapping = {
            "reject_below_floor": "none",
            "minimal_concession": "price",
            "anchor_high": "none",
            "term_value": "price",
            "payment_premium": "price",
            "close_deal": "price_and_value",
            "gradual_concession": "price"
        }
        return mapping.get(strategy, "price")
        
    def get_seller_decision(self, buyer_offer: OfferComponents, target_bundle: OfferBundle) -> str:
        """Determine seller's next step decision"""
        price_floor = self.vendor.guardrails.price_floor
        
        if buyer_offer.unit_price < price_floor:
            return "reject"
        elif abs(buyer_offer.unit_price - target_bundle.price) < 20:
            return "accept"
        else:
            return "counter"
            
    def run_simulation(self, max_rounds: int = 6) -> Dict[str, any]:
        """Run the complete negotiation simulation"""
        print("🚀 Starting Advanced Negotiation Simulation")
        print("=" * 60)
        
        request = self.create_test_request()
        
        # Seller starts with initial offer
        initial_offer = OfferComponents(
            unit_price=self.vendor.price_tiers["150"],  # Start at list price
            currency="USD",
            quantity=request.quantity,
            term_months=12,
            payment_terms=PaymentTerms.NET_45
        )
        
        print(f"\n📋 PROCUREMENT REQUEST")
        print(f"   Product: {request.description}")
        print(f"   Quantity: {request.quantity} seats")
        print(f"   Budget: ${request.budget_max:,.2f} (${request.budget_max/request.quantity:.2f}/seat)")
        print(f"   Must-haves: {request.must_haves}")
        
        print(f"\n🏢 VENDOR: {self.vendor.name}")
        print(f"   List Price: ${self.vendor.price_tiers['150']:.2f}/seat")
        print(f"   Price Floor: ${self.vendor.guardrails.price_floor:.2f}/seat")
        print(f"   Payment Terms: {self.vendor.guardrails.payment_terms_allowed}")
        
        print(f"\n💰 SELLER'S OPENING OFFER")
        print(f"   Price: ${initial_offer.unit_price:.2f}/seat")
        print(f"   Term: {initial_offer.term_months} months")
        print(f"   Payment: {initial_offer.payment_terms.value}")
        print(f"   Total Value: ${initial_offer.unit_price * initial_offer.quantity:,.2f}")
        
        current_offer = initial_offer
        round_num = 1
        
        while round_num <= max_rounds:
            print(f"\n{'='*20} ROUND {round_num} {'='*20}")
            
            # Buyer's turn
            print(f"\n🔵 BUYER'S MOVE (Round {round_num})")
            try:
                buyer_msg = self.generate_buyer_message(request, current_offer, round_num)
                self.negotiation_history.append(buyer_msg)
                
                buyer_strategy = self.get_buyer_strategy(current_offer, round_num)
                buyer_utility = self.calculate_utility(buyer_msg.proposal, request, is_buyer=True)
                buyer_tco = self.calculate_tco(buyer_msg.proposal)
                
                print(f"   Strategy: {buyer_strategy}")
                print(f"   Offer: ${buyer_msg.proposal.unit_price:.2f}/seat, {buyer_msg.proposal.term_months}mo, {buyer_msg.proposal.payment_terms}")
                print(f"   TCO: ${buyer_tco:,.2f}")
                print(f"   Utility: {buyer_utility:.3f}")
                print(f"   Justification: {buyer_msg.justification_bullets[0]}")
                
                # Check if seller would accept
                if buyer_msg.proposal.unit_price >= self.vendor.guardrails.price_floor * 1.02:
                    acceptance_prob = min(0.9, (buyer_msg.proposal.unit_price - self.vendor.guardrails.price_floor) / 
                                        (self.vendor.price_tiers["150"] - self.vendor.guardrails.price_floor))
                    print(f"   Seller acceptance probability: {acceptance_prob:.1%}")
                
            except Exception as e:
                print(f"   ❌ Error generating buyer message: {e}")
                break
                
            # Seller's turn
            print(f"\n🔴 SELLER'S RESPONSE")
            try:
                seller_msg = self.generate_seller_message(request, buyer_msg.proposal, round_num)
                self.negotiation_history.append(seller_msg)
                
                seller_strategy = self.get_seller_strategy(buyer_msg.proposal, round_num)
                seller_utility = self.calculate_utility(seller_msg.proposal, request, is_buyer=False)
                seller_margin = seller_msg.proposal.unit_price - self.vendor.guardrails.price_floor
                
                print(f"   Strategy: {seller_strategy}")
                print(f"   Counter: ${seller_msg.proposal.unit_price:.2f}/seat, {seller_msg.proposal.term_months}mo, {seller_msg.proposal.payment_terms}")
                print(f"   Margin: ${seller_margin:.2f}/seat")
                print(f"   Utility: {seller_utility:.3f}")
                print(f"   Justification: {seller_msg.justification_bullets[0]}")
                print(f"   Decision: {seller_msg.next_step_hint}")
                
                # Check for deal closure
                if seller_msg.next_step_hint == "accept":
                    print(f"\n🎉 DEAL CLOSED! Seller accepts buyer's offer.")
                    final_deal = buyer_msg.proposal
                    break
                elif abs(seller_msg.proposal.unit_price - buyer_msg.proposal.unit_price) < 25:
                    print(f"\n🤝 CONVERGENCE DETECTED - Offers within $25/seat")
                    
                current_offer = seller_msg.proposal
                
            except Exception as e:
                print(f"   ❌ Error generating seller message: {e}")
                break
                
            # Stalemate detection
            if self.detect_stalemate():
                print(f"\n⚠️  STALEMATE DETECTED - No meaningful progress in recent rounds")
                break
                
            round_num += 1
            
        # Final analysis
        print(f"\n{'='*20} NEGOTIATION COMPLETE {'='*20}")
        
        if round_num <= max_rounds and len(self.negotiation_history) >= 2:
            final_buyer_offer = None
            final_seller_offer = None
            
            for msg in reversed(self.negotiation_history):
                if msg.actor == ActorRole.BUYER_AGENT and final_buyer_offer is None:
                    final_buyer_offer = msg.proposal
                elif msg.actor == ActorRole.SELLER_AGENT and final_seller_offer is None:
                    final_seller_offer = msg.proposal
                    
            if final_buyer_offer and final_seller_offer:
                gap = abs(final_seller_offer.unit_price - final_buyer_offer.unit_price)
                print(f"\n📊 FINAL ANALYSIS:")
                print(f"   Buyer's final offer: ${final_buyer_offer.unit_price:.2f}/seat")
                print(f"   Seller's final offer: ${final_seller_offer.unit_price:.2f}/seat")
                print(f"   Price gap: ${gap:.2f}/seat")
                print(f"   Total rounds: {len(self.negotiation_history)}")
                
                # Opponent model insights
                print(f"\n🧠 OPPONENT MODELING INSIGHTS:")
                print(f"   Buyer's estimate of seller price floor: ${self.buyer_model.price_floor_estimate:.2f}")
                print(f"   Seller's estimate of buyer budget ceiling: ${self.seller_model.price_ceiling_estimate:.2f}")
                print(f"   Actual seller price floor: ${self.vendor.guardrails.price_floor:.2f}")
                print(f"   Actual buyer budget max: ${request.budget_max/request.quantity:.2f}")
                
        return {
            "rounds_completed": len(self.negotiation_history),
            "negotiation_history": self.negotiation_history,
            "final_gap": gap if 'gap' in locals() else None,
            "buyer_model": self.buyer_model,
            "seller_model": self.seller_model
        }


def main():
    """Run the advanced negotiation simulation"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv("NVIDIA_API_KEY")
    
    if not api_key:
        print("❌ Error: NVIDIA_API_KEY not found in .env file")
        return
        
    simulator = NegotiationSimulator(api_key)
    results = simulator.run_simulation(max_rounds=6)
    
    print(f"\n✅ Simulation completed with {results['rounds_completed']} total messages")


if __name__ == "__main__":
    main()
