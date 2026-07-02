from __future__ import annotations

from typing import Any, Dict, List


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def calculate_talent_score(talent: Dict[str, Any]) -> int:
    highest_score = _safe_int(talent.get("highest_score"))
    average_score = _safe_int(talent.get("average_score"))
    average_confidence = _safe_int(talent.get("average_confidence"))

    if highest_score == 0 and average_score == 0 and average_confidence == 0:
        return 0

    return round(
        highest_score * 0.4
        + average_score * 0.4
        + average_confidence * 0.2
    )


def get_progression_trend(talent: Dict[str, Any]) -> str:
    history = talent.get("application_history") or []

    if len(history) < 2:
        return "Not enough history"

    chronological = sorted(
        history,
        key=lambda item: item.get("updated_at") or "",
    )

    first_score = _safe_int(chronological[0].get("score"))
    last_score = _safe_int(chronological[-1].get("score"))

    if last_score > first_score:
        return "Improving"

    if last_score < first_score:
        return "Declining"

    return "Stable"


def get_best_application(talent: Dict[str, Any]) -> Dict[str, Any] | None:
    history = talent.get("application_history") or []

    if not history:
        return None

    return max(history, key=lambda item: _safe_int(item.get("score")))


def get_latest_application(talent: Dict[str, Any]) -> Dict[str, Any] | None:
    history = talent.get("application_history") or []

    if not history:
        return None

    return max(history, key=lambda item: item.get("updated_at") or "")


def enrich_talent_profile(talent: Dict[str, Any]) -> Dict[str, Any]:
    enriched = dict(talent)

    enriched["talent_score"] = calculate_talent_score(talent)
    enriched["progression_trend"] = get_progression_trend(talent)
    enriched["best_application"] = get_best_application(talent)
    enriched["latest_application"] = get_latest_application(talent)

    return enriched


def enrich_talent_profiles(talents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    enriched = [enrich_talent_profile(talent) for talent in talents]

    return sorted(
        enriched,
        key=lambda item: item.get("talent_score", 0),
        reverse=True,
    )
