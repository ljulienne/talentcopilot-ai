
from typing import Any, Dict, List


DEFAULT_WEIGHTS = {
    "skills": 0.35,
    "experience": 0.20,
    "hris_expertise": 0.15,
    "languages": 0.10,
    "certifications": 0.05,
    "leadership": 0.05,
    "risk": 0.05,
    "confidence": 0.05,
}


def _safe_score(value: Any) -> int:
    try:
        return max(0, min(round(float(value)), 100))
    except (TypeError, ValueError):
        return 0


def _capability_text(candidate: Any) -> str:
    capabilities = getattr(candidate, "capabilities", []) or []
    return " ".join(getattr(cap, "name", "") for cap in capabilities).lower()


def _has_any(text: str, keywords: List[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def build_weighted_ranking(item: Dict[str, Any], weights: Dict[str, float] | None = None) -> Dict[str, Any]:
    weights = weights or DEFAULT_WEIGHTS

    candidate = item.get("candidate")
    match = item.get("match_result")

    if not candidate or not match:
        return {
            "weighted_ranking_score": 0,
            "criteria": {},
            "weights": weights,
            "explanation": "Insufficient data."
        }

    overall_score = _safe_score(getattr(match, "overall_score", 0))
    confidence = _safe_score(getattr(match, "confidence_score", 0))
    capability_text = _capability_text(candidate)

    details = getattr(match, "match_details", []) or []
    detail_scores = [_safe_score(getattr(detail, "score", 0)) for detail in details]
    skills = _safe_score(sum(detail_scores) / len(detail_scores)) if detail_scores else overall_score

    hris_expertise = overall_score if _has_any(
        capability_text,
        ["hris", "sirh", "hcm", "workday", "successfactors", "talentsoft", "payroll", "time & attendance"]
    ) else _safe_score(overall_score * 0.75)

    languages = 90 if _has_any(
        capability_text,
        ["french", "français", "english", "anglais", "mandarin", "chinese", "chinois"]
    ) else 50

    certifications = 85 if _has_any(
        capability_text,
        ["certification", "certified", "phr", "sphr", "pmp", "hrip", "scrum", "agile"]
    ) else 55

    leadership = 85 if _has_any(
        capability_text,
        ["leadership", "management", "stakeholder", "project management", "change management"]
    ) else 60

    gaps = getattr(match, "gaps", []) or []
    high_gaps = sum(1 for gap in gaps if getattr(gap, "severity", "").lower() == "high")
    medium_gaps = sum(1 for gap in gaps if getattr(gap, "severity", "").lower() == "medium")
    risk = _safe_score(100 - high_gaps * 25 - medium_gaps * 12)

    criteria = {
        "skills": skills,
        "experience": overall_score,
        "hris_expertise": hris_expertise,
        "languages": languages,
        "certifications": certifications,
        "leadership": leadership,
        "risk": risk,
        "confidence": confidence,
    }

    weighted_score = round(
        sum(criteria[key] * weights.get(key, 0) for key in criteria)
    )

    return {
        "weighted_ranking_score": weighted_score,
        "criteria": criteria,
        "weights": weights,
        "explanation": (
            f"Weighted ranking score is {weighted_score}%, based on skills, experience, "
            f"HRIS expertise, languages, certifications, leadership, risk and confidence."
        )
    }


def enrich_with_weighted_ranking(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    enriched = []

    for item in results:
        item["weighted_ranking"] = build_weighted_ranking(item)
        enriched.append(item)

    return enriched
