"""
DEPRECATED: This in-memory event bus is deprecated.
Use the Redis-backed event bus from src.procur.events.bus instead.

This module is kept for backward compatibility with workflow orchestration
but will be removed in a future version.
"""
from __future__ import annotations

import warnings
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Callable, Deque, Dict, List


@dataclass
class Event:
    """Simple event for in-memory orchestration (deprecated)."""
    name: str
    payload: dict


class EventBus:
    """
    DEPRECATED: In-memory event bus for workflow orchestration.
    
    Use src.procur.events.bus.EventBus for production workloads.
    This implementation is synchronous and does not persist events.
    """

    def __init__(self) -> None:
        warnings.warn(
            "orchestration.EventBus is deprecated. Use events.bus.EventBus instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._subscribers: Dict[str, List[Callable[[Event], None]]] = defaultdict(list)
        self._queue: Deque[Event] = deque()

    def subscribe(self, event_name: str, handler: Callable[[Event], None]) -> None:
        self._subscribers[event_name].append(handler)

    def publish(self, event: Event) -> None:
        self._queue.append(event)
        self._dispatch()

    def _dispatch(self) -> None:
        while self._queue:
            event = self._queue.popleft()
            for handler in list(self._subscribers.get(event.name, [])):
                handler(event)
