"""Advanced seller negotiation strategies."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

from ..models import OfferComponents
from ..services.negotiation_engine import VendorNegotiationState
from .seller_personality import PersonalityTraits, VendorContext
from .seller_learning import BuyerProfile, CategoryInsights


class AdvancedSellerStrategy(Enum):
    """Advanced seller strategies."""
    ANCHOR_HIGH = "anchor_high"  # Start with premium pricing
    VALUE_JUSTIFICATION = "value_justification"  # Emphasize value over price
    COMPETITIVE_MATCH = "competitive_match"  # Match competitor pricing
    VOLUME_INCENTIVE = "volume_incentive"  # Discount for larger quantities
    TERM_PREMIUM = "term_premium"  # Better pricing for longer terms
    RELATIONSHIP_INVESTMENT = "relationship_investment"  # Invest in long-term customer
    SCARCITY_LEVERAGE = "scarcity_leverage"  # Limited availability
    BUNDLE_UPSELL = "bundle_upsell"  # Add value through bundling
    GRADUAL_CONCESSION = "gradual_concession"  # Small incremental concessions
    FINAL_OFFER = "final_offer"  # Best and final offer
    WALK_AWAY = "walk_away"  # Reject and end negotiation
    HOLD_FIRM = "hold_firm"  # No movement on price
    SPLIT_DIFFERENCE = "split_difference"  # Meet in the middle
    CONDITIONAL_DISCOUNT = "conditional_discount"  # Discount with conditions


@dataclass
class StrategyContext:
    """Context for strategy selection."""
    round_number: int
    total_rounds_expected: int
    buyer_aggressiveness: float
    price_gap_percentage: float
    buyer_profile: Optional[BuyerProfile]
    category_insights: Optional[CategoryInsights]
    personality_traits: PersonalityTraits
    vendor_context: VendorContext
    competitive_pressure: float
    deal_importance: float  # 0.0-1.0


class SellerStrategyEngine:
    """Engine for selecting and executing seller strategies."""
    
    def __init__(self):
        """Initialize strategy engine."""
        pass
    
    def select_strategy(
        self,
        context: StrategyContext,
        state: VendorNegotiationState,
        buyer_offer: OfferComponents,
    ) -> AdvancedSellerStrategy:
        """Select optimal strategy based on context."""
        traits = context.personality_traits
        
        # Early rounds: Establish position
        if context.round_number <= 2:
            if traits.value_emphasis > 0.7:
                return AdvancedSellerStrategy.VALUE_JUSTIFICATION
            elif traits.competitive_response > 0.7:
                return AdvancedSellerStrategy.COMPETITIVE_MATCH
            else:
                return AdvancedSellerStrategy.ANCHOR_HIGH
        
        # Mid rounds: Negotiate
        elif context.round_number <= context.total_rounds_expected - 2:
            # High competitive pressure
            if context.competitive_pressure > 0.7:
                if traits.concession_willingness > 0.6:
                    return AdvancedSellerStrategy.VOLUME_INCENTIVE
                else:
                    return AdvancedSellerStrategy.COMPETITIVE_MATCH
            
            # High price gap
            if context.price_gap_percentage > 20:
                if traits.relationship_focus > 0.7:
                    return AdvancedSellerStrategy.RELATIONSHIP_INVESTMENT
                elif traits.value_emphasis > 0.6:
                    return AdvancedSellerStrategy.VALUE_JUSTIFICATION
                else:
                    return AdvancedSellerStrategy.GRADUAL_CONCESSION
            
            # Moderate gap
            else:
                if traits.concession_willingness > 0.6:
                    return AdvancedSellerStrategy.SPLIT_DIFFERENCE
                else:
                    return AdvancedSellerStrategy.CONDITIONAL_DISCOUNT
        
        # Late rounds: Close or walk
        else:
            # Small gap - close the deal
            if context.price_gap_percentage < 10:
                if context.deal_importance > 0.7:
                    return AdvancedSellerStrategy.SPLIT_DIFFERENCE
                else:
                    return AdvancedSellerStrategy.FINAL_OFFER
            
            # Large gap - firm or walk
            else:
                if context.price_gap_percentage > 30:
                    if traits.patience < 0.3:
                        return AdvancedSellerStrategy.WALK_AWAY
                    else:
                        return AdvancedSellerStrategy.HOLD_FIRM
                else:
                    if traits.concession_willingness > 0.5:
                        return AdvancedSellerStrategy.FINAL_OFFER
                    else:
                        return AdvancedSellerStrategy.HOLD_FIRM
    
    def execute_strategy(
        self,
        strategy: AdvancedSellerStrategy,
        current_offer: OfferComponents,
        buyer_offer: OfferComponents,
        state: VendorNegotiationState,
        context: StrategyContext,
    ) -> Tuple[OfferComponents, str]:
        """Execute selected strategy and return counter-offer."""
        
        if strategy == AdvancedSellerStrategy.ANCHOR_HIGH:
            return self._anchor_high(current_offer, state, context)
        
        elif strategy == AdvancedSellerStrategy.VALUE_JUSTIFICATION:
            return self._value_justification(current_offer, buyer_offer, state, context)
        
        elif strategy == AdvancedSellerStrategy.COMPETITIVE_MATCH:
            return self._competitive_match(current_offer, buyer_offer, state, context)
        
        elif strategy == AdvancedSellerStrategy.VOLUME_INCENTIVE:
            return self._volume_incentive(current_offer, buyer_offer, state, context)
        
        elif strategy == AdvancedSellerStrategy.TERM_PREMIUM:
            return self._term_premium(current_offer, buyer_offer, state, context)
        
        elif strategy == AdvancedSellerStrategy.RELATIONSHIP_INVESTMENT:
            return self._relationship_investment(current_offer, buyer_offer, state, context)
        
        elif strategy == AdvancedSellerStrategy.GRADUAL_CONCESSION:
            return self._gradual_concession(current_offer, buyer_offer, state, context)
        
        elif strategy == AdvancedSellerStrategy.SPLIT_DIFFERENCE:
            return self._split_difference(current_offer, buyer_offer, state, context)
        
        elif strategy == AdvancedSellerStrategy.FINAL_OFFER:
            return self._final_offer(current_offer, buyer_offer, state, context)
        
        elif strategy == AdvancedSellerStrategy.HOLD_FIRM:
            return self._hold_firm(current_offer, state, context)
        
        elif strategy == AdvancedSellerStrategy.CONDITIONAL_DISCOUNT:
            return self._conditional_discount(current_offer, buyer_offer, state, context)
        
        else:
            # Default: gradual concession
            return self._gradual_concession(current_offer, buyer_offer, state, context)
    
    def _anchor_high(
        self,
        current_offer: OfferComponents,
        state: VendorNegotiationState,
        context: StrategyContext,
    ) -> Tuple[OfferComponents, str]:
        """Anchor with premium pricing."""
        # Start at list price or slightly above
        new_offer = OfferComponents(
            unit_price=state.list_price * 1.05,
            quantity=current_offer.quantity,
            term_months=current_offer.term_months,
            payment_terms=current_offer.payment_terms,
            delivery_days=current_offer.delivery_days,
        )
        
        rationale = "Premium pricing reflects our market-leading solution and comprehensive support."
        return new_offer, rationale
    
    def _value_justification(
        self,
        current_offer: OfferComponents,
        buyer_offer: OfferComponents,
        state: VendorNegotiationState,
        context: StrategyContext,
    ) -> Tuple[OfferComponents, str]:
        """Justify value over price."""
        # Small concession with value emphasis
        price_gap = current_offer.unit_price - buyer_offer.unit_price
        concession = price_gap * 0.15  # 15% of gap
        
        new_offer = OfferComponents(
            unit_price=current_offer.unit_price - concession,
            quantity=buyer_offer.quantity,
            term_months=max(current_offer.term_months, buyer_offer.term_months),
            payment_terms=current_offer.payment_terms,
            delivery_days=min(current_offer.delivery_days, buyer_offer.delivery_days),
        )
        
        rationale = "Our solution delivers 3x ROI through increased productivity and reduced operational costs."
        return new_offer, rationale
    
    def _competitive_match(
        self,
        current_offer: OfferComponents,
        buyer_offer: OfferComponents,
        state: VendorNegotiationState,
        context: StrategyContext,
    ) -> Tuple[OfferComponents, str]:
        """Match competitive pricing."""
        # Move closer to buyer's price
        price_gap = current_offer.unit_price - buyer_offer.unit_price
        concession = price_gap * 0.4  # 40% of gap
        
        new_offer = OfferComponents(
            unit_price=current_offer.unit_price - concession,
            quantity=buyer_offer.quantity,
            term_months=buyer_offer.term_months,
            payment_terms=buyer_offer.payment_terms,
            delivery_days=buyer_offer.delivery_days,
        )
        
        rationale = "We're matching market rates while providing superior service and support."
        return new_offer, rationale
    
    def _volume_incentive(
        self,
        current_offer: OfferComponents,
        buyer_offer: OfferComponents,
        state: VendorNegotiationState,
        context: StrategyContext,
    ) -> Tuple[OfferComponents, str]:
        """Offer volume-based discount."""
        # Discount for increased quantity
        quantity_increase = max(1.2, buyer_offer.quantity / current_offer.quantity)
        discount = min(0.15, (quantity_increase - 1.0) * 0.5)  # Up to 15% discount
        
        new_offer = OfferComponents(
            unit_price=current_offer.unit_price * (1 - discount),
            quantity=int(current_offer.quantity * quantity_increase),
            term_months=buyer_offer.term_months,
            payment_terms=current_offer.payment_terms,
            delivery_days=current_offer.delivery_days,
        )
        
        rationale = f"Volume discount of {discount*100:.1f}% for {int(quantity_increase*100)}% quantity increase."
        return new_offer, rationale
    
    def _term_premium(
        self,
        current_offer: OfferComponents,
        buyer_offer: OfferComponents,
        state: VendorNegotiationState,
        context: StrategyContext,
    ) -> Tuple[OfferComponents, str]:
        """Better pricing for longer terms."""
        # Discount for longer commitment
        term_ratio = buyer_offer.term_months / max(12, current_offer.term_months)
        discount = min(0.12, (term_ratio - 1.0) * 0.08)  # Up to 12% discount
        
        new_offer = OfferComponents(
            unit_price=current_offer.unit_price * (1 - discount),
            quantity=buyer_offer.quantity,
            term_months=max(buyer_offer.term_months, 24),
            payment_terms=current_offer.payment_terms,
            delivery_days=current_offer.delivery_days,
        )
        
        rationale = f"Long-term commitment discount of {discount*100:.1f}% for {new_offer.term_months}-month term."
        return new_offer, rationale
    
    def _relationship_investment(
        self,
        current_offer: OfferComponents,
        buyer_offer: OfferComponents,
        state: VendorNegotiationState,
        context: StrategyContext,
    ) -> Tuple[OfferComponents, str]:
        """Invest in long-term relationship."""
        # Significant concession for relationship building
        price_gap = current_offer.unit_price - buyer_offer.unit_price
        concession = price_gap * 0.6  # 60% of gap
        
        new_offer = OfferComponents(
            unit_price=current_offer.unit_price - concession,
            quantity=buyer_offer.quantity,
            term_months=max(buyer_offer.term_months, 24),
            payment_terms=buyer_offer.payment_terms,
            delivery_days=buyer_offer.delivery_days,
        )
        
        rationale = "Strategic partnership pricing with dedicated account management and priority support."
        return new_offer, rationale
    
    def _gradual_concession(
        self,
        current_offer: OfferComponents,
        buyer_offer: OfferComponents,
        state: VendorNegotiationState,
        context: StrategyContext,
    ) -> Tuple[OfferComponents, str]:
        """Make small incremental concession."""
        # Small concession based on willingness
        price_gap = current_offer.unit_price - buyer_offer.unit_price
        concession_rate = context.personality_traits.concession_willingness * 0.25
        concession = price_gap * concession_rate
        
        new_offer = OfferComponents(
            unit_price=current_offer.unit_price - concession,
            quantity=buyer_offer.quantity,
            term_months=current_offer.term_months,
            payment_terms=current_offer.payment_terms,
            delivery_days=current_offer.delivery_days,
        )
        
        rationale = f"Incremental concession to move toward agreement."
        return new_offer, rationale
    
    def _split_difference(
        self,
        current_offer: OfferComponents,
        buyer_offer: OfferComponents,
        state: VendorNegotiationState,
        context: StrategyContext,
    ) -> Tuple[OfferComponents, str]:
        """Meet in the middle."""
        # Split the difference
        midpoint_price = (current_offer.unit_price + buyer_offer.unit_price) / 2
        
        new_offer = OfferComponents(
            unit_price=midpoint_price,
            quantity=buyer_offer.quantity,
            term_months=buyer_offer.term_months,
            payment_terms=buyer_offer.payment_terms,
            delivery_days=buyer_offer.delivery_days,
        )
        
        rationale = "Let's meet in the middle to close this deal."
        return new_offer, rationale
    
    def _final_offer(
        self,
        current_offer: OfferComponents,
        buyer_offer: OfferComponents,
        state: VendorNegotiationState,
        context: StrategyContext,
    ) -> Tuple[OfferComponents, str]:
        """Best and final offer."""
        # Move close to floor with final concession
        floor_price = state.floor_price
        final_price = max(floor_price * 1.02, buyer_offer.unit_price * 1.05)
        
        new_offer = OfferComponents(
            unit_price=final_price,
            quantity=buyer_offer.quantity,
            term_months=buyer_offer.term_months,
            payment_terms=buyer_offer.payment_terms,
            delivery_days=buyer_offer.delivery_days,
        )
        
        rationale = "This is our best and final offer. We cannot go lower while maintaining quality."
        return new_offer, rationale
    
    def _hold_firm(
        self,
        current_offer: OfferComponents,
        state: VendorNegotiationState,
        context: StrategyContext,
    ) -> Tuple[OfferComponents, str]:
        """Hold firm on current position."""
        rationale = "We believe our current offer represents fair market value and cannot reduce further."
        return current_offer, rationale
    
    def _conditional_discount(
        self,
        current_offer: OfferComponents,
        buyer_offer: OfferComponents,
        state: VendorNegotiationState,
        context: StrategyContext,
    ) -> Tuple[OfferComponents, str]:
        """Offer discount with conditions."""
        # Discount for favorable terms
        price_gap = current_offer.unit_price - buyer_offer.unit_price
        concession = price_gap * 0.3
        
        # Require longer term or better payment
        new_offer = OfferComponents(
            unit_price=current_offer.unit_price - concession,
            quantity=buyer_offer.quantity,
            term_months=max(buyer_offer.term_months, 24),
            payment_terms="NET15",  # Faster payment
            delivery_days=buyer_offer.delivery_days,
        )
        
        rationale = "Conditional discount for 24-month term and NET15 payment terms."
        return new_offer, rationale
