"""Inventory, capacity, and resource constraints for seller agents."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum


class ResourceType(Enum):
    """Types of constrained resources."""
    INVENTORY = "inventory"
    CAPACITY = "capacity"
    PERSONNEL = "personnel"
    DELIVERY = "delivery"


@dataclass
class InventoryConstraint:
    """Inventory availability constraint."""
    product_id: str
    available_quantity: int
    reserved_quantity: int
    lead_time_days: int
    reorder_point: int
    max_capacity: int
    
    def get_available(self) -> int:
        """Get currently available quantity."""
        return self.available_quantity - self.reserved_quantity
    
    def can_fulfill(self, quantity: int) -> bool:
        """Check if quantity can be fulfilled."""
        return self.get_available() >= quantity
    
    def get_fulfillment_date(self, quantity: int) -> Optional[datetime]:
        """Get earliest fulfillment date."""
        available = self.get_available()
        
        if available >= quantity:
            return datetime.now()
        
        # Need to wait for restock
        shortage = quantity - available
        batches_needed = (shortage + self.max_capacity - 1) // self.max_capacity
        days_needed = batches_needed * self.lead_time_days
        
        return datetime.now() + timedelta(days=days_needed)


@dataclass
class CapacityConstraint:
    """Service capacity constraint."""
    service_type: str
    max_concurrent: int
    current_utilization: int
    onboarding_days: int
    
    def get_utilization_rate(self) -> float:
        """Get capacity utilization rate."""
        return self.current_utilization / self.max_concurrent
    
    def can_accept(self, additional: int) -> bool:
        """Check if can accept additional customers."""
        return (self.current_utilization + additional) <= self.max_concurrent
    
    def get_availability_date(self, quantity: int) -> Optional[datetime]:
        """Get date when capacity will be available."""
        if self.can_accept(quantity):
            return datetime.now()
        
        # Estimate based on average customer lifecycle
        avg_lifecycle_days = 180  # 6 months average
        slots_needed = quantity - (self.max_concurrent - self.current_utilization)
        
        # Assume 10% churn per month
        months_to_free = slots_needed / (self.max_concurrent * 0.1)
        days_needed = int(months_to_free * 30)
        
        return datetime.now() + timedelta(days=days_needed)


@dataclass
class SeasonalPattern:
    """Seasonal pricing and demand patterns."""
    month: int
    demand_multiplier: float  # 1.0 = normal, >1.0 = high demand
    price_multiplier: float  # 1.0 = normal, >1.0 = premium
    capacity_multiplier: float  # 1.0 = normal, <1.0 = constrained
    
    @staticmethod
    def get_default_patterns() -> List['SeasonalPattern']:
        """Get default seasonal patterns."""
        return [
            SeasonalPattern(1, 0.8, 0.95, 1.1),   # Jan: Low demand, discounts
            SeasonalPattern(2, 0.9, 0.98, 1.1),   # Feb: Building
            SeasonalPattern(3, 1.1, 1.02, 0.95),  # Mar: Q1 end rush
            SeasonalPattern(4, 1.0, 1.0, 1.0),    # Apr: Normal
            SeasonalPattern(5, 1.0, 1.0, 1.0),    # May: Normal
            SeasonalPattern(6, 1.2, 1.05, 0.9),   # Jun: Q2 end rush
            SeasonalPattern(7, 0.7, 0.92, 1.2),   # Jul: Summer slow
            SeasonalPattern(8, 0.8, 0.95, 1.15),  # Aug: Summer slow
            SeasonalPattern(9, 1.1, 1.02, 0.95),  # Sep: Q3 end rush
            SeasonalPattern(10, 1.0, 1.0, 1.0),   # Oct: Normal
            SeasonalPattern(11, 1.1, 1.03, 0.95), # Nov: Year-end planning
            SeasonalPattern(12, 1.3, 1.08, 0.85), # Dec: Year-end rush
        ]


@dataclass
class MultiBuyerContext:
    """Context for managing multiple concurrent negotiations."""
    active_negotiations: int
    total_pipeline_value: float
    avg_deal_size: float
    win_rate_this_month: float
    quota_attainment: float  # 0.0-1.0
    days_left_in_quarter: int
    
    def get_deal_priority(self, deal_value: float) -> float:
        """Calculate priority score for a deal (0.0-1.0)."""
        # Larger deals get higher priority
        size_score = min(1.0, deal_value / (self.avg_deal_size * 2))
        
        # End of quarter increases priority
        urgency_score = 1.0 - (self.days_left_in_quarter / 90.0)
        
        # Below quota increases priority
        quota_score = max(0.0, 1.0 - self.quota_attainment)
        
        priority = (
            size_score * 0.4 +
            urgency_score * 0.3 +
            quota_score * 0.3
        )
        
        return priority
    
    def should_prioritize_volume(self) -> bool:
        """Check if should prioritize volume over margin."""
        # Prioritize volume if:
        # - Below quota
        # - End of quarter
        # - Low win rate
        return (
            self.quota_attainment < 0.8 or
            self.days_left_in_quarter < 15 or
            self.win_rate_this_month < 0.4
        )


class ConstraintManager:
    """Manages all constraints for seller agent."""
    
    def __init__(self):
        """Initialize constraint manager."""
        self.inventory_constraints: Dict[str, InventoryConstraint] = {}
        self.capacity_constraints: Dict[str, CapacityConstraint] = {}
        self.seasonal_patterns: List[SeasonalPattern] = SeasonalPattern.get_default_patterns()
        self.multi_buyer_context: Optional[MultiBuyerContext] = None
    
    def add_inventory_constraint(self, constraint: InventoryConstraint):
        """Add inventory constraint."""
        self.inventory_constraints[constraint.product_id] = constraint
    
    def add_capacity_constraint(self, constraint: CapacityConstraint):
        """Add capacity constraint."""
        self.capacity_constraints[constraint.service_type] = constraint
    
    def set_multi_buyer_context(self, context: MultiBuyerContext):
        """Set multi-buyer context."""
        self.multi_buyer_context = context
    
    def check_inventory(self, product_id: str, quantity: int) -> Dict[str, any]:
        """Check inventory availability."""
        if product_id not in self.inventory_constraints:
            return {
                "available": True,
                "quantity": quantity,
                "delivery_date": datetime.now(),
                "constraint_type": None,
            }
        
        constraint = self.inventory_constraints[product_id]
        
        return {
            "available": constraint.can_fulfill(quantity),
            "quantity": min(quantity, constraint.get_available()),
            "delivery_date": constraint.get_fulfillment_date(quantity),
            "constraint_type": "inventory",
            "lead_time_days": constraint.lead_time_days if not constraint.can_fulfill(quantity) else 0,
        }
    
    def check_capacity(self, service_type: str, quantity: int) -> Dict[str, any]:
        """Check service capacity."""
        if service_type not in self.capacity_constraints:
            return {
                "available": True,
                "quantity": quantity,
                "onboarding_date": datetime.now(),
                "constraint_type": None,
            }
        
        constraint = self.capacity_constraints[service_type]
        
        return {
            "available": constraint.can_accept(quantity),
            "quantity": min(quantity, constraint.max_concurrent - constraint.current_utilization),
            "onboarding_date": constraint.get_availability_date(quantity),
            "constraint_type": "capacity",
            "utilization_rate": constraint.get_utilization_rate(),
        }
    
    def get_seasonal_adjustment(self, month: Optional[int] = None) -> SeasonalPattern:
        """Get seasonal adjustment for current or specified month."""
        target_month = month or datetime.now().month
        
        for pattern in self.seasonal_patterns:
            if pattern.month == target_month:
                return pattern
        
        # Default pattern
        return SeasonalPattern(target_month, 1.0, 1.0, 1.0)
    
    def adjust_price_for_constraints(
        self,
        base_price: float,
        product_id: str,
        quantity: int,
    ) -> float:
        """Adjust price based on constraints."""
        adjusted_price = base_price
        
        # Seasonal adjustment
        seasonal = self.get_seasonal_adjustment()
        adjusted_price *= seasonal.price_multiplier
        
        # Inventory constraint adjustment
        if product_id in self.inventory_constraints:
            constraint = self.inventory_constraints[product_id]
            utilization = constraint.current_utilization / constraint.max_capacity
            
            # High utilization = premium pricing
            if utilization > 0.8:
                adjusted_price *= 1.1
            # Low utilization = discount
            elif utilization < 0.3:
                adjusted_price *= 0.95
        
        # Capacity constraint adjustment
        for constraint in self.capacity_constraints.values():
            utilization = constraint.get_utilization_rate()
            
            # High utilization = premium
            if utilization > 0.85:
                adjusted_price *= 1.08
            # Low utilization = discount
            elif utilization < 0.4:
                adjusted_price *= 0.93
        
        return adjusted_price
    
    def get_concession_flexibility(self) -> float:
        """Get concession flexibility based on constraints (0.0-1.0)."""
        flexibility_factors = []
        
        # Seasonal flexibility
        seasonal = self.get_seasonal_adjustment()
        if seasonal.demand_multiplier < 0.9:
            flexibility_factors.append(0.8)  # More flexible in low demand
        elif seasonal.demand_multiplier > 1.1:
            flexibility_factors.append(0.3)  # Less flexible in high demand
        else:
            flexibility_factors.append(0.5)
        
        # Inventory flexibility
        if self.inventory_constraints:
            avg_utilization = sum(
                c.current_utilization / c.max_capacity
                for c in self.inventory_constraints.values()
            ) / len(self.inventory_constraints)
            
            # Low inventory = more flexible
            flexibility_factors.append(1.0 - avg_utilization)
        
        # Capacity flexibility
        if self.capacity_constraints:
            avg_utilization = sum(
                c.get_utilization_rate()
                for c in self.capacity_constraints.values()
            ) / len(self.capacity_constraints)
            
            # Low capacity utilization = more flexible
            flexibility_factors.append(1.0 - avg_utilization)
        
        # Multi-buyer context
        if self.multi_buyer_context:
            if self.multi_buyer_context.should_prioritize_volume():
                flexibility_factors.append(0.7)  # More flexible to close deals
            else:
                flexibility_factors.append(0.4)  # Less flexible, focus on margin
        
        # Average all factors
        if flexibility_factors:
            return sum(flexibility_factors) / len(flexibility_factors)
        
        return 0.5  # Default moderate flexibility
