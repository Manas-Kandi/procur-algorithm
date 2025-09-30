# Advanced Seller Agent System

## Overview

Sophisticated seller agent with personality-driven behavior, historical learning, competitive intelligence, and advanced negotiation strategies matching the buyer agent's 1800+ line sophistication.

## Features

✅ **Vendor Personality Profiles** - 7 distinct personalities (aggressive, cooperative, strategic, etc.)
✅ **Historical Learning** - Learn from past negotiations to improve outcomes
✅ **Advanced Strategies** - 14 sophisticated negotiation strategies
✅ **Multi-Buyer Handling** - Manage multiple concurrent negotiations
✅ **Inventory Constraints** - Real inventory and capacity management
✅ **Seasonal Pricing** - Dynamic pricing based on time of year
✅ **Competitive Intelligence** - Track competitors and market dynamics
✅ **Context-Aware** - Adjust behavior based on business context

## Architecture

### Components

1. **Personality System** (`seller_personality.py`)
   - 7 vendor personality types
   - 8 personality traits
   - Context-based trait adjustment
   - Business context modeling

2. **Learning System** (`seller_learning.py`)
   - Historical negotiation records
   - Buyer organization profiles
   - Category insights
   - Predictive behavior modeling

3. **Strategy Engine** (`seller_strategies.py`)
   - 14 advanced strategies
   - Context-aware strategy selection
   - Strategy execution with rationale

4. **Constraint Manager** (`seller_constraints.py`)
   - Inventory constraints
   - Capacity constraints
   - Seasonal patterns
   - Multi-buyer context

5. **Competitive Intelligence** (`seller_competitive.py`)
   - Competitor profiles
   - Market intelligence
   - Win/loss analysis
   - Competitive strategy recommendations

6. **Advanced Seller Agent** (`advanced_seller_agent.py`)
   - Integrates all components
   - Sophisticated counter-offers
   - Learning and adaptation

## Vendor Personalities

### 1. Aggressive
- **Behavior**: Maximize profit, minimal concessions
- **Concession Willingness**: 20%
- **Best For**: High-demand products, premium brands

### 2. Cooperative
- **Behavior**: Win-win approach, reasonable concessions
- **Concession Willingness**: 70%
- **Best For**: Long-term relationships, partnerships

### 3. Strategic
- **Behavior**: Long-term focus, strategic pricing
- **Concession Willingness**: 50%
- **Best For**: Enterprise sales, complex deals

### 4. Opportunistic
- **Behavior**: Market-driven, flexible
- **Concession Willingness**: 60%
- **Best For**: Competitive markets, dynamic pricing

### 5. Premium
- **Behavior**: Value-based, minimal discounts
- **Concession Willingness**: 30%
- **Best For**: Luxury products, differentiated offerings

### 6. Volume-Focused
- **Behavior**: Market share priority, aggressive pricing
- **Concession Willingness**: 80%
- **Best For**: Commodity products, scale businesses

### 7. Relationship
- **Behavior**: Customer retention, loyalty-based
- **Concession Willingness**: 60%
- **Best For**: Subscription services, recurring revenue

## Advanced Strategies

### Early Round Strategies

1. **Anchor High** - Start with premium pricing
2. **Value Justification** - Emphasize value over price
3. **Competitive Match** - Match competitor pricing

### Mid-Round Strategies

4. **Volume Incentive** - Discount for larger quantities
5. **Term Premium** - Better pricing for longer terms
6. **Relationship Investment** - Invest in long-term customer
7. **Gradual Concession** - Small incremental concessions
8. **Conditional Discount** - Discount with conditions

### Late Round Strategies

9. **Split Difference** - Meet in the middle
10. **Final Offer** - Best and final offer
11. **Hold Firm** - No movement on price
12. **Walk Away** - Reject and end negotiation

### Specialized Strategies

13. **Scarcity Leverage** - Limited availability
14. **Bundle Upsell** - Add value through bundling

## Usage

### Basic Setup

