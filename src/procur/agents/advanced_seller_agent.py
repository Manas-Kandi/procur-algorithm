"""Advanced seller agent with sophisticated negotiation capabilities."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple

from ..models import Offer, OfferComponents, Request, VendorProfile
from ..services import GuardrailService, NegotiationEngine, PolicyEngine, ScoringService
from ..services.policy_engine import PolicyResult
from ..services.guardrail_service import GuardrailAlert
from ..services.negotiation_engine import SellerStrategy, VendorNegotiationState

from .seller_personality import (
    VendorPersonality,
    VendorContext,
    get_personality_traits,
    adjust_traits_for_context,
)
from .seller_learning import (
    SellerLearningSystem,
    NegotiationHistory,
)
from .seller_strategies import (
    AdvancedSellerStrategy,
    StrategyContext,
    SellerStrategyEngine,
)
from .seller_constraints import (
    ConstraintManager,
    MultiBuyerContext,
)
from .seller_competitive import (
    CompetitiveIntelligenceSystem,
    CompetitiveIntelligence,
)


@dataclass
class AdvancedSellerConfig:
    """Configuration for advanced seller agent."""
    personality: VendorPersonality = VendorPersonality.STRATEGIC
    enable_learning: bool = True
    enable_constraints: bool = True
    enable_competitive_intelligence: bool = True
    response_window_hours: int = 24


class AdvancedSellerAgent:
    """
    Advanced seller agent with sophisticated negotiation capabilities.
    
    Features:
    - Personality-driven behavior (aggressive, cooperative, strategic, etc.)
    - Historical learning from past negotiations
    - Multi-buyer negotiation handling
    - Inventory and capacity constraints
    - Seasonal pricing adjustments
    - Competitive intelligence
    - Advanced counter-negotiation strategies
    """
    
    def __init__(
        self,
        vendor: VendorProfile,
        policy_engine: PolicyEngine,
        scoring_service: ScoringService,
        guardrail_service: GuardrailService,
        negotiation_engine: NegotiationEngine,
        config: Optional[AdvancedSellerConfig] = None,
    ):
        """Initialize advanced seller agent."""
        self.vendor = vendor
        self.policy_engine = policy_engine
        self.scoring_service = scoring_service
        self.guardrail_service = guardrail_service
        self.negotiation_engine = negotiation_engine
        self.config = config or AdvancedSellerConfig()
        
        # Initialize advanced components
        self.personality_traits = get_personality_traits(self.config.personality)
        self.vendor_context = VendorContext()
        self.learning_system = SellerLearningSystem() if self.config.enable_learning else None
        self.constraint_manager = ConstraintManager() if self.config.enable_constraints else None
        self.competitive_intelligence = CompetitiveIntelligenceSystem() if self.config.enable_competitive_intelligence else None
        self.strategy_engine = SellerStrategyEngine()
    
    def set_vendor_context(self, context: VendorContext):
        """Update vendor business context."""
        self.vendor_context = context
    
    def set_multi_buyer_context(self, context: MultiBuyerContext):
        """Update multi-buyer context."""
        if self.constraint_manager:
            self.constraint_manager.set_multi_buyer_context(context)
    
    def respond(
        self,
        request: Request,
        state: VendorNegotiationState,
        buyer_offer: OfferComponents,
        round_number: int,
        buyer_organization: Optional[str] = None,
        competitive_intel: Optional[CompetitiveIntelligence] = None,
    ) -> Tuple[Offer, AdvancedSellerStrategy, List[GuardrailAlert], PolicyResult, str]:
        """
        Generate sophisticated counter-offer.
        
        Returns:
            Tuple of (offer, strategy, alerts, policy_result, rationale)
        """
        # Adjust personality for context
        adjusted_traits = adjust_traits_for_context(
            self.personality_traits,
            self.vendor_context,
        )
        
        # Get buyer profile from learning
        buyer_profile = None
        if self.learning_system and buyer_organization:
            buyer_profile = self.learning_system.get_buyer_profile(buyer_organization)
        
        # Get category insights
        category_insights = None
        if self.learning_system:
            category_insights = self.learning_system.get_category_insights(
                request.category or "general"
            )
        
        # Calculate price gap
        current_price = state.current_offer_price or state.list_price
        price_gap_percentage = ((current_price - buyer_offer.unit_price) / current_price) * 100
        
        # Determine deal importance
        deal_importance = self._calculate_deal_importance(
            request,
            buyer_profile,
            competitive_intel,
        )
        
        # Build strategy context
        strategy_context = StrategyContext(
            round_number=round_number,
            total_rounds_expected=5,
            buyer_aggressiveness=self._estimate_buyer_aggressiveness(buyer_offer, state),
            price_gap_percentage=price_gap_percentage,
            buyer_profile=buyer_profile,
            category_insights=category_insights,
            personality_traits=adjusted_traits,
            vendor_context=self.vendor_context,
            competitive_pressure=competitive_intel.competitive_pressure if competitive_intel else 0.5,
            deal_importance=deal_importance,
        )
        
        # Select strategy
        strategy = self.strategy_engine.select_strategy(
            strategy_context,
            state,
            buyer_offer,
        )
        
        # Get current offer
        current_offer = OfferComponents(
            unit_price=current_price,
            quantity=buyer_offer.quantity,
            term_months=state.current_term_months or 12,
            payment_terms=state.current_payment_terms or "NET30",
            delivery_days=30,
        )
        
        # Apply constraints
        if self.constraint_manager:
            current_offer = self._apply_constraints(current_offer, request)
        
        # Execute strategy
        counter_components, rationale = self.strategy_engine.execute_strategy(
            strategy,
            current_offer,
            buyer_offer,
            state,
            strategy_context,
        )
        
        # Apply competitive intelligence
        if self.competitive_intelligence and competitive_intel:
            counter_components = self._apply_competitive_intelligence(
                counter_components,
                competitive_intel,
                request.category or "general",
            )
        
        # Validate with policy engine
        policy_feedback = self.policy_engine.validate_offer(
            request,
            counter_components,
            vendor=self.vendor,
            is_buyer_proposal=False,
        )
        
        # Enforce floor price
        if not policy_feedback.valid:
            floor = self.vendor.guardrails.price_floor or counter_components.unit_price
            
            # Adjust floor based on learning
            if self.learning_system and buyer_organization:
                floor = self.learning_system.get_recommended_floor(
                    floor,
                    buyer_organization,
                    request.category or "general",
                )
            
            counter_components.unit_price = max(counter_components.unit_price, floor)
        
        # Check guardrails
        guardrail_alerts = self.guardrail_service.vet_offer(
            self.vendor,
            counter_components,
        )
        
        # Score offer
        score = self.scoring_service.score_offer(
            self.vendor,
            counter_components,
            request,
        )
        
        # Create offer
        offer = Offer(
            offer_id=f"{request.request_id}-{self.vendor.vendor_id}-advanced-{round_number}",
            request_id=request.request_id,
            vendor_id=self.vendor.vendor_id,
            components=counter_components,
            score=score,
        )
        
        return offer, strategy, guardrail_alerts, policy_feedback, rationale
    
    def record_negotiation_outcome(
        self,
        negotiation_id: str,
        buyer_organization: str,
        category: str,
        initial_ask: float,
        final_price: float,
        rounds: int,
        outcome: str,
        duration_hours: float,
        buyer_aggressiveness: float,
    ):
        """Record negotiation outcome for learning."""
        if not self.learning_system:
            return
        
        concession_percentage = ((initial_ask - final_price) / initial_ask) * 100
        
        history = NegotiationHistory(
            negotiation_id=negotiation_id,
            buyer_organization=buyer_organization,
            category=category,
            initial_ask=initial_ask,
            final_price=final_price,
            rounds=rounds,
            outcome=outcome,
            duration_hours=duration_hours,
            concession_percentage=concession_percentage,
            buyer_aggressiveness=buyer_aggressiveness,
            timestamp=datetime.now(),
        )
        
        self.learning_system.record_negotiation(history)
    
    def _calculate_deal_importance(
        self,
        request: Request,
        buyer_profile: Optional[any],
        competitive_intel: Optional[CompetitiveIntelligence],
    ) -> float:
        """Calculate importance of deal (0.0-1.0)."""
        importance = 0.5
        
        # Large deal size
        if request.budget_max and request.budget_max > 100000:
            importance += 0.2
        
        # High-value buyer
        if buyer_profile and buyer_profile.relationship_value > 500000:
            importance += 0.2
        
        # High competitive pressure
        if competitive_intel and competitive_intel.competitive_pressure > 0.7:
            importance += 0.1
        
        # Multi-buyer context
        if self.constraint_manager and self.constraint_manager.multi_buyer_context:
            context = self.constraint_manager.multi_buyer_context
            if context.quota_attainment < 0.8:
                importance += 0.15
        
        return min(1.0, importance)
    
    def _estimate_buyer_aggressiveness(
        self,
        buyer_offer: OfferComponents,
        state: VendorNegotiationState,
    ) -> float:
        """Estimate buyer aggressiveness (0.0-1.0)."""
        # Compare offer to floor
        if state.floor_price:
            gap_to_floor = (buyer_offer.unit_price - state.floor_price) / state.floor_price
            
            if gap_to_floor < 0.05:
                return 0.9  # Very aggressive
            elif gap_to_floor < 0.15:
                return 0.7  # Aggressive
            elif gap_to_floor < 0.25:
                return 0.5  # Moderate
            else:
                return 0.3  # Conservative
        
        return 0.5
    
    def _apply_constraints(
        self,
        offer: OfferComponents,
        request: Request,
    ) -> OfferComponents:
        """Apply inventory and capacity constraints."""
        if not self.constraint_manager:
            return offer
        
        # Adjust price for constraints
        adjusted_price = self.constraint_manager.adjust_price_for_constraints(
            offer.unit_price,
            request.product_id or "default",
            offer.quantity,
        )
        
        # Check inventory/capacity
        # (In real implementation, would adjust quantity/delivery based on constraints)
        
        return OfferComponents(
            unit_price=adjusted_price,
            quantity=offer.quantity,
            term_months=offer.term_months,
            payment_terms=offer.payment_terms,
            delivery_days=offer.delivery_days,
        )
    
    def _apply_competitive_intelligence(
        self,
        offer: OfferComponents,
        competitive_intel: CompetitiveIntelligence,
        category: str,
    ) -> OfferComponents:
        """Apply competitive intelligence to offer."""
        if not self.competitive_intelligence:
            return offer
        
        # Get competitive strategy
        strategy = self.competitive_intelligence.get_competitive_strategy(
            competitive_intel,
            offer.unit_price,
            category,
        )
        
        # Apply price adjustment
        adjusted_price = offer.unit_price * strategy["price_adjustment"]
        
        return OfferComponents(
            unit_price=adjusted_price,
            quantity=offer.quantity,
            term_months=offer.term_months,
            payment_terms=offer.payment_terms,
            delivery_days=offer.delivery_days,
        )
    
    def get_negotiation_insights(
        self,
        buyer_organization: str,
        category: str,
    ) -> dict:
        """Get insights for negotiation planning."""
        insights = {
            "buyer_behavior": {},
            "category_trends": {},
            "competitive_landscape": {},
            "recommended_approach": "balanced",
        }
        
        # Buyer insights
        if self.learning_system:
            buyer_prediction = self.learning_system.predict_buyer_behavior(
                buyer_organization
            )
            insights["buyer_behavior"] = buyer_prediction
            
            # Category insights
            competitive_intel = self.learning_system.get_competitive_intelligence(
                category,
                datetime.now().month,
            )
            insights["category_trends"] = competitive_intel
            insights["recommended_approach"] = competitive_intel.get("recommended_strategy", "balanced")
        
        # Competitive insights
        if self.competitive_intelligence:
            loss_analysis = self.competitive_intelligence.get_loss_analysis(category)
            insights["competitive_landscape"] = loss_analysis
        
        return insights
