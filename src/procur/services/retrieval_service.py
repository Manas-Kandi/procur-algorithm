from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Tuple

from ..models import NegotiationMemory


class RetrievalResult:
    """Lightweight container for retrieved exemplar memories."""

    def __init__(self, memory: NegotiationMemory, score: float) -> None:
        self.memory = memory
        self.score = score

    def to_context_snippet(self) -> Dict[str, object]:
        rounds = [
            {
                "round": r.round_number,
                "strategy": r.strategy,
                "lever": r.selected.primary_lever,
                "decision": r.decision.value,
                "delta_utility": r.delta_utility,
                "delta_tco": r.delta_tco,
            }
            for r in self.memory.rounds[-3:]
        ]
        return {
            "vendor_id": self.memory.vendor_id,
            "tags": self.memory.scenario_tags,
            "outcome": self.memory.outcome,
            "savings": self.memory.savings,
            "rounds": rounds,
        }


class InMemoryVectorStore:
    """Tag-based retrieval fallback when embeddings are unavailable."""

    def __init__(self) -> None:
        self._entries: List[Tuple[NegotiationMemory, set[str]]] = []

    def add(self, memory: NegotiationMemory) -> None:
        tags = set(memory.scenario_tags)
        self._entries.append((memory, tags))

    def query(self, tags: Iterable[str], k: int = 3) -> List[RetrievalResult]:
        query_tags = set(tags)
        if not query_tags:
            query_tags = {"general"}
        scored: List[Tuple[NegotiationMemory, float]] = []
        for memory, mem_tags in self._entries:
            intersection = len(query_tags & mem_tags)
            if not intersection:
                continue
            union = len(query_tags | mem_tags) or 1
            score = intersection / union
            scored.append((memory, score))
        scored.sort(key=lambda item: item[1], reverse=True)
        return [RetrievalResult(memory=item[0], score=item[1]) for item in scored[:k]]


class RetrievalService:
    """High-level retrieval helper with pluggable vector store."""

    def __init__(self, vector_store: Optional[InMemoryVectorStore] = None) -> None:
        self.vector_store = vector_store or InMemoryVectorStore()
        self._cache: Dict[str, List[RetrievalResult]] = defaultdict(list)

    def register_memory(self, memory: NegotiationMemory) -> None:
        self.vector_store.add(memory)
        cache_key = self._cache_key(memory.scenario_tags)
        self._cache.pop(cache_key, None)

    def retrieve(self, tags: Iterable[str], k: int = 3) -> List[RetrievalResult]:
        cache_key = self._cache_key(tags)
        if cache_key in self._cache and self._cache[cache_key]:
            return self._cache[cache_key][:k]
        results = self.vector_store.query(tags, k=k)
        self._cache[cache_key] = results
        return results

    def exemplar_context(self, tags: Iterable[str], k: int = 3) -> List[Dict[str, object]]:
        return [result.to_context_snippet() for result in self.retrieve(tags, k=k)]

    def _cache_key(self, tags: Iterable[str]) -> str:
        return "|".join(sorted(set(tags)))