```python
from procur.agents.advanced_seller_agent import (
    AdvancedSellerAgent,
    AdvancedSellerConfig,
)
from procur.agents.seller_personality import VendorPersonality

# Configure seller
config = AdvancedSellerConfig(
    personality=VendorPersonality.STRATEGIC,
    enable_learning=True,
    enable_constraints=True,
    enable_competitive_intelligence=True,
)

# Create agent
seller = AdvancedSellerAgent(
    vendor=vendor_profile,
    policy_engine=policy_engine,
    scoring_service=scoring_service,
    guardrail_service=guardrail_service,
    negotiation_engine=negotiation_engine,
    config=config,
)
```

### Set Business Context

```python
from procur.agents.seller_personality import VendorContext

context = VendorContext(
    capacity_utilization=0.75,
    inventory_level=0.6,
    quarter_position=0.8,  # Near end of quarter
    pipeline_strength=0.5,
    competitive_pressure=0.7,
)

seller.set_vendor_context(context)
```

### Generate Counter-Offer

```python
from procur.agents.seller_competitive import CompetitiveIntelligence

# Provide competitive intelligence
competitive_intel = CompetitiveIntelligence(
    competitors_involved=["competitor-1", "competitor-2"],
    estimated_competitor_prices={"competitor-1": 135.0, "competitor-2": 140.0},
    competitive_pressure=0.7,
    decision_criteria=["price", "features", "support"],
)

# Generate response
offer, strategy, alerts, policy_result, rationale = seller.respond(
    request=request,
    state=vendor_state,
    buyer_offer=buyer_offer_components,
    round_number=2,
    buyer_organization="acme-corp",
    competitive_intel=competitive_intel,
)

print(f"Strategy: {strategy}")
print(f"Price: ${offer.components.unit_price}")
print(f"Rationale: {rationale}")
```

### Record Outcome for Learning

```python
seller.record_negotiation_outcome(
    negotiation_id="neg-001",
    buyer_organization="acme-corp",
    category="CRM",
    initial_ask=150.0,
    final_price=140.0,
    rounds=4,
    outcome="won",
    duration_hours=48.0,
    buyer_aggressiveness=0.7,
)
```

### Get Negotiation Insights

```python
insights = seller.get_negotiation_insights(
    buyer_organization="acme-corp",
    category="CRM",
)

print(f"Expected rounds: {insights['buyer_behavior']['expected_rounds']}")
print(f"Expected discount: {insights['buyer_behavior']['expected_discount']}")
print(f"Recommended approach: {insights['recommended_approach']}")
```

## Historical Learning

### Buyer Profiles

The system learns:
- Win rate with each buyer
- Average discount given
- Negotiation patterns
- Price sensitivity
- Relationship value

### Category Insights

The system tracks:
- Average discounts by category
- Competitive intensity
- Win rates
- Seasonal patterns

### Predictive Capabilities

```python
prediction = learning_system.predict_buyer_behavior("acme-corp")
# Returns:
# {
#     "expected_rounds": 3.5,
#     "expected_discount": 0.12,
#     "aggressiveness": 0.7,
#     "price_sensitivity": 0.6,
#     "win_probability": 0.65,
# }
```

## Inventory & Capacity Constraints

### Inventory Management

```python
from procur.agents.seller_constraints import InventoryConstraint

constraint = InventoryConstraint(
    product_id="crm-license",
    available_quantity=1000,
    reserved_quantity=200,
    lead_time_days=14,
    reorder_point=300,
    max_capacity=1500,
)

constraint_manager.add_inventory_constraint(constraint)
```

### Capacity Management

```python
from procur.agents.seller_constraints import CapacityConstraint

constraint = CapacityConstraint(
    service_type="implementation",
    max_concurrent=50,
    current_utilization=35,
    onboarding_days=30,
)

constraint_manager.add_capacity_constraint(constraint)
```

### Seasonal Pricing

Automatic adjustments by month:
- **January**: Low demand, 5% discount
- **March**: Q1 rush, 2% premium
- **June**: Q2 rush, 5% premium
- **July-August**: Summer slow, 5-8% discount
- **December**: Year-end rush, 8% premium

