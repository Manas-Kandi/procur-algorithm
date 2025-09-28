from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Tuple

from ..models import Request, VendorProfile, Offer, OfferComponents, PaymentTerms, NegotiationDecision
from .policy_engine import PolicyEngine, PolicyResult
from .scoring_service import ScoringService
from .evaluation import (
    TCOInputs,
    compute_tco,
    compute_buyer_utility,
    compute_seller_utility,
    UtilityBreakdown,
    compute_feature_score,
    detect_zopa,
)


class NegotiationStrategy(Enum):
    """Buyer negotiation strategies"""
    PRICE_ANCHOR = "price_anchor"
    TERM_TRADE = "term_trade" 
    PAYMENT_TRADE = "payment_trade"
    VALUE_ADD = "value_add"
    ULTIMATUM = "ultimatum"
    PRICE_PRESSURE = "price_pressure"


class SellerStrategy(Enum):
    """Seller negotiation strategies"""
    ANCHOR_HIGH = "anchor_high"
    REJECT_BELOW_FLOOR = "reject_below_floor"
    MINIMAL_CONCESSION = "minimal_concession"
    TERM_VALUE = "term_value"
    PAYMENT_PREMIUM = "payment_premium"
    CLOSE_DEAL = "close_deal"
    GRADUAL_CONCESSION = "gradual_concession"


@dataclass
class OpponentModel:
    """Model of opponent's constraints and behavior"""
    price_floor_estimate: float
    price_ceiling_estimate: float
    price_elasticity: float = 0.5
    term_elasticity: float = 0.3
    consecutive_no_price_moves: int = 0
    last_offers: List[OfferComponents] = field(default_factory=list)


@dataclass
class OfferBundle:
    """Multi-dimensional offer bundle"""
    price: float
    term_months: int
    payment_terms: PaymentTerms
    value_adds: Dict[str, float]
    tco: float = 0
    utility: float = 0


@dataclass
class CompetingOffer:
    """Comparable offer from another vendor used for leverage."""

    vendor_id: str
    unit_price: float
    total_cost: float


@dataclass
class ExchangeRule:
    description: str
    minimum_delta: float
    leverage: str


@dataclass
class ExchangePolicy:
    """Deterministic exchange rates for price-for-lever trades"""

    term_trade: Dict[int, float] = field(
        default_factory=lambda: {12: 0.03, 24: 0.05, 36: 0.07}
    )
    payment_trade: Dict[PaymentTerms, float] = field(
        default_factory=lambda: {
            PaymentTerms.NET_15: 0.008,
            PaymentTerms.NET_30: 0.0,
            PaymentTerms.NET_45: -0.004,
            PaymentTerms.MILESTONES: 0.004,
            PaymentTerms.DEPOSIT: 0.012,
        }
    )
    value_add_offsets: Dict[str, float] = field(
        default_factory=lambda: {"training_credits": 1500.0}
    )
    min_step_abs: float = 10.0
    finalize_gap_abs: float = 5000.0
    finalize_gap_pct: float = 0.02
    close_extra_discount: float = 5.0
    max_rounds: int = 8


@dataclass
class NegotiationPlan:
    anchors: Dict[str, float]
    concession_ladder: List[str]
    stop_conditions: Dict[str, float]
    allowed_concessions: List[str]
    # Enhanced with opponent modeling
    opponent_model: Optional[OpponentModel] = None
    current_strategy: Optional[NegotiationStrategy] = None
    exchange_policy: ExchangePolicy = field(default_factory=ExchangePolicy)


@dataclass
class VendorNegotiationState:
    vendor: VendorProfile
    round: int = 0
    best_offer: Offer | None = None
    active: bool = True
    concession_index: int = 0
    history: List[Offer] = field(default_factory=list)
    # Enhanced with opponent modeling
    opponent_model: Optional[OpponentModel] = None
    stalemate_rounds: int = 0
    plan: Optional[NegotiationPlan] = None
    compliance_summary: List[str] = field(default_factory=list)
    outcome_state: Optional[str] = None
    outcome_reason: Optional[str] = None
    fsm_state: str = "init"
    concessions: Optional[ConcessionEngine] = None
    estimated_min_concession_price: Optional[float] = None
    concession_notes: List[str] = field(default_factory=list)
    match_summary: Optional[object] = None
    competing_offers: List[CompetingOffer] = field(default_factory=list)


class AdvancedNegotiationStrategies:
    """Optional advanced tactics layered on top of the core engine."""

    def __init__(self, engine: "NegotiationEngine") -> None:
        self.engine = engine

    # ------------------------------------------------------------------
    # Tactical levers
    # ------------------------------------------------------------------
    def competitor_leveraging(self, state: VendorNegotiationState) -> Optional[NegotiationStrategy]:
        """Recommend a strategy when stronger competing offers exist."""
        if not state.competing_offers:
            return None
        if state.best_offer is None:
            return None

        best_competitor = min(state.competing_offers, key=lambda offer: offer.total_cost)
        best_price = best_competitor.unit_price
        current_price = state.best_offer.components.unit_price

        # Require a meaningful delta (≥5%) before escalating
        if current_price <= 0:
            return None
        price_gap = (current_price - best_price) / current_price
        if price_gap >= 0.05:
            note = (
                f"Leverage competitor {best_competitor.vendor_id} (${best_price:,.2f})"
                f" vs current ${current_price:,.2f}"
            )
            state.concession_notes.append(note)
            return NegotiationStrategy.PRICE_PRESSURE
        return None

    def volume_discounting(self, request: Request) -> float:
        """Calculate additional discount based on deal volume."""
        if request.quantity >= 500:
            return 0.20
        if request.quantity >= 250:
            return 0.18
        if request.quantity > 100:
            return 0.15
        return 0.0

    def seasonal_timing(self, vendor: VendorProfile) -> float:
        """Increase leverage near quarter/year end when vendors chase targets."""
        if self.is_end_of_quarter():
            return 0.10
        if self.is_end_of_year():
            return 0.12
        return 0.0

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------
    @staticmethod
    def is_end_of_quarter() -> bool:
        today = datetime.utcnow()
        return today.month in {3, 6, 9, 12} and today.day >= 20

    @staticmethod
    def is_end_of_year() -> bool:
        today = datetime.utcnow()
        return today.month == 12 and today.day >= 10

    def combined_discount(self, request: Request, vendor: VendorProfile) -> float:
        volume = self.volume_discounting(request)
        seasonal = self.seasonal_timing(vendor)
        return min(volume + seasonal, 0.30)

