"""Vendor personality profiles for seller agents."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


class VendorPersonality(Enum):
    """Vendor personality types."""
    AGGRESSIVE = "aggressive"  # Maximize profit, minimal concessions
    COOPERATIVE = "cooperative"  # Win-win, reasonable concessions
    STRATEGIC = "strategic"  # Long-term relationships, strategic pricing
    OPPORTUNISTIC = "opportunistic"  # Market-driven, flexible
    PREMIUM = "premium"  # Value-based, minimal discounts
    VOLUME_FOCUSED = "volume_focused"  # Market share, aggressive pricing
    RELATIONSHIP = "relationship"  # Customer retention, loyalty-based


@dataclass
class PersonalityTraits:
    """Personality trait configuration."""
    
    # Concession behavior (0.0 = no concessions, 1.0 = very flexible)
    concession_willingness: float
    
    # Price floor flexibility (0.0 = rigid floor, 1.0 = flexible)
    floor_flexibility: float
    
    # Response to pressure (0.0 = resistant, 1.0 = accommodating)
    pressure_sensitivity: float
    
    # Long-term vs short-term focus (0.0 = short-term, 1.0 = long-term)
    relationship_focus: float
    
    # Competitive response (0.0 = ignore competition, 1.0 = match aggressively)
    competitive_response: float
    
    # Risk tolerance (0.0 = risk-averse, 1.0 = risk-seeking)
    risk_tolerance: float
    
    # Negotiation patience (0.0 = quick close, 1.0 = patient)
    patience: float
    
    # Value perception emphasis (0.0 = price-focused, 1.0 = value-focused)
    value_emphasis: float


# Personality trait configurations
PERSONALITY_CONFIGS: Dict[VendorPersonality, PersonalityTraits] = {
    VendorPersonality.AGGRESSIVE: PersonalityTraits(
        concession_willingness=0.2,
        floor_flexibility=0.1,
        pressure_sensitivity=0.3,
        relationship_focus=0.2,
        competitive_response=0.8,
        risk_tolerance=0.7,
        patience=0.3,
        value_emphasis=0.3,
    ),
    VendorPersonality.COOPERATIVE: PersonalityTraits(
        concession_willingness=0.7,
        floor_flexibility=0.6,
        pressure_sensitivity=0.7,
        relationship_focus=0.8,
        competitive_response=0.5,
        risk_tolerance=0.4,
        patience=0.7,
        value_emphasis=0.7,
    ),
    VendorPersonality.STRATEGIC: PersonalityTraits(
        concession_willingness=0.5,
        floor_flexibility=0.4,
        pressure_sensitivity=0.4,
        relationship_focus=0.9,
        competitive_response=0.6,
        risk_tolerance=0.5,
        patience=0.8,
        value_emphasis=0.8,
    ),
    VendorPersonality.OPPORTUNISTIC: PersonalityTraits(
        concession_willingness=0.6,
        floor_flexibility=0.7,
        pressure_sensitivity=0.6,
        relationship_focus=0.4,
        competitive_response=0.9,
        risk_tolerance=0.8,
        patience=0.4,
        value_emphasis=0.5,
    ),
    VendorPersonality.PREMIUM: PersonalityTraits(
        concession_willingness=0.3,
        floor_flexibility=0.2,
        pressure_sensitivity=0.2,
        relationship_focus=0.6,
        competitive_response=0.3,
        risk_tolerance=0.3,
        patience=0.6,
        value_emphasis=0.9,
    ),
    VendorPersonality.VOLUME_FOCUSED: PersonalityTraits(
        concession_willingness=0.8,
        floor_flexibility=0.8,
        pressure_sensitivity=0.8,
        relationship_focus=0.5,
        competitive_response=0.9,
        risk_tolerance=0.6,
        patience=0.3,
        value_emphasis=0.4,
    ),
    VendorPersonality.RELATIONSHIP: PersonalityTraits(
        concession_willingness=0.6,
        floor_flexibility=0.5,
        pressure_sensitivity=0.6,
        relationship_focus=1.0,
        competitive_response=0.4,
        risk_tolerance=0.4,
        patience=0.9,
        value_emphasis=0.8,
    ),
}


@dataclass
class VendorContext:
    """Vendor business context affecting negotiation."""
    
    # Current capacity utilization (0.0 = empty, 1.0 = full)
    capacity_utilization: float = 0.7
    
    # Inventory levels (0.0 = no inventory, 1.0 = excess)
    inventory_level: float = 0.5
    
    # Quarter position (0.0 = start, 1.0 = end)
    quarter_position: float = 0.5
    
    # Year position (0.0 = start, 1.0 = end)
    year_position: float = 0.5
    
    # Pipeline health (0.0 = weak, 1.0 = strong)
    pipeline_strength: float = 0.6
    
    # Recent win rate (0.0 = losing, 1.0 = winning)
    recent_win_rate: float = 0.5
    
    # Competitive pressure (0.0 = low, 1.0 = high)
    competitive_pressure: float = 0.5
    
    # Market demand (0.0 = low, 1.0 = high)
    market_demand: float = 0.6
    
    def get_urgency_multiplier(self) -> float:
        """Calculate urgency to close deals."""
        # End of quarter/year increases urgency
        quarter_urgency = self.quarter_position ** 2
        year_urgency = self.year_position ** 2
        
        # Low pipeline increases urgency
        pipeline_urgency = 1.0 - self.pipeline_strength
        
        # Low capacity utilization increases urgency
        capacity_urgency = 1.0 - self.capacity_utilization
        
        # Combine factors
        urgency = (
            quarter_urgency * 0.3 +
            year_urgency * 0.2 +
            pipeline_urgency * 0.3 +
            capacity_urgency * 0.2
        )
        
        return urgency
    
    def get_pricing_pressure(self) -> float:
        """Calculate downward pricing pressure."""
        # High inventory creates pressure
        inventory_pressure = self.inventory_level
        
        # Low demand creates pressure
        demand_pressure = 1.0 - self.market_demand
        
        # High competition creates pressure
        competitive_pressure = self.competitive_pressure
        
        # Low win rate creates pressure
        win_rate_pressure = 1.0 - self.recent_win_rate
        
        # Combine factors
        pressure = (
            inventory_pressure * 0.25 +
            demand_pressure * 0.3 +
            competitive_pressure * 0.3 +
            win_rate_pressure * 0.15
        )
        
        return pressure


def get_personality_traits(personality: VendorPersonality) -> PersonalityTraits:
    """Get personality traits for vendor type."""
    return PERSONALITY_CONFIGS[personality]


def adjust_traits_for_context(
    base_traits: PersonalityTraits,
    context: VendorContext,
) -> PersonalityTraits:
    """Adjust personality traits based on business context."""
    urgency = context.get_urgency_multiplier()
    pricing_pressure = context.get_pricing_pressure()
    
    # Create adjusted traits
    adjusted = PersonalityTraits(
        concession_willingness=min(1.0, base_traits.concession_willingness + urgency * 0.3 + pricing_pressure * 0.2),
        floor_flexibility=min(1.0, base_traits.floor_flexibility + pricing_pressure * 0.3),
        pressure_sensitivity=min(1.0, base_traits.pressure_sensitivity + urgency * 0.2),
        relationship_focus=base_traits.relationship_focus,
        competitive_response=min(1.0, base_traits.competitive_response + context.competitive_pressure * 0.2),
        risk_tolerance=min(1.0, base_traits.risk_tolerance + urgency * 0.15),
        patience=max(0.0, base_traits.patience - urgency * 0.3),
        value_emphasis=base_traits.value_emphasis,
    )
    
    return adjusted