## Competitive Intelligence

### Competitor Profiles

```python
from procur.agents.seller_competitive import CompetitorProfile, CompetitorTier

competitor = CompetitorProfile(
    competitor_id="salesforce",
    name="Salesforce",
    tier=CompetitorTier.PREMIUM,
    market_share=0.25,
    avg_price_point=160.0,
    strengths=["brand", "features", "ecosystem"],
    weaknesses=["price", "complexity"],
    typical_discount=0.08,
    win_rate_against=0.55,
)

competitive_intelligence.add_competitor(competitor)
```

### Win/Loss Tracking

```python
# Record loss
competitive_intelligence.record_loss(
    competitor_id="salesforce",
    deal_value=100000.0,
    reason="price",
    price_gap=15.0,
)

# Record win
competitive_intelligence.record_win(
    competitor_id="salesforce",
    deal_value=120000.0,
    price_advantage=5.0,
)
```

### Competitive Strategy

```python
strategy = competitive_intelligence.get_competitive_strategy(
    intelligence=competitive_intel,
    our_price=145.0,
    category="CRM",
)

# Returns:
# {
#     "approach": "competitive",
#     "price_adjustment": 0.97,
#     "emphasis": ["features", "reliability"],
#     "talking_points": ["Best value in market"],
# }
```

## Multi-Buyer Negotiation

### Context Management

```python
from procur.agents.seller_constraints import MultiBuyerContext

context = MultiBuyerContext(
    active_negotiations=8,
    total_pipeline_value=500000.0,
    avg_deal_size=50000.0,
    win_rate_this_month=0.45,
    quota_attainment=0.72,
    days_left_in_quarter=15,
)

seller.set_multi_buyer_context(context)
```

### Priority Scoring

```python
priority = context.get_deal_priority(deal_value=75000.0)
# Higher priority for:
# - Larger deals
# - End of quarter
# - Below quota
```

## Comparison: Basic vs Advanced

### Basic Seller Agent (69 lines)
- ❌ Single generic strategy
- ❌ No learning
- ❌ No personality
- ❌ No constraints
- ❌ No competitive intelligence
- ❌ Static pricing

### Advanced Seller Agent (2000+ lines)
- ✅ 14 sophisticated strategies
- ✅ Historical learning
- ✅ 7 personality types
- ✅ Inventory/capacity constraints
- ✅ Competitive intelligence
- ✅ Dynamic pricing
- ✅ Multi-buyer handling
- ✅ Seasonal adjustments
- ✅ Context-aware behavior

## Best Practices

### 1. Choose Appropriate Personality

Match personality to business model:
- **SaaS**: Strategic or Relationship
- **Hardware**: Volume-Focused or Opportunistic
- **Premium Products**: Premium or Aggressive
- **Services**: Cooperative or Strategic

### 2. Enable Learning

Always enable learning for better outcomes over time:
```python
config.enable_learning = True
```

### 3. Provide Competitive Intelligence

Better decisions with market context:
```python
competitive_intel = CompetitiveIntelligence(
    competitors_involved=[...],
    estimated_competitor_prices={...},
    competitive_pressure=0.7,
)
```

### 4. Update Business Context

Regularly update context for accurate behavior:
```python
# Update quarterly
context.quarter_position = days_into_quarter / 90.0
seller.set_vendor_context(context)
```

### 5. Record All Outcomes

Feed learning system for continuous improvement:
```python
seller.record_negotiation_outcome(...)
```

## Performance Metrics

Track seller agent performance:
- Win rate by personality type
- Average discount given
- Negotiation duration
- Customer satisfaction
- Revenue per negotiation
- Quota attainment

## Integration with Buyer Agent

The advanced seller agent matches the buyer agent's sophistication:

**Buyer Agent Features** → **Seller Agent Features**
- Opponent modeling → Buyer profiling
- Strategy selection → Counter-strategy selection
- TCO calculation → Value justification
- Stalemate detection → Walk-away logic
- Multi-vendor → Multi-buyer
- Learning → Historical learning

## License

Part of the Procur procurement automation platform.
