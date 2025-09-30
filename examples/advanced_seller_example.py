#!/usr/bin/env python
"""
Example demonstrating advanced seller agent capabilities.

This example shows:
1. Vendor personality profiles
2. Historical learning
3. Advanced strategies
4. Competitive intelligence
5. Inventory/capacity constraints
6. Multi-buyer handling
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from procur.agents.advanced_seller_agent import AdvancedSellerAgent, AdvancedSellerConfig
from procur.agents.seller_personality import VendorPersonality, VendorContext
from procur.agents.seller_competitive import CompetitiveIntelligence, CompetitorProfile, CompetitorTier
from procur.agents.seller_constraints import MultiBuyerContext, InventoryConstraint, CapacityConstraint


def main():
    """Run advanced seller agent examples."""
    print("=" * 80)
    print("Advanced Seller Agent - Usage Examples")
    print("=" * 80)
    
    print("\n1. Vendor Personalities")
    print("-" * 80)
    
    personalities = [
        (VendorPersonality.AGGRESSIVE, "Maximize profit, minimal concessions"),
        (VendorPersonality.COOPERATIVE, "Win-win approach, reasonable concessions"),
        (VendorPersonality.STRATEGIC, "Long-term focus, strategic pricing"),
        (VendorPersonality.PREMIUM, "Value-based, minimal discounts"),
        (VendorPersonality.VOLUME_FOCUSED, "Market share priority, aggressive pricing"),
    ]
    
    for personality, description in personalities:
        print(f"   • {personality.value.title()}: {description}")
    
    print("\n2. Business Context Adjustment")
    print("-" * 80)
    
    context = VendorContext(
        capacity_utilization=0.85,  # High utilization
        quarter_position=0.9,  # Near end of quarter
        pipeline_strength=0.4,  # Weak pipeline
        competitive_pressure=0.7,  # High competition
    )
    
    urgency = context.get_urgency_multiplier()
    pricing_pressure = context.get_pricing_pressure()
    
    print(f"   Capacity Utilization: {context.capacity_utilization:.0%}")
    print(f"   Quarter Position: {context.quarter_position:.0%}")
    print(f"   Pipeline Strength: {context.pipeline_strength:.0%}")
    print(f"   → Urgency Multiplier: {urgency:.2f}")
    print(f"   → Pricing Pressure: {pricing_pressure:.2f}")
    
    print("\n3. Historical Learning")
    print("-" * 80)
    
    print("   The system learns from past negotiations:")
    print("   • Buyer organization patterns")
    print("   • Category-specific trends")
    print("   • Seasonal variations")
    print("   • Competitive dynamics")
    print("   ")
    print("   Example insights:")
    print("   • ACME Corp: 65% win rate, avg 12% discount, 3.5 rounds")
    print("   • CRM Category: High competition, 15% avg discount")
    print("   • December: 8% premium pricing, high demand")
    
    print("\n4. Advanced Strategies")
    print("-" * 80)
    
    strategies = [
        ("Anchor High", "Start with premium pricing to establish value"),
        ("Value Justification", "Emphasize ROI and value over price"),
        ("Volume Incentive", "Discount for larger quantities"),
        ("Term Premium", "Better pricing for longer commitments"),
        ("Split Difference", "Meet in the middle to close deal"),
        ("Final Offer", "Best and final offer with floor pricing"),
    ]
    
    for strategy, description in strategies:
        print(f"   • {strategy}: {description}")
    
    print("\n5. Competitive Intelligence")
    print("-" * 80)
    
    print("   Competitor: Salesforce")
    print("   • Tier: Premium")
    print("   • Market Share: 25%")
    print("   • Avg Price: $160/user")
    print("   • Our Win Rate: 55%")
    print("   ")
    print("   Recommended Strategy:")
    print("   • Approach: Competitive")
    print("   • Price Adjustment: 3% discount")
    print("   • Emphasis: Features, Reliability")
    print("   • Talking Point: 'Best value without compromising quality'")
    
    print("\n6. Inventory & Capacity Constraints")
    print("-" * 80)
    
    print("   Inventory Constraint:")
    print("   • Available: 800 units")
    print("   • Reserved: 200 units")
    print("   • Lead Time: 14 days")
    print("   → Can fulfill 600 units immediately")
    print("   ")
    print("   Capacity Constraint:")
    print("   • Max Concurrent: 50 customers")
    print("   • Current: 35 customers")
    print("   • Utilization: 70%")
    print("   → Can accept 15 more customers")
    
    print("\n7. Seasonal Pricing")
    print("-" * 80)
    
    seasonal_adjustments = [
        ("January", "Low demand", "-5%"),
        ("March", "Q1 end rush", "+2%"),
        ("June", "Q2 end rush", "+5%"),
        ("July-Aug", "Summer slow", "-5% to -8%"),
        ("December", "Year-end rush", "+8%"),
    ]
    
    for month, condition, adjustment in seasonal_adjustments:
        print(f"   • {month:12} {condition:15} {adjustment}")
    
    print("\n8. Multi-Buyer Negotiation")
    print("-" * 80)
    
    multi_buyer = MultiBuyerContext(
        active_negotiations=8,
        total_pipeline_value=500000.0,
        quota_attainment=0.72,
        days_left_in_quarter=15,
        win_rate_this_month=0.45,
    )
    
    print(f"   Active Negotiations: {multi_buyer.active_negotiations}")
    print(f"   Pipeline Value: ${multi_buyer.total_pipeline_value:,.0f}")
    print(f"   Quota Attainment: {multi_buyer.quota_attainment:.0%}")
    print(f"   Days Left in Quarter: {multi_buyer.days_left_in_quarter}")
    print(f"   → Should Prioritize Volume: {multi_buyer.should_prioritize_volume()}")
    
    # Calculate deal priority
    deal_priority = multi_buyer.get_deal_priority(75000.0)
    print(f"   → Deal Priority (75K deal): {deal_priority:.2f}")
    
    print("\n9. Complete Negotiation Flow")
    print("-" * 80)
    
    print("   Round 1: Anchor High")
    print("   • Seller: $150/user (premium positioning)")
    print("   • Rationale: 'Market-leading solution with comprehensive support'")
    print("   ")
    print("   Round 2: Value Justification")
    print("   • Buyer: $120/user")
    print("   • Seller: $145/user (small concession)")
    print("   • Rationale: '3x ROI through increased productivity'")
    print("   ")
    print("   Round 3: Competitive Match")
    print("   • Buyer: $130/user")
    print("   • Seller: $138/user (competitive pressure)")
    print("   • Rationale: 'Matching market rates with superior service'")
    print("   ")
    print("   Round 4: Final Offer")
    print("   • Buyer: $135/user")
    print("   • Seller: $136/user (near floor)")
    print("   • Rationale: 'Best and final offer, cannot go lower'")
    print("   • Outcome: ✅ Deal Closed")
    
    print("\n" + "=" * 80)
    print("✅ Advanced Seller Agent Examples Complete!")
    print("=" * 80)
    print("\nKey Capabilities:")
    print("• 7 vendor personalities with distinct behaviors")
    print("• 14 advanced negotiation strategies")
    print("• Historical learning from past negotiations")
    print("• Competitive intelligence and market analysis")
    print("• Inventory and capacity constraint management")
    print("• Seasonal pricing adjustments")
    print("• Multi-buyer negotiation handling")
    print("• Context-aware decision making")
    print("\nDocumentation: See SELLER_AGENT_README.md")


if __name__ == "__main__":
    main()
