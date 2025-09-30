"""Competitive intelligence system for seller agents."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


class CompetitorTier(Enum):
    """Competitor tier classification."""
    PREMIUM = "premium"  # High-end, expensive
    MAINSTREAM = "mainstream"  # Mid-market
    VALUE = "value"  # Budget-friendly
    NICHE = "niche"  # Specialized


@dataclass
class CompetitorProfile:
    """Profile of a competitor."""
    competitor_id: str
    name: str
    tier: CompetitorTier
    market_share: float  # 0.0-1.0
    avg_price_point: float
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    typical_discount: float = 0.10
    win_rate_against: float = 0.5  # Our win rate when competing
    
    def get_competitive_position(self, our_price: float) -> str:
        """Determine our competitive position."""
        price_ratio = our_price / self.avg_price_point
        
        if price_ratio < 0.9:
            return "undercutting"
        elif price_ratio < 1.1:
            return "competitive"
        else:
            return "premium"


@dataclass
class CompetitiveIntelligence:
    """Competitive intelligence for a deal."""
    competitors_involved: List[str]
    estimated_competitor_prices: Dict[str, float]
    buyer_preference: Optional[str]  # Preferred competitor
    decision_criteria: List[str]  # What buyer cares about
    competitive_pressure: float  # 0.0-1.0
    
    def get_lowest_competitor_price(self) -> Optional[float]:
        """Get lowest competitor price."""
        if not self.estimated_competitor_prices:
            return None
        return min(self.estimated_competitor_prices.values())
    
    def get_price_to_beat(self) -> Optional[float]:
        """Get price we need to beat."""
        lowest = self.get_lowest_competitor_price()
        if lowest:
            return lowest * 0.98  # Beat by 2%
        return None


@dataclass
class MarketIntelligence:
    """Market-level intelligence."""
    category: str
    market_growth_rate: float  # Annual growth rate
    avg_deal_size: float
    avg_sales_cycle_days: int
    competitive_intensity: float  # 0.0-1.0
    price_sensitivity: float  # 0.0-1.0
    innovation_rate: float  # 0.0-1.0
    consolidation_trend: float  # 0.0-1.0


class CompetitiveIntelligenceSystem:
    """System for managing competitive intelligence."""
    
    def __init__(self):
        """Initialize competitive intelligence system."""
        self.competitor_profiles: Dict[str, CompetitorProfile] = {}
        self.market_intelligence: Dict[str, MarketIntelligence] = {}
        self.recent_losses: List[Dict] = []  # Track lost deals
    
    def add_competitor(self, profile: CompetitorProfile):
        """Add competitor profile."""
        self.competitor_profiles[profile.competitor_id] = profile
    
    def add_market_intelligence(self, intelligence: MarketIntelligence):
        """Add market intelligence."""
        self.market_intelligence[intelligence.category] = intelligence
    
    def record_loss(
        self,
        competitor_id: str,
        deal_value: float,
        reason: str,
        price_gap: float,
    ):
        """Record a lost deal."""
        self.recent_losses.append({
            "competitor_id": competitor_id,
            "deal_value": deal_value,
            "reason": reason,
            "price_gap": price_gap,
            "timestamp": datetime.now(),
        })
        
        # Update competitor win rate
        if competitor_id in self.competitor_profiles:
            profile = self.competitor_profiles[competitor_id]
            # Decay old win rate and incorporate loss
            profile.win_rate_against = profile.win_rate_against * 0.9
    
    def record_win(
        self,
        competitor_id: str,
        deal_value: float,
        price_advantage: float,
    ):
        """Record a won deal."""
        if competitor_id in self.competitor_profiles:
            profile = self.competitor_profiles[competitor_id]
            # Decay old win rate and incorporate win
            profile.win_rate_against = profile.win_rate_against * 0.9 + 0.1
    
    def get_competitive_strategy(
        self,
        intelligence: CompetitiveIntelligence,
        our_price: float,
        category: str,
    ) -> Dict[str, any]:
        """Get recommended competitive strategy."""
        strategy = {
            "approach": "balanced",
            "price_adjustment": 1.0,
            "emphasis": [],
            "talking_points": [],
        }
        
        # Analyze competitors
        if intelligence.competitors_involved:
            competitor_tiers = []
            for comp_id in intelligence.competitors_involved:
                if comp_id in self.competitor_profiles:
                    competitor_tiers.append(
                        self.competitor_profiles[comp_id].tier
                    )
            
            # Against premium competitors
            if CompetitorTier.PREMIUM in competitor_tiers:
                strategy["approach"] = "value"
                strategy["emphasis"].append("roi")
                strategy["emphasis"].append("cost_effectiveness")
                strategy["talking_points"].append(
                    "Comparable features at better value"
                )
            
            # Against value competitors
            elif CompetitorTier.VALUE in competitor_tiers:
                strategy["approach"] = "differentiation"
                strategy["emphasis"].append("quality")
                strategy["emphasis"].append("support")
                strategy["talking_points"].append(
                    "Superior quality and support justify premium"
                )
            
            # Against mainstream competitors
            else:
                strategy["approach"] = "competitive"
                strategy["emphasis"].append("features")
                strategy["emphasis"].append("reliability")
        
        # Price positioning
        lowest_price = intelligence.get_lowest_competitor_price()
        if lowest_price:
            price_ratio = our_price / lowest_price
            
            if price_ratio > 1.2:
                # We're significantly more expensive
                strategy["price_adjustment"] = 0.95
                strategy["talking_points"].append(
                    "Premium pricing reflects superior value"
                )
            elif price_ratio < 0.9:
                # We're significantly cheaper
                strategy["talking_points"].append(
                    "Best value in market without compromising quality"
                )
        
        # High competitive pressure
        if intelligence.competitive_pressure > 0.7:
            strategy["approach"] = "aggressive"
            strategy["price_adjustment"] = 0.93
            strategy["emphasis"].append("urgency")
        
        # Market intelligence
        if category in self.market_intelligence:
            market = self.market_intelligence[category]
            
            # High price sensitivity
            if market.price_sensitivity > 0.7:
                strategy["price_adjustment"] *= 0.97
                strategy["emphasis"].append("value")
            
            # Low competitive intensity
            if market.competitive_intensity < 0.4:
                strategy["price_adjustment"] *= 1.03
                strategy["emphasis"].append("quality")
        
        return strategy
    
    def estimate_win_probability(
        self,
        intelligence: CompetitiveIntelligence,
        our_price: float,
        our_strengths: List[str],
    ) -> float:
        """Estimate probability of winning (0.0-1.0)."""
        base_probability = 0.5
        
        # Price competitiveness
        lowest_price = intelligence.get_lowest_competitor_price()
        if lowest_price:
            price_ratio = our_price / lowest_price
            
            if price_ratio < 0.95:
                base_probability += 0.2  # Significantly cheaper
            elif price_ratio < 1.05:
                base_probability += 0.1  # Competitive
            elif price_ratio > 1.2:
                base_probability -= 0.2  # Significantly more expensive
        
        # Historical win rate against competitors
        if intelligence.competitors_involved:
            win_rates = []
            for comp_id in intelligence.competitors_involved:
                if comp_id in self.competitor_profiles:
                    win_rates.append(
                        self.competitor_profiles[comp_id].win_rate_against
                    )
            
            if win_rates:
                avg_win_rate = sum(win_rates) / len(win_rates)
                base_probability = base_probability * 0.6 + avg_win_rate * 0.4
        
        # Alignment with decision criteria
        if intelligence.decision_criteria:
            aligned_criteria = sum(
                1 for criterion in intelligence.decision_criteria
                if criterion.lower() in [s.lower() for s in our_strengths]
            )
            alignment_score = aligned_criteria / len(intelligence.decision_criteria)
            base_probability += alignment_score * 0.15
        
        # Buyer preference
        if intelligence.buyer_preference:
            if intelligence.buyer_preference == "us":
                base_probability += 0.15
            else:
                base_probability -= 0.1
        
        # Competitive pressure
        base_probability -= intelligence.competitive_pressure * 0.1
        
        # Clamp to 0-1
        return max(0.0, min(1.0, base_probability))
    
    def get_loss_analysis(self, category: Optional[str] = None) -> Dict[str, any]:
        """Analyze recent losses."""
        relevant_losses = self.recent_losses
        
        if category:
            # Filter by category if available
            pass
        
        if not relevant_losses:
            return {
                "total_losses": 0,
                "avg_price_gap": 0.0,
                "top_reasons": [],
                "top_competitors": [],
            }
        
        # Analyze reasons
        reason_counts = {}
        for loss in relevant_losses:
            reason = loss["reason"]
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
        
        top_reasons = sorted(
            reason_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        # Analyze competitors
        competitor_counts = {}
        for loss in relevant_losses:
            comp_id = loss["competitor_id"]
            competitor_counts[comp_id] = competitor_counts.get(comp_id, 0) + 1
        
        top_competitors = sorted(
            competitor_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        # Average price gap
        avg_price_gap = sum(loss["price_gap"] for loss in relevant_losses) / len(relevant_losses)
        
        return {
            "total_losses": len(relevant_losses),
            "avg_price_gap": avg_price_gap,
            "top_reasons": [r[0] for r in top_reasons],
            "top_competitors": [c[0] for c in top_competitors],
        }
