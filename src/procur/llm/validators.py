from __future__ import annotations

import json
from typing import Any, Callable, Dict, Optional, TypeVar

from pydantic import ValidationError

from ..models import NegotiationMessage, Request

T = TypeVar("T")


class LLMValidationError(RuntimeError):
    """Raised when LLM output fails schema validation."""


def parse_request(payload: Dict[str, Any]) -> Request:
    try:
        return Request.model_validate(payload)
    except ValidationError as exc:  # pragma: no cover - simple rethrow
        raise LLMValidationError(str(exc)) from exc


def parse_negotiation_message(payload: Dict[str, Any]) -> NegotiationMessage:
    try:
        return NegotiationMessage.model_validate(payload)
    except ValidationError as exc:
        raise LLMValidationError(str(exc)) from exc


def guarded_completion(
    generator: Callable[[], Dict[str, Any]],
    *,
    parser: Callable[[Dict[str, Any]], T],
    retries: int = 2,
) -> T:
    last_error: Optional[Exception] = None
    for _ in range(retries + 1):
        response = generator()
        content = response.get("content")
        if not isinstance(content, str):
            last_error = LLMValidationError("LLM response missing content")
            continue
        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            last_error = exc
            continue
        try:
            return parser(payload)
        except LLMValidationError as exc:
            last_error = exc
    if last_error:
        raise LLMValidationError(str(last_error))
    raise LLMValidationError("Unknown LLM validation failure")
