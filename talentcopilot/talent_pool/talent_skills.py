from __future__ import annotations

from typing import Any, Dict, List


SKILL_KEYWORDS = {
    "HRIS": ["hris", "sirh", "workday", "successfactors", "sap sf", "oracle hcm", "sedit", "talentsoft"],
    "Payroll": ["payroll", "paie", "paye", "salary", "compensation"],
    "Project Management": ["project", "implementation", "deployment", "rollout", "migration", "pmp", "agile"],
    "Data": ["power bi", "tableau", "dashboard", "reporting", "analytics", "kpi", "excel"],
    "Integration": ["api", "interface", "integration", "middleware", "etl", "automation"],
    "Change Management": ["change management", "training", "adoption", "stakeholder", "communication"],
    "Recruitment": ["recruitment", "talent acquisition", "ats", "candidate", "sourcing"],
    "Languages": ["english", "french", "mandarin", "chinese", "spanish"],
}


def _collect_text_from_history(talent: Dict[str, Any]) -> str:
    parts: List[str] = []

    for record in talent.get("application_history", []) or []:
        parts.append(str(record.get("recruitment_title", "")))
        parts.append(str(record.get("recommendation", "")))
        parts.append(str(record.get("executive_summary", "")))

    return " ".join(parts).lower()


def detect_skills(talent: Dict[str, Any]) -> Dict[str, List[str]]:
    text = _collect_text_from_history(talent)

    detected: Dict[str, List[str]] = {}

    for category, keywords in SKILL_KEYWORDS.items():
        matches = []

        for keyword in keywords:
            if keyword.lower() in text:
                matches.append(keyword)

        if matches:
            detected[category] = sorted(set(matches))

    return detected


def calculate_skill_coverage(talent: Dict[str, Any]) -> int:
    detected = detect_skills(talent)

    if not detected:
        return 0

    detected_categories = len(detected)
    total_categories = len(SKILL_KEYWORDS)

    return round((detected_categories / total_categories) * 100)


def enrich_talent_with_skills(talent: Dict[str, Any]) -> Dict[str, Any]:
    enriched = dict(talent)

    enriched["detected_skills"] = detect_skills(talent)
    enriched["skill_coverage"] = calculate_skill_coverage(talent)

    return enriched


def enrich_talents_with_skills(talents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [enrich_talent_with_skills(talent) for talent in talents]