class NegotiationEngine:
    """Enhanced negotiation engine with sophisticated algorithms."""

    def __init__(
        self,
        policy_engine: PolicyEngine,
        scoring_service: ScoringService,
        *,
        buyer_accept_threshold: float = 0.75,
        seller_accept_threshold: float = 0.10,
        max_stalled_rounds: int = 3,
    ) -> None:
        self.policy_engine = policy_engine
        self.scoring_service = scoring_service
        self.buyer_accept_threshold = buyer_accept_threshold
        self.seller_accept_threshold = seller_accept_threshold
        self.max_stalled_rounds = max_stalled_rounds
        # Keep module-level constants in sync for legacy consumers
        global BUYER_ACCEPT_THRESHOLD, SELLER_ACCEPT_THRESHOLD, MAX_STALLED_ROUNDS
        BUYER_ACCEPT_THRESHOLD = buyer_accept_threshold
        SELLER_ACCEPT_THRESHOLD = seller_accept_threshold
        MAX_STALLED_ROUNDS = max_stalled_rounds
        self.advanced_strategies = AdvancedNegotiationStrategies(self)

    def _offer_to_tco_inputs(self, offer: OfferComponents) -> TCOInputs:
        one_time_positive = sum(value for value in offer.one_time_fees.values() if value >= 0)
        credits = -sum(value for value in offer.one_time_fees.values() if value < 0)
        return TCOInputs(
            unit_price=Decimal(str(offer.unit_price or 0.0)),
            seats=offer.quantity or 1,
            term_months=offer.term_months or 12,
            one_time_fees=Decimal(str(one_time_positive)),
            credits=Decimal(str(credits)),
            payment_prepaid=False,
            prepay_discount_rate=Decimal(str(getattr(offer, "prepay_discount_rate", 0.0))),
        )

    def calculate_tco_breakdown(self, offer: OfferComponents):
        return compute_tco(self._offer_to_tco_inputs(offer))

    def calculate_tco(self, offer: OfferComponents) -> float:
        return float(self.calculate_tco_breakdown(offer).total)

    def calculate_utility(
        self,
        offer: OfferComponents,
        request: Request,
        *,
        vendor: Optional[VendorProfile] = None,
        is_buyer: bool = True,
    ) -> float:
        """Calculate utility score for an offer"""
        tco = self.calculate_tco(offer)

        if is_buyer:
            budget_max = request.budget_max or 0.0
            cost_fit = 0.0
            if budget_max > 0 and tco > 0:
                cost_fit = min(budget_max / tco, 1.0)

            feature_fit = self._feature_fit(request, vendor)
            compliance_fit = self._compliance_fit(request, vendor)
            term_fit = max(0.0, 1 - abs(offer.term_months - 12) / 24)
            payment_fit = self._buyer_payment_preference(offer.payment_terms)

            utility = (
                0.4 * cost_fit
                + 0.2 * feature_fit
                + 0.2 * compliance_fit
                + 0.1 * term_fit
                + 0.1 * payment_fit
            )
            return round(min(max(utility, 0.0), 1.0), 4)

        if vendor is None:
            return 0.5

        floor = vendor.guardrails.price_floor or max(offer.unit_price * 0.4, 1.0)
        margin = max(offer.unit_price - floor, 0)
        max_margin = max((vendor.price_tiers.get(str(offer.quantity), offer.unit_price) - floor), 1.0)
        margin_utility = min(margin / max_margin, 1.0)

        term_preference = min(offer.term_months / 36, 1.0)
        payment_preference = self._seller_payment_preference(offer.payment_terms)

        return 0.6 * margin_utility + 0.25 * term_preference + 0.15 * payment_preference

    def _feature_fit(self, request: Request, vendor: Optional[VendorProfile]) -> float:
        required_features = list(
            dict.fromkeys([*request.must_haves, *request.specs.get("features", [])])
        )

        if not required_features:
            return 1.0
        if vendor is None:
            return 0.6

        score = compute_feature_score(
            must_haves=required_features,
            vendor_features=vendor.capability_tags,
        )
        return max(0.0, min(score.score, 1.0))

    def _compliance_fit(self, request: Request, vendor: Optional[VendorProfile]) -> float:
        requirements = {req.lower() for req in request.compliance_requirements}
        if not requirements:
            return 1.0
        if vendor is None:
            return 0.6
        vendor_certs = {cert.lower() for cert in vendor.certifications}
        matches = len(requirements & vendor_certs)
        return max(0.0, min(matches / len(requirements), 1.0))

    def _buyer_payment_preference(self, payment_terms: PaymentTerms) -> float:
        mapping = {
            PaymentTerms.NET_15: 0.9,
            PaymentTerms.NET_30: 1.0,
            PaymentTerms.NET_45: 0.7,
            PaymentTerms.MILESTONES: 0.85,
            PaymentTerms.DEPOSIT: 0.6,
        }
        return mapping.get(payment_terms, 0.75)

    def _strategy_for_lever(self, lever: str) -> NegotiationStrategy:
        mapping = {
            "multi_year_discount": NegotiationStrategy.TERM_TRADE,
            "term": NegotiationStrategy.TERM_TRADE,
            "payment_terms": NegotiationStrategy.PAYMENT_TRADE,
            "payment": NegotiationStrategy.PAYMENT_TRADE,
            "value_add": NegotiationStrategy.VALUE_ADD,
            "price_adjustment": NegotiationStrategy.PRICE_PRESSURE,
        }
        return mapping.get(lever, NegotiationStrategy.PRICE_PRESSURE)

    def determine_buyer_strategy(self, state: VendorNegotiationState, current_offer: OfferComponents) -> NegotiationStrategy:
        """Determine optimal buyer strategy based on negotiation state"""
        round_num = state.round
        plan = state.plan

        advanced = self.advanced_strategies.competitor_leveraging(state)
        if advanced:
            return advanced

        if plan and state.stalemate_rounds >= self.max_stalled_rounds:
            next_lever = self.next_concession(plan, state)
            state.stalemate_rounds = 0
            return self._strategy_for_lever(next_lever)

        if round_num == 1:
            return NegotiationStrategy.PRICE_ANCHOR
        elif round_num == 2 and state.opponent_model and state.opponent_model.consecutive_no_price_moves > 0:
            return NegotiationStrategy.TERM_TRADE
        elif round_num == 3 and current_offer.payment_terms == PaymentTerms.NET_45:
            return NegotiationStrategy.PAYMENT_TRADE
        elif self.detect_stalemate(state):
            return NegotiationStrategy.ULTIMATUM
        elif round_num >= 4:
            return NegotiationStrategy.VALUE_ADD
        else:
            return NegotiationStrategy.PRICE_PRESSURE

    def detect_stalemate(self, state: VendorNegotiationState) -> bool:
        """Detect if negotiation is stuck with minimal utility/TCO improvement"""
        if len(state.history) < self.max_stalled_rounds:
            return False

        # Check if last MAX_STALLED_ROUNDS rounds had minimal progress
        recent_offers = state.history[-self.max_stalled_rounds:]
        if len(recent_offers) >= self.max_stalled_rounds:
            utility_changes = []
            tco_changes = []

            for i in range(1, len(recent_offers)):
                prev_offer = recent_offers[i-1]
                curr_offer = recent_offers[i]

                # Track utility improvement
                utility_change = abs(curr_offer.score.utility - prev_offer.score.utility)
                utility_changes.append(utility_change)

                # Track TCO improvement (lower is better, so we look for decreases)
                prev_tco = self.calculate_tco(prev_offer.components)
                curr_tco = self.calculate_tco(curr_offer.components)
                tco_improvement = max(0, prev_tco - curr_tco)  # Positive if TCO decreased
                tco_changes.append(tco_improvement)

            # If average utility improvement and TCO improvement are both less than ε, consider stalemate
            avg_utility_change = sum(utility_changes) / len(utility_changes) if utility_changes else 0
            avg_tco_improvement = sum(tco_changes) / len(tco_changes) if tco_changes else 0

            # ε thresholds for considering progress stalled
            utility_epsilon = 0.01  # 1% utility improvement
            tco_epsilon = 50.0     # $50 TCO improvement

            return avg_utility_change < utility_epsilon and avg_tco_improvement < tco_epsilon

        return False

    def update_opponent_model(self, model: OpponentModel, new_offer: OfferComponents, previous_offer: Optional[OfferComponents]):
        """Update beliefs about opponent based on their moves with tighter bounds"""
        if previous_offer is None:
            model.last_offers.append(new_offer)
            return
            
        # Track price movement
        price_change = new_offer.unit_price - previous_offer.unit_price
        moved_price = abs(price_change) >= 5  # Meaningful movement threshold
        
        if not moved_price:
            model.consecutive_no_price_moves += 1
            # Tighten floor estimate - we're likely near their limit
            delta = 25  # Conservative buffer
            model.price_floor_estimate = max(model.price_floor_estimate, new_offer.unit_price - delta)
        else:
            model.consecutive_no_price_moves = 0
            # Price moved - floor is at or below this price
            model.price_ceiling_estimate = min(model.price_ceiling_estimate, new_offer.unit_price)
            
        # Update elasticity based on movement patterns
        if moved_price:
            model.price_elasticity = min(0.9, model.price_elasticity + 0.1)
        else:
            model.price_elasticity = max(0.1, model.price_elasticity - 0.1)
        
        # Track term flexibility
        term_change = new_offer.term_months - previous_offer.term_months
        if abs(term_change) > 0:
            model.term_elasticity = min(0.9, model.term_elasticity + 0.1)
            
        model.last_offers.append(new_offer)
        if len(model.last_offers) > 3:
            model.last_offers.pop(0)

    def generate_target_bundle(self, strategy: NegotiationStrategy, request: Request, 
                             current_offer: OfferComponents, state: VendorNegotiationState) -> OfferBundle:
        """Generate target bundle based on strategy with consistency enforcement"""
        base_price = current_offer.unit_price
        policy = state.plan.exchange_policy if state.plan else ExchangePolicy()
        leverage_discount = self.advanced_strategies.combined_discount(request, state.vendor)
        discount_noted = False

        def apply_extra(price: float) -> float:
            nonlocal discount_noted
            if leverage_discount <= 0:
                return price
            adjusted = price * (1 - leverage_discount)
            if not discount_noted:
                state.concession_notes.append(
                    f"Applied advanced leverage discount {leverage_discount:.0%}"
                )
                discount_noted = True
            floor_price = state.vendor.guardrails.price_floor or 0.0
            minimum = floor_price if floor_price else adjusted
            return max(adjusted, minimum)

        if strategy == NegotiationStrategy.PRICE_ANCHOR:
            target_price = base_price * 0.85  # Aggressive anchor
            target_price = min(target_price, apply_extra(base_price))
            return OfferBundle(
                price=target_price,
                term_months=current_offer.term_months,
                payment_terms=current_offer.payment_terms,
                value_adds={}
            )
            
        elif strategy == NegotiationStrategy.TERM_TRADE:
            # STRATEGY CONSISTENCY: term_trade MUST increase terms
            new_term = max(current_offer.term_months + 12, 24)  # Force increase
            price_reduction = self._term_discount(policy, current_offer.term_months, new_term)
            target_price = base_price * (1 - price_reduction)
            target_price = apply_extra(target_price)
            
            return OfferBundle(
                price=max(target_price, base_price * 0.90),  # Floor at 10% reduction
                term_months=new_term,
                payment_terms=current_offer.payment_terms,
                value_adds={}
            )
            
        elif strategy == NegotiationStrategy.PAYMENT_TRADE:
            # Apply deterministic exchange rate for faster payment
            discount = self._payment_discount(policy, PaymentTerms.NET_15)
            target_price = base_price * (1 - discount)
            target_price = apply_extra(target_price)
            return OfferBundle(
                price=target_price,
                term_months=current_offer.term_months,
                payment_terms=PaymentTerms.NET_15,  # Faster payment
                value_adds={}
            )
            
        elif strategy == NegotiationStrategy.VALUE_ADD:
            # Request training credits at deterministic value
            value_adds = {
                key: self._value_add_credit(policy, key)
                for key in policy.value_add_offsets.keys()
            }
            return OfferBundle(
                price=base_price,  # No price change
                term_months=current_offer.term_months,
                payment_terms=current_offer.payment_terms,
                value_adds=value_adds
            )
            
        elif strategy == NegotiationStrategy.ULTIMATUM:
            floor_estimate = state.opponent_model.price_floor_estimate if state.opponent_model else base_price * 0.8
            return OfferBundle(
                price=max(apply_extra(floor_estimate + 25), base_price * 0.92),
                term_months=12,
                payment_terms=PaymentTerms.NET_30,
                value_adds={}
            )
        else:  # Default incremental with minimum step
            price_reduction = max(policy.min_step_abs, base_price * 0.08)
            target_price = apply_extra(base_price - price_reduction)
            return OfferBundle(
                price=target_price,
                term_months=current_offer.term_months,
                payment_terms=current_offer.payment_terms,
                value_adds={}
            )

    def evaluate_stop_conditions(
        self,
        plan: NegotiationPlan,
        state: VendorNegotiationState,
        offer: Offer,
    ) -> bool:
        score = offer.score.utility
        stop_score = plan.stop_conditions.get("utility")
        if stop_score is not None and score >= stop_score:
            return True
        risk = offer.score.risk
        max_risk = plan.stop_conditions.get("risk")
        if max_risk is not None and risk > max_risk:
            return True
        return False

    def next_concession(self, plan: NegotiationPlan, state: VendorNegotiationState) -> str:
        if not plan.concession_ladder:
            return "price_adjustment"
        idx = min(state.concession_index, len(plan.concession_ladder) - 1)
        lever = plan.concession_ladder[idx]
        state.concession_index = min(idx + 1, len(plan.concession_ladder) - 1)
        return lever

    def decide_next_move(
        self,
        plan: NegotiationPlan,
        state: VendorNegotiationState,
        offer: Offer,
    ) -> NegotiationDecision:
        if self.evaluate_stop_conditions(plan, state, offer):
            return NegotiationDecision.ACCEPT
        if state.round >= len(plan.concession_ladder) - 1:
            return NegotiationDecision.DROP
        return NegotiationDecision.COUNTER

    def record_offer(self, state: VendorNegotiationState, offer: Offer) -> None:
        state.history.append(offer)
        if not state.best_offer or offer.score.utility > state.best_offer.score.utility:
            state.best_offer = offer

    def validate_counter(
        self,
        components: OfferComponents,
        vendor: VendorProfile,
    ) -> PolicyResult:
        floor = vendor.guardrails.price_floor
        return self.policy_engine.enforce_concession_floor(floor, components.unit_price)

    def should_close_deal(self, state: VendorNegotiationState, current_offer: OfferComponents, request: Request) -> tuple[bool, str]:
        """Determine if we should accept current offer and close deal with reason"""
        if not current_offer:
            return False, "no_offer"

        # Compute TCO breakdown, buyer and seller utilities
        tco_breakdown = self.scoring_service.compute_tco_breakdown(current_offer)

        summary = getattr(state, "match_summary", None)
        feature_score = summary.feature.score if summary else 0.0
        compliance_score = summary.compliance.score if summary else 0.0
        sla_score = summary.sla_score if summary else 0.0
        budget_per_unit = 0.0
        if request.budget_max and request.quantity:
            budget_per_unit = request.budget_max / request.quantity

        buyer_bd = compute_buyer_utility(
            unit_price=current_offer.unit_price,
            budget_per_unit=budget_per_unit,
            feature_score=feature_score,
            compliance_score=compliance_score,
            sla_score=sla_score,
        )

        list_price = state.vendor.price_tiers.get(str(request.quantity), current_offer.unit_price)
        floor_price = state.vendor.guardrails.price_floor or current_offer.unit_price
        seller_bd = compute_seller_utility(
            proposed_price=current_offer.unit_price,
            list_price=list_price,
            floor_price=floor_price,
            min_accept_threshold=self.seller_accept_threshold,
        )

        # Before transitioning to ACCEPTED, enforce all invariants:

        # 1. Budget compliance
        if request.budget_max and float(tco_breakdown.total) > request.budget_max:
            return False, "budget_exceeded"

        # 2. Buyer utility threshold
        if buyer_bd.buyer_utility < self.buyer_accept_threshold:
            return False, "buyer_utility_too_low"

        # 3. Seller utility threshold
        if seller_bd.seller_utility < self.seller_accept_threshold:
            return False, "seller_utility_too_low"

        # 4. Policy compliance
        try:
            policy_result = self.policy_engine.validate_offer(
                request,
                current_offer,
                vendor=state.vendor,
                is_buyer_proposal=False,
            )
            if not policy_result.valid:
                return False, "policy_violation"
        except:
            return False, "policy_validation_failed"

        # 5. Guardrails check (in production mode)
        # This would check required guardrails like vendor bank verification
        # For now, we'll check basic vendor floor constraints
        if state.vendor.guardrails.price_floor and current_offer.unit_price < state.vendor.guardrails.price_floor:
            return False, "below_vendor_floor"

        # If all invariants pass, check convergence conditions
        policy = state.plan.exchange_policy if state.plan else ExchangePolicy()

        if state.opponent_model and len(state.opponent_model.last_offers) >= 2:
            recent_offers = state.opponent_model.last_offers[-2:]
            price_gap = abs(recent_offers[-1].unit_price - recent_offers[-2].unit_price)

            # Close if gap is small enough (absolute or percentage) AND price is moving in our favor
            if price_gap < policy.finalize_gap_abs and recent_offers[-1].unit_price <= recent_offers[-2].unit_price:
                return True, "converged_absolute"
            if (current_offer.unit_price > 0 and
                price_gap / current_offer.unit_price < policy.finalize_gap_pct and
                recent_offers[-1].unit_price <= recent_offers[-2].unit_price):
                return True, "converged_percentage"

        # Accept if all thresholds met
        return True, "utility_threshold"

    def enforce_offer_diversity(self, new_bundle: OfferBundle, state: VendorNegotiationState) -> OfferBundle:
        """Ensure offers are diverse and show monotonic progress"""
        if not state.opponent_model or not state.opponent_model.last_offers:
            return new_bundle
            
        last_offer = state.opponent_model.last_offers[-1]
        
        # Check if offer is too similar to previous
        price_diff = abs(new_bundle.price - last_offer.unit_price)
        term_diff = abs(new_bundle.term_months - last_offer.term_months)
        
        if price_diff < 5 and term_diff == 0:  # Too similar
            # Force meaningful change
            if new_bundle.price >= last_offer.unit_price:  # No progress
                new_bundle.price = last_offer.unit_price - 15  # Force concession
                
        # Ensure monotonic progress (buyer prices should generally decrease)
        if len(state.opponent_model.last_offers) >= 2:
            prev_offers = [o.unit_price for o in state.opponent_model.last_offers[-2:]]
            if new_bundle.price > min(prev_offers):  # Going backwards
                new_bundle.price = min(prev_offers) - 10  # Force progress
                
        return new_bundle

    def generate_multiple_bundles(self, strategy: NegotiationStrategy, request: Request, 
                                current_offer: OfferComponents, state: VendorNegotiationState) -> List[OfferBundle]:
        """Generate multiple offer bundles for enhanced UX"""
        vendor = state.vendor

        primary = self.generate_target_bundle(strategy, request, current_offer, state)
        primary = self.enforce_offer_diversity(primary, state)
        
        bundles = [primary]
        
        # Generate alternative bundles
        if strategy != NegotiationStrategy.TERM_TRADE:
            # Add term trade alternative
            term_alt = self.generate_target_bundle(NegotiationStrategy.TERM_TRADE, request, current_offer, state)
            bundles.append(term_alt)
            
        if strategy != NegotiationStrategy.PAYMENT_TRADE:
            # Add payment trade alternative  
            payment_alt = self.generate_target_bundle(NegotiationStrategy.PAYMENT_TRADE, request, current_offer, state)
            bundles.append(payment_alt)
            
        # Calculate TCO and utility for all bundles
        for bundle in bundles:
            mock_offer = OfferComponents(
                unit_price=bundle.price,
                currency=current_offer.currency,
                quantity=current_offer.quantity,
                term_months=bundle.term_months,
                payment_terms=bundle.payment_terms
            )
            bundle.tco = self.calculate_tco(mock_offer)
            bundle.utility = self.calculate_utility(
                mock_offer,
                request,
                vendor=vendor,
                is_buyer=True,
            )
            
        return bundles[:3]  # Limit to 3 options

    def determine_seller_strategy(self, state: VendorNegotiationState, buyer_offer: OfferComponents) -> SellerStrategy:
        """Mirror logic for seller strategy selection"""
        if not state.opponent_model:
            return SellerStrategy.ANCHOR_HIGH
            
        # Analyze buyer behavior patterns
        if len(state.opponent_model.last_offers) >= 2:
            recent_offers = state.opponent_model.last_offers[-2:]
            price_trend = recent_offers[-1].unit_price - recent_offers[-2].unit_price
            
            # If buyer is making aggressive moves, be firm
            if abs(price_trend) > 50:
                return SellerStrategy.REJECT_BELOW_FLOOR
                
            # If buyer is stalled, make minimal concession
            if abs(price_trend) < 10:
                return SellerStrategy.MINIMAL_CONCESSION
        
        # Check if near floor price
        floor_price = state.vendor.guardrails.price_floor
        if floor_price is not None and abs(buyer_offer.unit_price - floor_price) <= 1e-2:
            return SellerStrategy.CLOSE_DEAL
        if buyer_offer.unit_price <= floor_price * 1.1:
            return SellerStrategy.REJECT_BELOW_FLOOR
            
        # If many rounds, try to close
        if state.round >= 5:
            return SellerStrategy.CLOSE_DEAL
            
        # Default gradual concession
        return SellerStrategy.GRADUAL_CONCESSION

    def generate_seller_counter(self, strategy: SellerStrategy, buyer_offer: OfferComponents, 
                              state: VendorNegotiationState) -> OfferComponents:
        """Generate seller counter-offer based on strategy"""
        current_price = buyer_offer.unit_price
        floor_price = state.vendor.guardrails.price_floor
        policy = state.plan.exchange_policy if state.plan else ExchangePolicy()
        
        if strategy == SellerStrategy.ANCHOR_HIGH:
            # Start high to establish value perception
            target_price = max(current_price * 1.15, floor_price * 1.3)
            
        elif strategy == SellerStrategy.REJECT_BELOW_FLOOR:
            # Firm rejection, minimal movement
            target_price = max(floor_price * 1.05, current_price * 1.02)
            
        elif strategy == SellerStrategy.MINIMAL_CONCESSION:
            # Smallest possible concession
            target_price = max(floor_price, current_price - policy.min_step_abs)
            
        elif strategy == SellerStrategy.TERM_VALUE:
            # Reward longer terms with better pricing
            if buyer_offer.term_months >= 24:
                discount = self._term_discount(policy, 12, buyer_offer.term_months)
                target_price = current_price * (1 - discount)
            else:
                target_price = current_price * 1.01  # Small increase for short terms
                
        elif strategy == SellerStrategy.PAYMENT_PREMIUM:
            # Better pricing for faster payment
            if buyer_offer.payment_terms == PaymentTerms.NET_15:
                discount = self._payment_discount(policy, PaymentTerms.NET_15)
                target_price = current_price * (1 - discount)
            else:
                premium = abs(self._payment_discount(policy, buyer_offer.payment_terms))
                target_price = current_price * (1 + premium)
                
        elif strategy == SellerStrategy.CLOSE_DEAL:
            # Final concession to close at floor
            target_price = floor_price if floor_price is not None else current_price
            
        else:  # GRADUAL_CONCESSION
            # Standard incremental reduction
            target_price = max(floor_price, current_price - policy.min_step_abs)
        
        return OfferComponents(
            unit_price=max(target_price, floor_price) if floor_price is not None else target_price,
            currency=buyer_offer.currency,
            quantity=buyer_offer.quantity,
            term_months=buyer_offer.term_months,
            payment_terms=buyer_offer.payment_terms
        )

    def feasible_with_trades(self, request: Request, vendor: VendorProfile, policy: ExchangePolicy) -> bool:
        """Test feasibility including trade scenarios (not just price-only ZOPA)"""
        if request.quantity <= 0:
            return False
        budget_per_unit = request.budget_max / request.quantity
        tier_key = str(request.quantity)
        list_price = vendor.price_tiers.get(tier_key, vendor.guardrails.price_floor * 1.2)
        seller_floor = vendor.guardrails.price_floor or list_price

        concessions = ConcessionEngine(
            {
                "term_trade": policy.term_trade,
                "payment_trade": {term.value: pct for term, pct in policy.payment_trade.items()},
                "value_add_offsets": policy.value_add_offsets,
            }
        )
        best_price, _ = concessions.best_effective_price(
            list_price=list_price,
            floor_price=seller_floor,
            seats=request.quantity,
        )
        return detect_zopa(
            buyer_budget_per_unit=budget_per_unit,
            seller_floor=seller_floor,
            concessions_min_price=best_price,
        )
    
    def seed_bundles(self, request: Request, vendor: VendorProfile, policy: ExchangePolicy) -> List[OfferBundle]:
        """Generate 3 opening bundles that respect policy - MUST produce ≥1"""
        bundles = []
        if request.quantity <= 0:
            return bundles
        tier_key = str(request.quantity)
        list_price = vendor.price_tiers.get(tier_key, vendor.guardrails.price_floor * 1.2)
        budget_per_unit = request.budget_max / request.quantity
        
        # A) Price anchor (aggressive but within policy)
        anchor_drop = min(0.15, max(0.05, (list_price - budget_per_unit) / list_price))
        price_anchor = max(vendor.guardrails.price_floor, list_price * (1 - anchor_drop))
        bundles.append(OfferBundle(
            price=price_anchor,
            term_months=12,
            payment_terms=PaymentTerms.NET_30,
            value_adds={}
        ))
        
        # B) Term trade (longer term for price reduction)
        term_discount = max(policy.term_trade.get(12, 0.0), 0.0)
        price_term = max(vendor.guardrails.price_floor, list_price * (1 - term_discount))
        bundles.append(OfferBundle(
            price=price_term,
            term_months=24,
            payment_terms=PaymentTerms.NET_30,
            value_adds={}
        ))
        
        # C) Payment trade (faster payment for small discount)
        payment_discount = self._payment_discount(policy, PaymentTerms.NET_15)
        price_payment = max(vendor.guardrails.price_floor, list_price * (1 - payment_discount))
        bundles.append(OfferBundle(
            price=price_payment,
            term_months=12,
            payment_terms=PaymentTerms.NET_15,
            value_adds={}
        ))
        
        # D) Value-add bundle for tight budgets
        if budget_per_unit < list_price * 0.9:
            value_adds = {
                key: self._value_add_credit(policy, key)
                for key in policy.value_add_offsets
            }
            bundles.append(OfferBundle(
                price=list_price,
                term_months=12,
                payment_terms=PaymentTerms.NET_30,
                value_adds=value_adds
            ))
        
        # Validate bundles and apply deadman switch
        valid_bundles = []
        for bundle in bundles:
            tco = self.calculate_tco_for_bundle(bundle, request)
            budget_max = request.budget_max or float('inf')
            if tco <= budget_max * 1.1:  # Allow 10% budget flexibility
                valid_bundles.append(bundle)
        
        # Deadman switch: if no bundles pass, choose least violating
        if not valid_bundles:
            # Find bundle with lowest TCO overage
            best_bundle = min(bundles, key=lambda b: self.calculate_tco_for_bundle(b, request))
            valid_bundles = [best_bundle]
            
        return valid_bundles
    
    def calculate_tco_for_bundle(self, bundle: OfferBundle, request: Request) -> float:
        """Calculate TCO for an offer bundle"""
        mock_offer = OfferComponents(
            unit_price=bundle.price,
            currency="USD",
            quantity=request.quantity,
            term_months=bundle.term_months,
            payment_terms=bundle.payment_terms
        )
        tco = self.calculate_tco(mock_offer)
        
        # Subtract value-adds
        for value_type, amount in bundle.value_adds.items():
            if value_type == "training_credits":
                tco -= amount
                
        return tco
    
    def pv_benefit(self, amount: float, delta_days: int, annual_rate: float = 0.12) -> float:
        """Calculate present value benefit of delayed payment"""
        r_daily = (1 + annual_rate) ** (1/365) - 1
        return amount * (1 - 1/((1 + r_daily) ** delta_days))
    
    def maybe_close(self, buyer_price: float, seller_price: float, policy: ExchangePolicy, 
                   quantity: int, current_terms: tuple) -> List[OfferBundle]:
        """Generate closing options when prices converge"""
        gap = abs(buyer_price - seller_price) * quantity
        
        if (gap <= policy.finalize_gap_abs or 
            (buyer_price * quantity) > 0 and gap / (buyer_price * quantity) <= policy.finalize_gap_pct):
            
            mid_price = (buyer_price + seller_price) / 2
            term_months, payment_terms = current_terms
            
            # Option A: Mid-split at current terms
            option_a = OfferBundle(
                price=mid_price,
                term_months=term_months,
                payment_terms=payment_terms,
                value_adds={}
            )
            
            # Option B: Slightly lower price for longer term
            option_b = OfferBundle(
                price=mid_price - policy.close_extra_discount,
                term_months=max(term_months, 24),
                payment_terms=PaymentTerms.NET_30,
                value_adds={}
            )
            
            return [option_a, option_b]
        
        return []
    
    def choose_lever_epsilon_greedy(self, history: List[Offer], round_no: int) -> str:
        """Epsilon-greedy strategy selection for exploration vs exploitation"""
        eps = max(0.1, 0.4 - 0.05 * round_no)  # Anneal exploration
        levers = ["price", "term", "payment", "value"]
        
        if len(history) < 2 or random.random() < eps:
            # Explore: choose different lever than last round
            last_lever = getattr(history[-1], 'primary_lever', None) if history else None
            available_levers = [l for l in levers if l != last_lever]
            return available_levers[0] if available_levers else levers[0]
        
        # Exploit: choose lever with best historical yield
        return self.best_lever_by_yield(history)
    
    def best_lever_by_yield(self, history: List[Offer]) -> str:
        """Find lever with best ΔScore per unit concession"""
        lever_yields = {"price": 0, "term": 0, "payment": 0, "value": 0}
        
        for i in range(1, len(history)):
            prev_offer = history[i-1]
            curr_offer = history[i]
            score_change = curr_offer.score.utility - prev_offer.score.utility
            
            # Determine primary lever used
            if abs(curr_offer.components.unit_price - prev_offer.components.unit_price) > 5:
                lever_yields["price"] += score_change
            elif curr_offer.components.term_months != prev_offer.components.term_months:
                lever_yields["term"] += score_change
            elif curr_offer.components.payment_terms != prev_offer.components.payment_terms:
                lever_yields["payment"] += score_change
            else:
                lever_yields["value"] += score_change
        
        return max(lever_yields, key=lever_yields.get)

    def calculate_acceptance_probability(self, offer: OfferComponents, request: Request, 
                                       state: VendorNegotiationState) -> float:
        """Calibrated acceptance probability using logistic function"""
        tco = self.calculate_tco(offer)
        utility = self.calculate_utility(offer, request, vendor=state.vendor, is_buyer=True)
        
        # Price fit: how close to budget constraints
        budget_ratio = tco / request.budget_max
        price_fit = max(0, 1 - budget_ratio)  # 1.0 = perfect fit, 0.0 = over budget
        
        # Lever fit: term and payment preferences
        term_preference = 1.0 - abs(offer.term_months - 12) / 24  # Prefer 12 months
        payment_preference = {
            PaymentTerms.NET_30: 1.0,
            PaymentTerms.NET_15: 0.9,
            PaymentTerms.NET_45: 0.8,
            PaymentTerms.MILESTONES: 0.7,
            PaymentTerms.DEPOSIT: 0.6
        }.get(offer.payment_terms, 0.5)
        
        lever_fit = (term_preference + payment_preference) / 2
        
        # Combined score
        combined_score = (price_fit * 0.6) + (lever_fit * 0.2) + (utility * 0.2)
        
        # Logistic function for probability
        # P = 1 / (1 + e^(-k*(score - threshold)))
        k = 8  # Steepness parameter
        threshold = 0.7  # 70% combined score for 50% acceptance probability
        
        probability = 1 / (1 + math.exp(-k * (combined_score - threshold)))
        
        # Adjust based on negotiation round (fatigue factor)
        round_adjustment = max(0.5, 1 - (state.round * 0.05))  # Slight increase over time
        
        return min(1.0, probability * round_adjustment)

    def _term_discount(self, policy: ExchangePolicy, current_term: int, new_term: int) -> float:
        if new_term <= current_term:
            return 0.0
        delta = new_term - current_term
        if delta in policy.term_trade:
            return policy.term_trade[delta]
        base = policy.term_trade.get(12, 0.0)
        return base * (delta / 12)

    def _payment_term_days(self, terms: PaymentTerms) -> int:
        return {
            PaymentTerms.NET_15: 15,
            PaymentTerms.NET_30: 30,
            PaymentTerms.NET_45: 45,
            PaymentTerms.MILESTONES: 30,
            PaymentTerms.DEPOSIT: 0,
        }.get(terms, 30)

    def _pv_discount_pct(
        self,
        prev_price: float,
        previous_terms: PaymentTerms,
        new_terms: PaymentTerms,
        annual_rate: float = 0.12,
    ) -> float:
        prev_days = self._payment_term_days(previous_terms)
        new_days = self._payment_term_days(new_terms)
        if prev_days <= new_days or prev_price <= 0:
            return 0.0
        delta_days = prev_days - new_days
        benefit = self.pv_benefit(prev_price, delta_days, annual_rate)
        return min(max(benefit / prev_price, 0.0), 0.25)

    def enforce_exchange_requirements(
        self,
        policy: ExchangePolicy,
        previous: OfferComponents | None,
        current: OfferComponents,
        vendor: VendorProfile,
    ) -> List[str]:
        if previous is None:
            return []

        notes: List[str] = []
        prev_price = previous.unit_price
        floor = vendor.guardrails.price_floor or 0.0

        # Term trade enforcement
        term_discount = self._term_discount(policy, previous.term_months, current.term_months)
        if term_discount > 0 and prev_price > 0:
            required_price = prev_price * (1 - term_discount)
            if required_price < floor:
                required_price = floor
                notes.append(
                    "Term trade constrained by vendor floor"
                )
            if current.unit_price > required_price + 0.01:
                current.unit_price = round(required_price, 2)
                notes.append(
                    f"Applied term trade discount ≥{term_discount:.1%} for +{current.term_months - previous.term_months}mo"
                )

        # Payment term compensation
        prev_offset = policy.payment_trade.get(previous.payment_terms, 0.0)
        new_offset = policy.payment_trade.get(current.payment_terms, 0.0)
        delta_offset = new_offset - prev_offset
        if abs(delta_offset) > 1e-6 and prev_price > 0:
            pv_required = 0.0
            if delta_offset > 0:
                pv_required = self._pv_discount_pct(prev_price, previous.payment_terms, current.payment_terms)
            required_pct = delta_offset
            if delta_offset > 0:
                required_pct = max(delta_offset, pv_required)
                required_price = prev_price * (1 - required_pct)
                if required_price < floor:
                    required_price = floor
                    notes.append("Payment discount constrained by vendor floor")
                if current.unit_price > required_price + 0.01:
                    current.unit_price = round(required_price, 2)
                    notes.append(
                        f"Faster payment ({previous.payment_terms.value}→{current.payment_terms.value}) enforced ≥{required_pct:.1%} price drop"
                    )
            else:
                allowed_increase = -delta_offset
                allowed_price = prev_price * (1 + allowed_increase)
                if current.unit_price > allowed_price + 0.01:
                    current.unit_price = round(allowed_price, 2)
                    notes.append(
                        f"Slower payment premium capped at {allowed_increase:.1%}"
                    )

        if current.unit_price < floor:
            current.unit_price = round(floor, 2)

        current.unit_price = round(current.unit_price, 2)
        return notes

    def _payment_discount(self, policy: ExchangePolicy, terms: PaymentTerms) -> float:
        return policy.payment_trade.get(terms, 0.0)

    def _value_add_credit(self, policy: ExchangePolicy, value_type: str) -> float:
        return policy.value_add_offsets.get(value_type, 0.0)

    def _seller_payment_preference(self, payment_terms: PaymentTerms) -> float:
        mapping = {
            PaymentTerms.NET_15: 1.0,
            PaymentTerms.NET_30: 0.9,
            PaymentTerms.NET_45: 0.7,
            PaymentTerms.MILESTONES: 0.85,
            PaymentTerms.DEPOSIT: 1.0,
        }
        return mapping.get(payment_terms, 0.7)
