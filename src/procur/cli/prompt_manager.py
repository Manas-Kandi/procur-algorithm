from __future__ import annotations

import sys
import threading
from contextlib import contextmanager
from typing import Iterator


class PromptManager:
    """Coordinates user prompts and background status output."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._progress_enabled = True
        self._buffer: list[str] = []

    def status(self, message: str) -> None:
        with self._lock:
            if self._progress_enabled:
                print(message, file=sys.stderr, flush=True)
            else:
                self._buffer.append(message)

    def prompt(self, message: str) -> str:
        with self._prompt_lock():
            try:
                return input(message)
            except KeyboardInterrupt:  # pragma: no cover
                print("\nExiting...", flush=True)
                raise SystemExit(0)

    @contextmanager
    def _prompt_lock(self) -> Iterator[None]:
        with self._lock:
            self._progress_enabled = False
            sys.stderr.flush()
        try:
            yield
        finally:
            with self._lock:
                self._progress_enabled = True
                for message in self._buffer:
                    print(message, file=sys.stderr, flush=True)
                self._buffer.clear()

