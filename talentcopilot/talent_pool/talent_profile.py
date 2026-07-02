from __future__ import annotations

from typing import Any, Dict, List

from talentcopilot.talent_pool.talent_history import (
    build_application_record,
    merge_application_history,
)
from talentcopilot.talent_pool.talent_index import build_candidate_key
from talentcopilot.talent_pool.talent_store import find_talent_by_key, upsert_talent_profile


def _as_dict(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    if hasattr(value, "__dict__"):
        return vars(value)
    return {}


def _get_results(recruitment: Dict[str, Any]) -> List[Dict[str, Any]]:
    batch = recruitment.get("analysis_batch") or {}

    if not isinstance(batch, dict):
        return []

    results = batch.get("results") or []

    if not isinstance(results, list):
        return []

    return results


def _average(values: List[int]) -> int:
    valid_values = [value for value in values if value > 0]

    if not valid_values:
        return 0

    return round(sum(valid_values) / len(valid_values))


def build_talent_profile_from_result(
    recruitment: Dict[str, Any],
    result: Dict[str, Any],
) -> Dict[str, Any]:
    candidate = _as_dict(result.get("candidate"))
    match = _as_dict(result.get("match_result"))

    candidate_key = build_candidate_key(candidate)
    existing = find_talent_by_key(candidate_key) or {}

    application_record = build_application_record(recruitment, result)
    history = merge_application_history(
        existing.get("application_history", []),
        application_record,
    )

    scores = [int(record.get("score", 0) or 0) for record in history]
    confidences = [int(record.get("confidence", 0) or 0) for record in history]

    profile = {
        "candidate_key": candidate_key,
        "name": candidate.get("name", "Unknown Candidate"),
        "application_count": len(history),
        "average_score": _average(scores),
        "highest_score": max(scores) if scores else 0,
        "average_confidence": _average(confidences),
        "last_recruitment_title": application_record.get("recruitment_title"),
        "last_recruitment_id": application_record.get("recruitment_id"),
        "application_history": history,
    }

    return upsert_talent_profile(profile)


def index_recruitment_talents(recruitment: Dict[str, Any]) -> List[Dict[str, Any]]:
    indexed_profiles = []

    for result in _get_results(recruitment):
        indexed_profiles.append(
            build_talent_profile_from_result(recruitment, result)
        )

    return indexed_profiles
