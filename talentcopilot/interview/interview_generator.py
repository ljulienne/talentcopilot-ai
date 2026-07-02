from __future__ import annotations

from typing import Any, Dict, List

from talentcopilot.talent_pool.talent_skills import detect_skills


def _history(talent: Dict[str, Any]) -> List[Dict[str, Any]]:
    history = talent.get("application_history") or []
    return history if isinstance(history, list) else []


def _latest_summary(talent: Dict[str, Any]) -> str:
    history = _history(talent)

    if not history:
        return ""

    latest = max(history, key=lambda item: item.get("updated_at") or "")
    return latest.get("executive_summary") or ""


def _best_recommendation(talent: Dict[str, Any]) -> str:
    history = _history(talent)

    if not history:
        return "-"

    best = max(history, key=lambda item: int(item.get("score", 0) or 0))
    return best.get("recommendation") or "-"


def generate_interview_guide(talent: Dict[str, Any]) -> Dict[str, Any]:
    name = talent.get("name", "Unknown Candidate")
    skills = detect_skills(talent)
    summary = _latest_summary(talent)
    recommendation = _best_recommendation(talent)

    technical_questions = []
    behavioral_questions = [
        "Can you describe a situation where you had to influence stakeholders with different priorities?",
        "Tell me about a project where you had to manage ambiguity or changing requirements.",
        "Can you give an example of how you handled resistance to change?",
    ]
    risk_validation_questions = []
    role_fit_questions = [
        "What type of role or environment helps you perform at your best?",
        "Which responsibilities in this position are the most attractive to you?",
        "What would you need to succeed in the first 90 days?",
    ]

    if "HRIS" in skills:
        technical_questions.append(
            "Can you describe an HRIS implementation or optimization project you contributed to?"
        )

    if "Payroll" in skills:
        technical_questions.append(
            "How have you managed payroll-related requirements, controls or integrations?"
        )

    if "Data" in skills:
        technical_questions.append(
            "Can you explain how you have used reporting, dashboards or KPIs to support HR decisions?"
        )

    if "Integration" in skills:
        technical_questions.append(
            "Can you describe your experience with system integrations, APIs, interfaces or middleware?"
        )

    if "Project Management" in skills:
        technical_questions.append(
            "How do you structure an HR technology project from scoping to deployment?"
        )

    if "Change Management" in skills:
        technical_questions.append(
            "How do you drive adoption when users are resistant to a new HR process or tool?"
        )

    if not technical_questions:
        technical_questions.append(
            "Can you walk me through the most relevant project or experience in your background for this role?"
        )

    if talent.get("average_confidence", 0) < 80:
        risk_validation_questions.append(
            "Some parts of the profile may require validation. Can you clarify the experiences most relevant to this role?"
        )

    if talent.get("average_score", 0) < 75:
        risk_validation_questions.append(
            "Which requirements of this role do you feel are outside your strongest experience?"
        )

    if "payroll" not in summary.lower():
        risk_validation_questions.append(
            "Can you clarify your level of exposure to payroll processes or payroll integrations?"
        )

    if "api" not in summary.lower() and "integration" not in summary.lower():
        risk_validation_questions.append(
            "Can you clarify your experience with system integrations, data flows or APIs?"
        )

    return {
        "candidate_name": name,
        "best_recommendation": recommendation,
        "technical_questions": technical_questions[:5],
        "behavioral_questions": behavioral_questions[:5],
        "risk_validation_questions": risk_validation_questions[:5],
        "role_fit_questions": role_fit_questions[:5],
        "interview_focus": [
            "Validate the candidate's strongest experience against the role requirements.",
            "Clarify any gaps detected in previous AI assessments.",
            "Assess communication, stakeholder management and delivery ownership.",
            "Confirm motivation, availability and salary expectations.",
        ],
    }
