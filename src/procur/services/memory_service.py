from __future__ import annotations

from typing import Dict, Iterable, Optional

from ..models import NegotiationMemory, RoundMemory


class MemoryService:
    """Persists structured negotiation memories for retrieval/training."""

    def __init__(self) -> None:
        self._store: Dict[tuple[str, str], NegotiationMemory] = {}

    def start_session(
        self,
        request_id: str,
        vendor_id: str,
        *,
        scenario_tags: Optional[Iterable[str]] = None,
    ) -> NegotiationMemory:
        key = (request_id, vendor_id)
        if key not in self._store:
            memory = NegotiationMemory(
                request_id=request_id,
                vendor_id=vendor_id,
                scenario_tags=list(scenario_tags or []),
            )
            self._store[key] = memory
        else:
            memory = self._store[key]
            if scenario_tags:
                existing = set(memory.scenario_tags)
                for tag in scenario_tags:
                    if tag not in existing:
                        memory.scenario_tags.append(tag)
        return memory

    def record_round(self, round_memory: RoundMemory) -> None:
        session = self.start_session(
            round_memory.request_id,
            round_memory.vendor_id,
        )
        session.add_round(round_memory)

    def finalize_session(
        self,
        request_id: str,
        vendor_id: str,
        *,
        outcome: str,
        savings: Optional[float] = None,
    ) -> None:
        session = self.start_session(request_id, vendor_id)
        session.finalize(outcome, savings)

    def get_memory(self, request_id: str, vendor_id: str) -> Optional[NegotiationMemory]:
        return self._store.get((request_id, vendor_id))

    def all_memories(self) -> list[NegotiationMemory]:
        return list(self._store.values())

    def clear(self) -> None:
        self._store.clear()
