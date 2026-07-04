
from typing import Any, Dict, List


DEFAULT_DECISION_WEIGHTS = {
    "skills": 0.35,
    "experience": 0.20,
    "hris_expertise": 0.15,
    "languages": 0.10,
    "certifications": 0.05,
    "leadership": 0.05,
    "risk": 0.05,
    "confidence": 0.05,
}


HRIS_KEYWORDS = ["hris", "sirh", "hcm", "workday", "successfactors", "talentsoft", "payroll", "time & attendance"]
LANGUAGE_KEYWORDS = ["french", "english", "mandarin", "chinese", "français", "anglais", "chinois"]
CERTIFICATION_KEYWORDS = ["certification", "certified", "phr", "sphr", "pmp", "hrip", "scrum"]
LEADERSHIP_KEYWORDS = ["leadership", "management", "stakeholder", "project management", "change management"]


def _safe_score(value: Any, default: int = 0) -> int:
    try:
        return max(0, min(round(float(value)), 100))
    except (TypeError, ValueError):
        return default


def _capability_names(candidate: Any) -> List[str]:
    capabilities = getattr(candidate, "capabilities", []) or []
    return [getattr(cap, "name", "").lower() for cap in capabilities]


def _contains_keyword(names: List[str], keywords: List[str]) -> bool:
    text = " ".join(names)
    return any(keyword in text for keyword in keywords)


def _score_from_match_details(match_result: Any) -> int:
    details = getattr(match_result, "match_details", []) or []
    scores = [getattr(detail, "score", 0) for detail in details]

    if not scores:
        return _safe_score(getattr(match_result, "overall_score", 0))

    return _safe_score(sum(scores) / len(scores))


def _risk_score(match_result: Any) -> int:
    gaps = getattr(match_result, "gaps", []) or []

    if not gaps:
        return 100

    high_gaps = sum(1 for gap in gaps if getattr(gap, "severity", "").lower() == "high")
    medium_gaps = sum(1 for gap in gaps if getattr(gap, "severity", "").lower() == "medium")

    penalty = high_gaps * 25 + medium_gaps * 12
    return _safe_score(100 - penalty)


def evaluate_candidate_decision(item: Dict[str, Any], weights: Dict[str, float] | None = None) -> Dict[str, Any]:
    weights = weights or DEFAULT_DECISION_WEIGHTS

    candidate = item.get("candidate")
    match_result = item.get("match_result")

    if not candidate or not match_result:
        return {
            "candidate_name": "Unknown Candidate",
            "decision_score": 0,
            "criteria": {},
            "recommendation": "Not recommended",
            "explanation": "Insufficient candidate or match data."
        }

    capability_names = _capability_names(candidate)
    overall_score = _safe_score(getattr(match_result, "overall_score", 0))
    confidence_score = _safe_score(getattr(match_result, "confidence_score", 0))

    skills_score = _score_from_match_details(match_result)
    experience_score = overall_score

    hris_score = overall_score if _contains_keyword(capability_names, HRIS_KEYWORDS) else round(overall_score * 0.75)
    languages_score = 90 if _contains_keyword(capability_names, LANGUAGE_KEYWORDS) else 50
    certifications_score = 85 if _contains_keyword(capability_names, CERTIFICATION_KEYWORDS) else 55
    leadership_score = 85 if _contains_keyword(capability_names, LEADERSHIP_KEYWORDS) else 60
    risk_score = _risk_score(match_result)

    criteria = {
        "skills": skills_score,
        "experience": experience_score,
        "hris_expertise": hris_score,
        "languages": languages_score,
        "certifications": certifications_score,
        "leadership": leadership_score,
        "risk": risk_score,
        "confidence": confidence_score,
    }

    decision_score = round(
        sum(criteria[key] * weights.get(key, 0) for key in criteria)
    )

    if decision_score >= 85:
        recommendation = "Strong shortlist"
    elif decision_score >= 70:
        recommendation = "Interview"
    elif decision_score >= 50:
        recommendation = "Maybe"
    else:
        recommendation = "Not recommended"

    strongest_criteria = sorted(criteria.items(), key=lambda x: x[1], reverse=True)[:2]
    weakest_criteria = sorted(criteria.items(), key=lambda x: x[1])[:2]

    explanation = (
        f"{getattr(candidate, 'name', 'This candidate')} receives a decision score of {decision_score}%. "
        f"Strongest dimensions: {strongest_criteria[0][0]} and {strongest_criteria[1][0]}. "
        f"Main points to review: {weakest_criteria[0][0]} and {weakest_criteria[1][0]}."
    )

    return {
        "candidate_name": getattr(candidate, "name", "Unknown Candidate"),
        "decision_score": decision_score,
        "criteria": criteria,
        "weights": weights,
        "recommendation": recommendation,
        "explanation": explanation,
    }


def evaluate_batch_decisions(results: List[Dict[str, Any]], weights: Dict[str, float] | None = None) -> List[Dict[str, Any]]:
    enriched_results = []

    for item in results:
        decision = evaluate_candidate_decision(item, weights)
        item["decision"] = decision
        enriched_results.append(item)

    return enriched_results
