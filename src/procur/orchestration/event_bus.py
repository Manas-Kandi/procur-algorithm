from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Callable, Deque, Dict, List


@dataclass
class Event:
    name: str
    payload: dict


class EventBus:
    """In-memory event bus placeholder for workflow orchestration."""

    def __init__(self) -> None:
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
