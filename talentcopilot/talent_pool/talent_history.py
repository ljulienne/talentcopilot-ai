from __future__ import annotations

from typing import Any, Dict, List


def build_application_record(
    recruitment: Dict[str, Any],
    result: Dict[str, Any],
) -> Dict[str, Any]:
    match = result.get("match_result") or {}
    candidate = result.get("candidate") or {}

    if not isinstance(match, dict):
        match = vars(match)

    if not isinstance(candidate, dict):
        candidate = vars(candidate)

    return {
        "recruitment_id": recruitment.get("id"),
        "recruitment_title": recruitment.get("title"),
        "candidate_name": candidate.get("name", "Unknown Candidate"),
        "score": int(match.get("overall_score", 0) or 0),
        "confidence": int(match.get("confidence_score", 0) or 0),
        "recommendation": match.get("recommendation"),
        "executive_summary": match.get("executive_summary"),
        "updated_at": recruitment.get("updated_at"),
    }


def merge_application_history(
    existing_history: List[Dict[str, Any]],
    new_record: Dict[str, Any],
) -> List[Dict[str, Any]]:
    recruitment_id = new_record.get("recruitment_id")

    history = [
        record for record in existing_history
        if record.get("recruitment_id") != recruitment_id
    ]

    history.append(new_record)

    return sorted(
        history,
        key=lambda item: item.get("updated_at") or "",
        reverse=True,
    )
