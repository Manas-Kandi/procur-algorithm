from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Optional

from ..models import ActorRole, MoveLog, RoundLog, UtilitySnapshot


class AuditTrailService:
    """Collects structured negotiation logs for audit and playback."""

    def __init__(self) -> None:
        self._sessions: Dict[tuple[str, str], RoundLog] = {}
        self._events: Dict[str, List[dict]] = defaultdict(list)

    def start_session(self, request_id: str, vendor_id: str) -> RoundLog:
        key = (request_id, vendor_id)
        if key not in self._sessions:
            self._sessions[key] = RoundLog(request_id=request_id, vendor_id=vendor_id)
        return self._sessions[key]

    def record_event(self, request_id: str, name: str, payload: Optional[dict] = None) -> None:
        self._events[request_id].append({"name": name, "payload": payload or {}})

    def record_move(
        self,
        request_id: str,
        vendor_id: str,
        *,
        actor: ActorRole,
        round_number: int,
        offer,
        lever: str,
        rationale: Iterable[str],
        buyer_utility: float,
        seller_utility: float,
        tco: float,
        decision=None,
        policy_notes: Optional[Iterable[str]] = None,
        guardrail_notes: Optional[Iterable[str]] = None,
        compliance_notes: Optional[Iterable[str]] = None,
        buyer_breakdown: Optional[Dict[str, float]] = None,
        seller_breakdown: Optional[Dict[str, float]] = None,
        tco_breakdown: Optional[Dict[str, float]] = None,
    ) -> None:
        session = self.start_session(request_id, vendor_id)
        move = MoveLog(
            actor=actor,
            round_number=round_number,
            offer=offer,
            lever=lever,
            rationale=list(rationale),
            utility=UtilitySnapshot(
                buyer_utility=buyer_utility,
                seller_utility=seller_utility,
                tco=tco,
                buyer_components=dict(buyer_breakdown or {}),
                seller_components=dict(seller_breakdown or {}),
                tco_breakdown=dict(tco_breakdown or {}),
            ),
            decision=decision,
            policy_notes=list(policy_notes or []),
            guardrail_notes=list(guardrail_notes or []),
            compliance_notes=list(compliance_notes or []),
        )
        session.add_move(move)

    def finalize_session(
        self,
        request_id: str,
        vendor_id: str,
        *,
        outcome: str,
        summary: Optional[Dict[str, object]] = None,
    ) -> None:
        session = self.start_session(request_id, vendor_id)
        session.mark_outcome(outcome, summary)

    def export_sessions(self, request_id: str) -> Dict[str, dict]:
        payload: Dict[str, dict] = {
            vendor_id: session.model_dump()
            for (req_id, vendor_id), session in self._sessions.items()
            if req_id == request_id
        }
        events = self._events.get(request_id, [])
        return {"round_logs": payload, "events": events}

    def clear(self) -> None:
        self._sessions.clear()
        self._events.clear()
