from __future__ import annotations

from typing import Any, Dict, List, Optional

from talentcopilot.storage.recruitment_store import list_recruitments, load_recruitment


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _extract_results(recruitment: Dict[str, Any]) -> List[Dict[str, Any]]:
    batch = recruitment.get("analysis_batch") or {}

    if not isinstance(batch, dict):
        return []

    results = batch.get("results") or []

    if not isinstance(results, list):
        return []

    return results


def _extract_score(result: Dict[str, Any]) -> int:
    match_result = result.get("match_result") or {}

    if isinstance(match_result, dict):
        return _safe_int(match_result.get("overall_score"))

    return _safe_int(getattr(match_result, "overall_score", 0))


def _extract_confidence(result: Dict[str, Any]) -> int:
    match_result = result.get("match_result") or {}

    if isinstance(match_result, dict):
        return _safe_int(match_result.get("confidence_score"))

    return _safe_int(getattr(match_result, "confidence_score", 0))


def _extract_candidate_name(result: Dict[str, Any]) -> str:
    candidate = result.get("candidate") or {}

    if isinstance(candidate, dict):
        return candidate.get("name") or "Unknown Candidate"

    return getattr(candidate, "name", "Unknown Candidate")


def get_workspace_statistics() -> Dict[str, Any]:
    summaries = list_recruitments()

    total_recruitments = len(summaries)
    complete_recruitments = sum(1 for item in summaries if item.get("candidate_count", 0) > 0)
    draft_recruitments = total_recruitments - complete_recruitments

    total_candidates = 0
    all_scores: List[int] = []
    all_confidences: List[int] = []
    top_candidate: Optional[Dict[str, Any]] = None

    for summary in summaries:
        recruitment_id = summary.get("id")

        if not recruitment_id:
            continue

        try:
            recruitment = load_recruitment(recruitment_id)
        except Exception:
            continue

        results = _extract_results(recruitment)
        total_candidates += len(results)

        for result in results:
            score = _extract_score(result)
            confidence = _extract_confidence(result)

            if score > 0:
                all_scores.append(score)

            if confidence > 0:
                all_confidences.append(confidence)

            if not top_candidate or score > top_candidate["score"]:
                top_candidate = {
                    "name": _extract_candidate_name(result),
                    "score": score,
                    "recruitment_title": recruitment.get("title", "Untitled Recruitment"),
                    "recruitment_id": recruitment.get("id"),
                }

    average_match = round(sum(all_scores) / len(all_scores)) if all_scores else 0
    average_confidence = round(sum(all_confidences) / len(all_confidences)) if all_confidences else 0
    candidates_above_90 = sum(1 for score in all_scores if score >= 90)
    candidates_above_85 = sum(1 for score in all_scores if score >= 85)

    return {
        "total_recruitments": total_recruitments,
        "complete_recruitments": complete_recruitments,
        "draft_recruitments": draft_recruitments,
        "total_candidates": total_candidates,
        "average_match": average_match,
        "average_confidence": average_confidence,
        "candidates_above_90": candidates_above_90,
        "candidates_above_85": candidates_above_85,
        "top_candidate": top_candidate,
        "recent_recruitments": summaries[:5],
    }


def get_ai_insights() -> List[str]:
    stats = get_workspace_statistics()
    insights: List[str] = []

    if stats["total_recruitments"] == 0:
        return [
            "Create your first recruitment to start building your talent intelligence workspace.",
            "Once candidates are analyzed, TalentCopilot will generate portfolio-level insights here.",
        ]

    insights.append(
        f"{stats['total_recruitments']} recruitment project(s) saved in your workspace."
    )

    if stats["complete_recruitments"] > 0:
        insights.append(
            f"{stats['complete_recruitments']} recruitment(s) already include AI candidate analysis."
        )

    if stats["draft_recruitments"] > 0:
        insights.append(
            f"{stats['draft_recruitments']} recruitment(s) still need candidate analysis."
        )

    if stats["total_candidates"] > 0:
        insights.append(
            f"{stats['total_candidates']} candidate(s) analyzed across all recruitments."
        )

    if stats["candidates_above_90"] > 0:
        insights.append(
            f"{stats['candidates_above_90']} candidate(s) scored 90% or higher."
        )

    if stats["average_match"] > 0:
        insights.append(
            f"Average match score across analyzed candidates is {stats['average_match']}%."
        )

    if stats["average_confidence"] > 0:
        insights.append(
            f"Average AI confidence is {stats['average_confidence']}%."
        )

    return insights
