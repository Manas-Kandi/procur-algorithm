from __future__ import annotations

import re
from typing import Dict, Iterable, List, Sequence, Tuple

from ..services.evaluation import FEATURE_SYNONYMS, normalize_feature_token

CONTROL_CHARS = re.compile(r"[\x00-\x1F\x7F-\x9F]")


def _strip_control(text: str) -> str:
    cleaned = CONTROL_CHARS.sub(" ", text)
    return " ".join(cleaned.split())


def sanitize_text(value: str, *, remove_prefixes: Sequence[str] = ()) -> Tuple[str, List[str]]:
    text = _strip_control(value or "")
    if not text:
        return "", []

    removed: List[str] = []
    working = text
    lowered = working.lower()
    for prefix in remove_prefixes:
        normalized_prefix = prefix.lower()
        if lowered.startswith(normalized_prefix):
            removed.append(working[: len(prefix)])
            working = working[len(prefix) :].lstrip()
            lowered = working.lower()

    return working, removed


def sanitize_comma_separated_features(
    value: str,
    *,
    remove_prefixes: Sequence[str] = (),
    allowed_features: Iterable[str] | None = None,
) -> Tuple[List[str], Dict[str, List[str]]]:
    sanitized_text, removed_prefixes = sanitize_text(value, remove_prefixes=remove_prefixes)
    if not sanitized_text:
        return [], {"dropped_tokens": [], "removed_prefixes": removed_prefixes}

    allowed = {normalize_feature_token(item) for item in allowed_features or ()}
    tokens = [token.strip() for token in sanitized_text.split(",")]

    recognised: List[str] = []
    dropped: List[str] = []

    for token in tokens:
        if not token:
            continue

        canonical = normalize_feature_token(token)
        if allowed and canonical not in allowed:
            dropped.append(token)
            continue

        # Guardrail: only accept tokens that map to a known canonical feature
        if canonical in FEATURE_SYNONYMS or canonical in allowed:
            recognised.append(canonical)
        elif any(canonical == normalize_feature_token(variant) for variants in FEATURE_SYNONYMS.values() for variant in variants):
            recognised.append(canonical)
        else:
            dropped.append(token)

    # Deduplicate while preserving order
    seen = set()
    unique_ordered = []
    for feat in recognised:
        if feat not in seen:
            seen.add(feat)
            unique_ordered.append(feat)

    metadata = {
        "dropped_tokens": dropped,
        "removed_prefixes": removed_prefixes,
        "raw": value,
        "sanitized_text": sanitized_text,
    }
    return unique_ordered, metadata


def sanitize_simple_list(value: str, *, remove_prefixes: Sequence[str] = ()) -> Tuple[List[str], Dict[str, List[str]]]:
    sanitized_text, removed_prefixes = sanitize_text(value, remove_prefixes=remove_prefixes)
    if not sanitized_text:
        return [], {"dropped_tokens": [], "removed_prefixes": removed_prefixes}

    tokens = [token.strip() for token in sanitized_text.split(",") if token.strip()]
    metadata = {
        "dropped_tokens": [],
        "removed_prefixes": removed_prefixes,
        "raw": value,
        "sanitized_text": sanitized_text,
    }
    return tokens, metadata


def collect_allowed_feature_canonicals() -> List[str]:
    canonicals = set()
    for canonical, variants in FEATURE_SYNONYMS.items():
        canonicals.add(normalize_feature_token(canonical))
        for variant in variants:
            canonicals.add(normalize_feature_token(variant))
    return sorted(canonicals)

