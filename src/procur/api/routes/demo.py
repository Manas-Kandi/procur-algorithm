from __future__ import annotations

"""Demo endpoints that generate mock negotiations from the seed catalog.

These are intentionally schema-compatible with the frontend types in
`frontend/src/types/index.ts` (NegotiationSession, Offer, OfferComponents, etc.).

They do NOT persist to the database. Data is stored in-memory for the
server process lifetime only, suitable for demos.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter

from ...data.seeds_loader import build_vendor_profiles, load_seed_catalog
from ...models import (
    Offer,
    OfferComponents,
    Request,
    RequestType,
    VendorProfile,
)
from ...services.negotiation_engine import (
    NegotiationEngine,
    NegotiationStrategy,
    SellerStrategy,
    VendorNegotiationState,
)
from ...services.policy_engine import PolicyEngine
from ...services.scoring_service import ScoringService


router = APIRouter(prefix="/demo/negotiations", tags=["Demo Negotiations"])


# In-memory store: request_id -> List[NegotiationSession-like dict]
_SESSIONS: Dict[str, List[Dict[str, Any]]] = {}
_SESSION_INDEX: Dict[str, Dict[str, Any]] = {}


def _iso(dt: datetime) -> str:
    return dt.isoformat() + "Z"


def _default_request(request_id: str) -> Request:
    """Create a reasonable demo Request model."""
    return Request(
        request_id=request_id,
        requester_id="demo-user",
        type=RequestType.SAAS,
        description="Need 100 CRM seats • Budget $1,000/seat/year • SOC2 required",
        specs={"features": ["crm", "api", "analytics"], "max_term_months": 36},
        quantity=100,
        budget_min=80000.0,
        budget_max=110000.0,
        currency="USD",
        must_haves=["crm", "api"],
        compliance_requirements=["SOC2"],
        billing_cadence="per_seat_per_year",
        status="negotiating",
    )


def _initial_buyer_offer(vendor: VendorProfile, request: Request) -> OfferComponents:
    # Use vendor's 100-seat tier if present as baseline; otherwise fall back to any tier or 12mo list
    baseline = vendor.price_tiers.get("100") or next(iter(vendor.price_tiers.values()), 1000.0)
    unit_price = max(baseline * 0.9, (vendor.guardrails.price_floor or baseline * 0.8) + 20)  # anchor but above floor
    return OfferComponents(
        unit_price=round(unit_price, 2),
        currency=request.currency,
        quantity=request.quantity,
        term_months=12,
        payment_terms="Net30",  # pydantic will coerce to PaymentTerms
        one_time_fees={},
        notes="Initial anchor from buyer agent",
    )


def _to_front_offer(
    *,
    engine: NegotiationEngine,
    scoring: ScoringService,
    vendor: VendorProfile,
    request: Request,
    components: OfferComponents,
    vendor_id: str,
    request_id: str,
) -> Dict[str, Any]:
    score = scoring.score_offer(vendor, components, request)
    # Clamp utility to [0,1] for front-end progress bars
    try:
        score.utility = max(0.0, min(1.0, float(score.utility)))
    except Exception:
        pass
    offer = Offer(
        offer_id=f"offer-{uuid.uuid4().hex[:10]}",
        request_id=request_id,
        vendor_id=vendor_id,
        components=components,
        score=score,
        confidence=0.7,
        accepted=False,
    )
    return offer.model_dump()


def _seller_counter(
    *,
    engine: NegotiationEngine,
    state: VendorNegotiationState,
    buyer_offer: OfferComponents,
) -> OfferComponents:
    # Select a seller strategy and generate counter
    strat: SellerStrategy = engine.determine_seller_strategy(state, buyer_offer)
    counter = engine.generate_seller_counter(strat, buyer_offer, state)
    return counter


def _buyer_counter(
    *,
    engine: NegotiationEngine,
    state: VendorNegotiationState,
    request: Request,
    seller_offer: OfferComponents,
) -> OfferComponents:
    # Pick buyer strategy and generate a target bundle, then convert to components
    strat: NegotiationStrategy = engine.determine_buyer_strategy(state, seller_offer)
    bundle = engine.generate_target_bundle(strat, request, seller_offer, state)
    return OfferComponents(
        unit_price=round(bundle.price, 2),
        currency=seller_offer.currency,
        quantity=seller_offer.quantity,
        term_months=bundle.term_months or seller_offer.term_months,
        payment_terms=bundle.payment_terms.value if hasattr(bundle.payment_terms, "value") else str(bundle.payment_terms),
        one_time_fees={},
        notes=f"Buyer counter via {strat.value}",
    )


def _score_components_dict(scoring: ScoringService, components: OfferComponents) -> Dict[str, float]:
    # Simple proxy scores; detailed sensitivity needs OfferScore which we compute per-offer
    tco = scoring.compute_tco(components)
    return {"tco": float(round(tco, 2))}


def _build_messages(
    *,
    engine: NegotiationEngine,
    scoring: ScoringService,
    vendor: VendorProfile,
    request: Request,
) -> tuple[List[Dict[str, Any]], Dict[str, Any], int]:
    """Run a compact 2–3 round exchange and return (messages, best_offer, current_round)."""
    # Initialize state
    state = VendorNegotiationState(vendor=vendor, round=1)

    messages: List[Dict[str, Any]] = []

    # Round 1: Buyer anchor
    buyer_v1 = _initial_buyer_offer(vendor, request)
    messages.append(
        {
            "actor": "buyer",
            "round": 1,
            "proposal": buyer_v1.model_dump(),
            "justification_bullets": [
                "Aggressive price anchor to set range",
                "12-month term keeps optionality",
            ],
            "machine_rationale": {
                "score_components": _score_components_dict(scoring, buyer_v1),
                "constraints_respected": ["budget_window"],
                "concession_taken": "price_adjustment",
            },
            "next_step_hint": "counter",
        }
    )

    # Seller counter
    seller_c1 = _seller_counter(engine=engine, state=state, buyer_offer=buyer_v1)
    state.round = 1
    messages.append(
        {
            "actor": "seller",
            "round": 1,
            "proposal": seller_c1.model_dump(),
            "justification_bullets": [
                "Premium support and roadmap access",
                "Anchoring near published tier",
            ],
            "machine_rationale": {
                "score_components": _score_components_dict(scoring, seller_c1),
                "constraints_respected": ["vendor_floor"],
                "concession_taken": "anchor_high",
            },
            "next_step_hint": "counter",
        }
    )

    # Round 2: Buyer counter
    state.round = 2
    buyer_v2 = _buyer_counter(engine=engine, state=state, request=request, seller_offer=seller_c1)
    messages.append(
        {
            "actor": "buyer",
            "round": 2,
            "proposal": buyer_v2.model_dump(),
            "justification_bullets": [
                "Faster payment for price concession",
                "Feature-fit alignment with must-haves",
            ],
            "machine_rationale": {
                "score_components": _score_components_dict(scoring, buyer_v2),
                "constraints_respected": ["payment_terms"],
                "concession_taken": "payment_terms",
            },
            "next_step_hint": "counter",
        }
    )

    # Optional seller close-or-minimal
    state.round = 3
    seller_c2 = _seller_counter(engine=engine, state=state, buyer_offer=buyer_v2)
    messages.append(
        {
            "actor": "seller",
            "round": 3,
            "proposal": seller_c2.model_dump(),
            "justification_bullets": [
                "Meaningful movement but preserving margin",
            ],
            "machine_rationale": {
                "score_components": _score_components_dict(scoring, seller_c2),
                "constraints_respected": ["vendor_floor"],
                "concession_taken": "minimal_concession",
            },
            "next_step_hint": "counter",
        }
    )

    # Determine best offer (buyer perspective) among seller proposals
    seller_offers = [messages[1]["proposal"], messages[-1]["proposal"]]
    # Compute scores for seller offers and pick the best utility
    scored = [
        _to_front_offer(
            engine=engine,
            scoring=scoring,
            vendor=vendor,
            request=request,
            components=OfferComponents(**o),
            vendor_id=vendor.vendor_id,
            request_id=request.request_id,
        )
        for o in seller_offers
    ]
    best = max(scored, key=lambda x: x["score"]["utility"]) if scored else None
    return messages, best, 3


def _build_sessions_for_request(request_id: str) -> List[Dict[str, Any]]:
    # Load seed vendors
    seed_path = "assets/seeds.json"
    vendors = build_vendor_profiles(load_seed_catalog(seed_path))

    # Keep it interesting: pick top 3 diverse vendors
    selected: List[VendorProfile] = vendors[:3]

    # Prepare engine
    engine = NegotiationEngine(policy_engine=PolicyEngine(), scoring_service=ScoringService())
    scoring = engine.scoring_service

    # Create a synthetic request
    req = _default_request(request_id)

    sessions: List[Dict[str, Any]] = []
    now = datetime.utcnow()
    for v in selected:
        session_id = f"mock-{uuid.uuid4().hex[:12]}"
        messages, best_offer, current_round = _build_messages(
            engine=engine, scoring=scoring, vendor=v, request=req
        )
        session = {
            "session_id": session_id,
            "request_id": req.request_id,
            "vendor_id": v.vendor_id,
            "status": "active",
            "current_round": current_round,
            "messages": messages,
            "best_offer": best_offer,
            "created_at": _iso(now),
            "updated_at": _iso(now),
        }
        sessions.append(session)
        _SESSION_INDEX[session_id] = session
    return sessions


@router.post("/start/{request_id}")
def start_demo_negotiations(request_id: str) -> List[Dict[str, Any]]:
    """Generate and cache demo negotiations for a request id."""
    sessions = _build_sessions_for_request(request_id)
    _SESSIONS[request_id] = sessions
    return sessions


@router.get("/request/{request_id}")
def get_demo_negotiations_for_request(request_id: str) -> List[Dict[str, Any]]:
    """Return cached demo sessions, or generate them on first access."""
    if request_id not in _SESSIONS:
        _SESSIONS[request_id] = _build_sessions_for_request(request_id)
    return _SESSIONS[request_id]


@router.get("/{session_id}")
def get_demo_negotiation(session_id: str) -> Dict[str, Any] | Dict[str, str]:
    session = _SESSION_INDEX.get(session_id)
    if not session:
        return {"detail": "Not found"}
    return session
