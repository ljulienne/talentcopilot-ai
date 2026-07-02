from __future__ import annotations

from typing import Any, Dict, List


def _as_dict(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    if hasattr(value, "__dict__"):
        return vars(value)
    return {}


def _get_match(result: Dict[str, Any]) -> Dict[str, Any]:
    return _as_dict(result.get("match_result"))


def _get_candidate(result: Dict[str, Any]) -> Dict[str, Any]:
    return _as_dict(result.get("candidate"))


def _get_match_details(match: Dict[str, Any]) -> List[Any]:
    details = match.get("match_details") or []
    return details if isinstance(details, list) else []


def _detail_to_dict(detail: Any) -> Dict[str, Any]:
    if isinstance(detail, dict):
        return detail

    requirement = getattr(detail, "requirement", None)

    return {
        "score": getattr(detail, "score", 0),
        "explanation": getattr(detail, "explanation", ""),
        "requirement": {
            "name": getattr(requirement, "name", "Requirement"),
            "importance": getattr(requirement, "importance", ""),
        },
    }


def _requirement_name(detail: Dict[str, Any]) -> str:
    requirement = detail.get("requirement") or {}

    if isinstance(requirement, dict):
        return requirement.get("name", "Requirement")

    return getattr(requirement, "name", "Requirement")


def explain_candidate(result: Dict[str, Any]) -> Dict[str, Any]:
    candidate = _get_candidate(result)
    match = _get_match(result)

    name = candidate.get("name", "Unknown Candidate")
    score = int(match.get("overall_score", 0) or 0)
    confidence = int(match.get("confidence_score", 0) or 0)
    recommendation = match.get("recommendation", "No recommendation available")
    executive_summary = match.get("executive_summary", "")

    details = [_detail_to_dict(item) for item in _get_match_details(match)]

    strengths = []
    risks = []
    interview_focus = []

    for detail in details:
        detail_score = int(detail.get("score", 0) or 0)
        requirement = _requirement_name(detail)
        explanation = detail.get("explanation", "")

        if detail_score >= 80:
            strengths.append(f"{requirement} — strong alignment ({detail_score}%).")
        elif detail_score < 60:
            risks.append(f"{requirement} — potential gap ({detail_score}%).")
            interview_focus.append(f"Validate {requirement.lower()} during the interview.")
        else:
            interview_focus.append(f"Explore {requirement.lower()} in more detail.")

        if explanation and detail_score < 75:
            risks.append(explanation)

    if not strengths:
        strengths.append("No major strength has been detected from the current analysis.")

    if not risks:
        risks.append("No major risk has been detected from the current analysis.")

    if not interview_focus:
        interview_focus.append("Validate motivation, availability, salary expectations and role understanding.")

    if score >= 85:
        final_assessment = "Strong Hire"
    elif score >= 70:
        final_assessment = "Interview Recommended"
    elif score >= 55:
        final_assessment = "Possible Backup Candidate"
    else:
        final_assessment = "Not Recommended at this stage"

    return {
        "candidate_name": name,
        "score": score,
        "confidence": confidence,
        "recommendation": recommendation,
        "executive_summary": executive_summary,
        "strengths": strengths[:5],
        "risks": risks[:5],
        "interview_focus": interview_focus[:5],
        "final_assessment": final_assessment,
    }
