
from typing import Any, Dict, List


def _safe_get_name(obj: Any) -> str:
    return getattr(obj, "name", "") or ""


def _safe_get_score(obj: Any) -> int:
    try:
        return int(getattr(obj, "score", 0) or 0)
    except (TypeError, ValueError):
        return 0


def build_evidence_for_candidate(item: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Build structured evidence from matching details.

    This engine does not change ranking or scoring.
    It only explains what supports each requirement.
    """

    match_result = item.get("match_result")

    if not match_result:
        return []

    evidences = []

    for detail in getattr(match_result, "match_details", []) or []:
        requirement = getattr(detail, "requirement", None)
        capability = getattr(detail, "capability", None)

        competency = _safe_get_name(requirement)
        score = _safe_get_score(detail)
        confidence = getattr(detail, "confidence", 0) or 0
        explanation = getattr(detail, "explanation", "") or ""

        if capability:
            capability_evidence = getattr(capability, "evidence", []) or []

            if capability_evidence:
                excerpts = [
                    getattr(e, "text", str(e))
                    for e in capability_evidence
                ]
            else:
                excerpts = [explanation]
        else:
            excerpts = ["No evidence detected in the candidate profile."]

        evidences.append({
            "competency": competency,
            "score": score,
            "confidence": confidence,
            "status": "supported" if score >= 80 else "partial" if score >= 50 else "missing",
            "excerpts": excerpts,
            "recommendation": (
                f"Confirm {competency} during the interview."
                if score < 85
                else f"{competency} appears well supported."
            )
        })

    return evidences


def enrich_with_evidence(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    enriched = []

    for item in results:
        item["evidence"] = build_evidence_for_candidate(item)
        enriched.append(item)

    return enriched
