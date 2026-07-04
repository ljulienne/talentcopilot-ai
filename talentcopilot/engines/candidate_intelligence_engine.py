
from typing import Any, Dict, List


def _get_capability_names(candidate: Any) -> List[str]:
    return [
        getattr(capability, "name", "")
        for capability in getattr(candidate, "capabilities", []) or []
        if getattr(capability, "name", "")
    ]


def _get_strengths(match_result: Any, limit: int = 5) -> List[str]:
    details = getattr(match_result, "match_details", []) or []
    strengths = [
        detail.requirement.name
        for detail in details
        if getattr(detail, "score", 0) >= 80
    ]
    return strengths[:limit]


def _get_development_areas(match_result: Any, limit: int = 5) -> List[str]:
    gaps = getattr(match_result, "gaps", []) or []
    return [gap.competency for gap in gaps][:limit]


def _get_interview_focus(match_result: Any, limit: int = 5) -> List[str]:
    questions = getattr(match_result, "interview_questions", []) or []
    return [
        question.linked_competency
        for question in questions
    ][:limit]


def _detect_languages(capabilities: List[str]) -> List[str]:
    text = " ".join(capabilities).lower()
    languages = []

    if "french" in text or "français" in text:
        languages.append("French")
    if "english" in text or "anglais" in text:
        languages.append("English")
    if "mandarin" in text or "chinese" in text or "chinois" in text:
        languages.append("Mandarin")

    return languages


def _detect_certifications(capabilities: List[str]) -> List[str]:
    keywords = ["PMP", "PHR", "SPHR", "HRIP", "Scrum", "Agile"]
    detected = []

    text = " ".join(capabilities).lower()

    for keyword in keywords:
        if keyword.lower() in text:
            detected.append(keyword)

    return detected


def _readiness(score: int) -> str:
    if score >= 85:
        return "Ready"
    if score >= 70:
        return "Interview-ready"
    if score >= 50:
        return "Needs validation"
    return "High risk"


def build_candidate_intelligence(item: Dict[str, Any]) -> Dict[str, Any]:
    candidate = item.get("candidate")
    match_result = item.get("match_result")

    if not candidate or not match_result:
        return {
            "executive_summary": "Insufficient candidate data.",
            "overall_match": 0,
            "confidence": 0,
            "readiness": "Unknown",
            "hire_recommendation": "Not recommended",
            "strengths": [],
            "development_areas": [],
            "technical_skills": [],
            "business_skills": [],
            "languages": [],
            "certifications": [],
            "risk_factors": [],
            "interview_focus": [],
            "why": "No reliable candidate intelligence could be generated."
        }

    score = getattr(match_result, "overall_score", 0)
    confidence = getattr(match_result, "confidence_score", 0)
    capabilities = _get_capability_names(candidate)
    strengths = _get_strengths(match_result)
    development_areas = _get_development_areas(match_result)
    interview_focus = _get_interview_focus(match_result)

    risk_factors = [
        gap.explanation
        for gap in getattr(match_result, "gaps", []) or []
    ]

    why = (
        f"{candidate.name} receives a match score of {score}% with {confidence}% confidence. "
        f"The strongest areas are {', '.join(strengths[:3]) if strengths else 'not clearly identified'}. "
        f"The main areas to validate are {', '.join(development_areas[:3]) if development_areas else 'limited'}."
    )

    return {
        "executive_summary": getattr(match_result, "executive_summary", ""),
        "overall_match": score,
        "confidence": confidence,
        "readiness": _readiness(score),
        "hire_recommendation": getattr(match_result, "recommendation", ""),
        "strengths": strengths,
        "development_areas": development_areas,
        "technical_skills": capabilities[:8],
        "business_skills": strengths[:5],
        "languages": _detect_languages(capabilities),
        "certifications": _detect_certifications(capabilities),
        "risk_factors": risk_factors,
        "interview_focus": interview_focus,
        "why": why,
    }


def enrich_with_candidate_intelligence(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    enriched = []

    for item in results:
        item["candidate_intelligence"] = build_candidate_intelligence(item)
        enriched.append(item)

    return enriched
