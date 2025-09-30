"""Historical learning system for seller agents."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from statistics import mean, stdev


@dataclass
class NegotiationHistory:
    """Historical negotiation record."""
    negotiation_id: str
    buyer_organization: str
    category: str
    initial_ask: float
    final_price: float
    rounds: int
    outcome: str  # won, lost, abandoned
    duration_hours: float
    concession_percentage: float
    buyer_aggressiveness: float  # 0.0-1.0
    timestamp: datetime


@dataclass
class BuyerProfile:
    """Learned profile of a buyer organization."""
    organization_id: str
    negotiations_count: int = 0
    win_rate: float = 0.0
    avg_discount_given: float = 0.0
    avg_rounds: float = 0.0
    avg_duration_hours: float = 0.0
    aggressiveness_score: float = 0.5
    price_sensitivity: float = 0.5
    relationship_value: float = 0.0  # Lifetime value
    last_negotiation: Optional[datetime] = None
    preferred_terms: Dict[str, any] = field(default_factory=dict)


@dataclass
class CategoryInsights:
    """Learned insights for a product category."""
    category: str
    negotiations_count: int = 0
    avg_discount: float = 0.0
    avg_rounds: float = 0.0
    win_rate: float = 0.0
    competitive_intensity: float = 0.5
    price_elasticity: float = 0.5
    seasonal_patterns: Dict[int, float] = field(default_factory=dict)  # month -> multiplier


class SellerLearningSystem:
    """Learning system for seller agents."""
    
    def __init__(self):
        """Initialize learning system."""
        self.negotiation_history: List[NegotiationHistory] = []
        self.buyer_profiles: Dict[str, BuyerProfile] = {}
        self.category_insights: Dict[str, CategoryInsights] = {}
    
    def record_negotiation(self, history: NegotiationHistory):
        """Record a completed negotiation."""
        self.negotiation_history.append(history)
        
        # Update buyer profile
        self._update_buyer_profile(history)
        
        # Update category insights
        self._update_category_insights(history)
    
    def _update_buyer_profile(self, history: NegotiationHistory):
        """Update buyer organization profile."""
        org_id = history.buyer_organization
        
        if org_id not in self.buyer_profiles:
            self.buyer_profiles[org_id] = BuyerProfile(organization_id=org_id)
        
        profile = self.buyer_profiles[org_id]
        
        # Update counts
        profile.negotiations_count += 1
        
        # Update win rate
        if history.outcome == "won":
            profile.win_rate = (
                (profile.win_rate * (profile.negotiations_count - 1) + 1.0) /
                profile.negotiations_count
            )
        else:
            profile.win_rate = (
                (profile.win_rate * (profile.negotiations_count - 1)) /
                profile.negotiations_count
            )
        
        # Update averages
        profile.avg_discount_given = (
            (profile.avg_discount_given * (profile.negotiations_count - 1) +
             history.concession_percentage) /
            profile.negotiations_count
        )
        
        profile.avg_rounds = (
            (profile.avg_rounds * (profile.negotiations_count - 1) + history.rounds) /
            profile.negotiations_count
        )
        
        profile.avg_duration_hours = (
            (profile.avg_duration_hours * (profile.negotiations_count - 1) +
             history.duration_hours) /
            profile.negotiations_count
        )
        
        # Update aggressiveness
        profile.aggressiveness_score = (
            (profile.aggressiveness_score * (profile.negotiations_count - 1) +
             history.buyer_aggressiveness) /
            profile.negotiations_count
        )
        
        # Calculate price sensitivity
        if history.outcome == "won":
            # Lower concession = higher sensitivity
            profile.price_sensitivity = history.concession_percentage / 100.0
        
        # Update relationship value (cumulative revenue)
        if history.outcome == "won":
            profile.relationship_value += history.final_price
        
        profile.last_negotiation = history.timestamp
    
    def _update_category_insights(self, history: NegotiationHistory):
        """Update category-specific insights."""
        category = history.category
        
        if category not in self.category_insights:
            self.category_insights[category] = CategoryInsights(category=category)
        
        insights = self.category_insights[category]
        
        # Update counts
        insights.negotiations_count += 1
        
        # Update averages
        insights.avg_discount = (
            (insights.avg_discount * (insights.negotiations_count - 1) +
             history.concession_percentage) /
            insights.negotiations_count
        )
        
        insights.avg_rounds = (
            (insights.avg_rounds * (insights.negotiations_count - 1) + history.rounds) /
            insights.negotiations_count
        )
        
        # Update win rate
        if history.outcome == "won":
            insights.win_rate = (
                (insights.win_rate * (insights.negotiations_count - 1) + 1.0) /
                insights.negotiations_count
            )
        else:
            insights.win_rate = (
                (insights.win_rate * (insights.negotiations_count - 1)) /
                insights.negotiations_count
            )
        
        # Update seasonal patterns
        month = history.timestamp.month
        if month not in insights.seasonal_patterns:
            insights.seasonal_patterns[month] = 1.0
        
        # Adjust seasonal multiplier based on outcomes
        if history.outcome == "won":
            insights.seasonal_patterns[month] = (
                insights.seasonal_patterns[month] * 0.9 + 1.1 * 0.1
            )
        else:
            insights.seasonal_patterns[month] = (
                insights.seasonal_patterns[month] * 0.9 + 0.9 * 0.1
            )
    
    def get_buyer_profile(self, organization_id: str) -> Optional[BuyerProfile]:
        """Get learned profile for buyer organization."""
        return self.buyer_profiles.get(organization_id)
    
    def get_category_insights(self, category: str) -> Optional[CategoryInsights]:
        """Get insights for category."""
        return self.category_insights.get(category)
    
    def get_recommended_floor(
        self,
        base_floor: float,
        buyer_organization: str,
        category: str,
    ) -> float:
        """Get recommended price floor based on learning."""
        adjustments = []
        
        # Buyer-specific adjustment
        buyer_profile = self.get_buyer_profile(buyer_organization)
        if buyer_profile and buyer_profile.negotiations_count >= 3:
            # High-value buyers get better pricing
            if buyer_profile.relationship_value > 100000:
                adjustments.append(0.95)  # 5% discount
            
            # Frequent buyers get loyalty discount
            if buyer_profile.negotiations_count > 10:
                adjustments.append(0.97)  # 3% discount
        
        # Category-specific adjustment
        category_insights = self.get_category_insights(category)
        if category_insights and category_insights.negotiations_count >= 5:
            # High competition = lower floor
            if category_insights.competitive_intensity > 0.7:
                adjustments.append(0.95)
            
            # Low win rate = lower floor
            if category_insights.win_rate < 0.4:
                adjustments.append(0.93)
        
        # Apply adjustments
        adjusted_floor = base_floor
        for adj in adjustments:
            adjusted_floor *= adj
        
        return adjusted_floor
    
    def predict_buyer_behavior(
        self,
        buyer_organization: str,
    ) -> Dict[str, float]:
        """Predict buyer negotiation behavior."""
        profile = self.get_buyer_profile(buyer_organization)
        
        if not profile or profile.negotiations_count < 2:
            # Default predictions for unknown buyers
            return {
                "expected_rounds": 3.0,
                "expected_discount": 0.10,
                "aggressiveness": 0.5,
                "price_sensitivity": 0.5,
                "win_probability": 0.5,
            }
        
        return {
            "expected_rounds": profile.avg_rounds,
            "expected_discount": profile.avg_discount_given / 100.0,
            "aggressiveness": profile.aggressiveness_score,
            "price_sensitivity": profile.price_sensitivity,
            "win_probability": profile.win_rate,
        }
    
    def get_competitive_intelligence(
        self,
        category: str,
        current_month: int,
    ) -> Dict[str, any]:
        """Get competitive intelligence for category."""
        insights = self.get_category_insights(category)
        
        if not insights or insights.negotiations_count < 5:
            return {
                "avg_discount": 0.10,
                "competitive_intensity": 0.5,
                "seasonal_multiplier": 1.0,
                "recommended_strategy": "balanced",
            }
        
        seasonal_multiplier = insights.seasonal_patterns.get(current_month, 1.0)
        
        # Determine recommended strategy
        if insights.competitive_intensity > 0.7:
            strategy = "aggressive"
        elif insights.win_rate > 0.7:
            strategy = "premium"
        else:
            strategy = "balanced"
        
        return {
            "avg_discount": insights.avg_discount / 100.0,
            "competitive_intensity": insights.competitive_intensity,
            "seasonal_multiplier": seasonal_multiplier,
            "recommended_strategy": strategy,
            "win_rate": insights.win_rate,
        }