class NegotiationLifecycle(Enum):
    INIT = "init"
    NEGOTIATING = "negotiating"
    NO_ZOPA = "no_zopa"
    ACCEPTED = "accepted"
    DROPPED = "dropped"
    REPLAN_REQUIRED = "replan_required"


BUYER_ACCEPT_THRESHOLD = 0.75
# Allow sellers to clear deals even at absolute floor while still tracking minimal utility
SELLER_ACCEPT_THRESHOLD = 0.10
MAX_STALLED_ROUNDS = 3


class ConcessionEngine:
    """Utility to convert vendor concessions to monetary impacts."""

    def __init__(self, record_metadata: Dict[str, object]) -> None:
        self.term_trade: Dict[int, float] = {
            int(k): float(v) for k, v in record_metadata.get("term_trade", {}).items()
        }
        self.payment_trade: Dict[str, float] = {
            str(k): float(v) for k, v in record_metadata.get("payment_trade", {}).items()
        }
        self.value_add_offsets: Dict[str, float] = {
            str(k): float(v) for k, v in record_metadata.get("value_add_offsets", {}).items()
        }

    def best_effective_price(
        self,
        *,
        list_price: float,
        floor_price: float,
        seats: int,
    ) -> Tuple[float, List[str]]:
        """Evaluate combinations of levers to find the best effective price."""
        best_price = list_price
        best_applied: List[str] = []

        # Generate all possible combinations
        combinations = self._generate_combinations(list_price, seats)

        for combo_price, combo_applied in combinations:
            if combo_price >= floor_price and combo_price < best_price:
                best_price = combo_price
                best_applied = combo_applied

        return best_price, best_applied

    def _generate_combinations(self, list_price: float, seats: int) -> List[Tuple[float, List[str]]]:
        """Generate all valid combinations of concessions."""
        combinations = []

        # Start with no concessions
        combinations.append((list_price, []))

        # Single lever concessions
        # Payment concessions only
        for term, discount in self.payment_trade.items():
            if discount > 0:
                price = list_price * (1 - discount)
                applied = [f"payment:{term}:{discount:.2%}"]
                combinations.append((price, applied))

        # Term concessions only
        for delta, discount in self.term_trade.items():
            if discount > 0:
                price = list_price * (1 - discount)
                applied = [f"term:+{delta}:{discount:.2%}"]
                combinations.append((price, applied))

        # Value-add credits only
        if seats > 0 and self.value_add_offsets:
            total_credit = sum(self.value_add_offsets.values())
            per_seat_credit = total_credit / seats
            price = list_price - per_seat_credit
            applied = [f"value_add:${total_credit:.2f}"]
            combinations.append((price, applied))

        # Combined lever concessions
        # Payment + Term combinations
        for term_key, payment_discount in self.payment_trade.items():
            if payment_discount <= 0:
                continue
            for delta, term_discount in self.term_trade.items():
                if term_discount <= 0:
                    continue
                # Apply both discounts (multiplicative)
                price = list_price * (1 - payment_discount) * (1 - term_discount)
                applied = [
                    f"payment:{term_key}:{payment_discount:.2%}",
                    f"term:+{delta}:{term_discount:.2%}"
                ]
                combinations.append((price, applied))

        # Payment + Value-add combinations
        if seats > 0 and self.value_add_offsets:
            total_credit = sum(self.value_add_offsets.values())
            per_seat_credit = total_credit / seats
            for term_key, payment_discount in self.payment_trade.items():
                if payment_discount <= 0:
                    continue
                # Apply payment discount and subtract value-add credit
                price = (list_price * (1 - payment_discount)) - per_seat_credit
                applied = [
                    f"payment:{term_key}:{payment_discount:.2%}",
                    f"value_add:${total_credit:.2f}"
                ]
                combinations.append((price, applied))

        # Term + Value-add combinations
        if seats > 0 and self.value_add_offsets:
            total_credit = sum(self.value_add_offsets.values())
            per_seat_credit = total_credit / seats
            for delta, term_discount in self.term_trade.items():
                if term_discount <= 0:
                    continue
                # Apply term discount and subtract value-add credit
                price = (list_price * (1 - term_discount)) - per_seat_credit
                applied = [
                    f"term:+{delta}:{term_discount:.2%}",
                    f"value_add:${total_credit:.2f}"
                ]
                combinations.append((price, applied))

        # Triple combinations (Payment + Term + Value-add)
        if seats > 0 and self.value_add_offsets:
            total_credit = sum(self.value_add_offsets.values())
            per_seat_credit = total_credit / seats

            # Limit to top combinations to keep search manageable
            top_payment_options = sorted(
                [(k, v) for k, v in self.payment_trade.items() if v > 0],
                key=lambda x: x[1], reverse=True
            )[:2]  # Top 2 payment options

            top_term_options = sorted(
                [(k, v) for k, v in self.term_trade.items() if v > 0],
                key=lambda x: x[1], reverse=True
            )[:2]  # Top 2 term options

            for term_key, payment_discount in top_payment_options:
                for delta, term_discount in top_term_options:
                    # Apply all three: payment discount, term discount, and value-add credit
                    price = (list_price * (1 - payment_discount) * (1 - term_discount)) - per_seat_credit
                    applied = [
                        f"payment:{term_key}:{payment_discount:.2%}",
                        f"term:+{delta}:{term_discount:.2%}",
                        f"value_add:${total_credit:.2f}"
                    ]
                    combinations.append((price, applied))

        return combinations
