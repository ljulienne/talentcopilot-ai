from __future__ import annotations

from typing import Any, Dict, List

from talentcopilot.semantic.lexical_search import LexicalSearchEngine
from talentcopilot.semantic.search_engine import SearchEngine


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def summarize_talent(talent: Dict[str, Any]) -> Dict[str, Any]:
    financial = talent.get("financial_data", {}) or {}
    skills = talent.get("detected_skills", {}) or {}

    return {
        "name": talent.get("name", "Unknown Candidate"),
        "candidate_key": talent.get("candidate_key"),
        "talent_score": talent.get("talent_score", 0),
        "average_score": talent.get("average_score", 0),
        "highest_score": talent.get("highest_score", 0),
        "average_confidence": talent.get("average_confidence", 0),
        "application_count": talent.get("application_count", 0),
        "progression_trend": talent.get("progression_trend", "Not enough history"),
        "last_recruitment_title": talent.get("last_recruitment_title"),
        "skills": skills,
        "financial_data": {
            "budget_min": financial.get("budget_min"),
            "budget_max": financial.get("budget_max"),
            "expected_salary": financial.get("expected_salary"),
            "currency": financial.get("currency"),
        },
    }


def build_recruiter_context(
    question: str,
    talents: List[Dict[str, Any]],
    local_response: Dict[str, Any] | None = None,
    max_talents: int = 10,
    search_engine: SearchEngine | None = None,
) -> Dict[str, Any]:
    safe_talents = _safe_list(talents)
    engine = search_engine or LexicalSearchEngine()

    semantic_results = engine.search(
        talents=safe_talents,
        query=question,
        top_k=max_talents,
    )

    if semantic_results:
        selected_talents = [result["talent"] for result in semantic_results]
    else:
        selected_talents = safe_talents[:max_talents]

    summarized_talents = [
        summarize_talent(talent)
        for talent in selected_talents
    ]

    return {
        "question": question,
        "talent_count": len(safe_talents),
        "selected_talent_count": len(selected_talents),
        "talents": summarized_talents,
        "local_response": local_response or {},
        "search_engine": engine.__class__.__name__,
        "instructions": {
            "role": "Senior Recruitment Consultant",
            "tone": "professional, concise, evidence-based",
            "rules": [
                "Do not invent candidate information.",
                "Base the answer only on the provided TalentCopilot context.",
                "Explain recommendations clearly.",
                "Highlight risks, gaps or budget concerns when relevant.",
                "When data is missing, say that the data is not available.",
            ],
        },
    }


def format_context_for_prompt(context: Dict[str, Any]) -> str:
    lines = []

    lines.append("You are TalentCopilot, an Enterprise AI Recruitment Intelligence assistant.")
    lines.append("")
    lines.append(f"User question: {context.get('question', '')}")
    lines.append("")
    lines.append("Local engine response:")
    local_response = context.get("local_response", {})
    lines.append(f"Title: {local_response.get('title', '-')}")
    lines.append(f"Answer: {local_response.get('answer', '-')}")
    lines.append("")
    lines.append(f"Talent count: {context.get('talent_count', 0)}")
    lines.append(f"Relevant talents selected: {context.get('selected_talent_count', 0)}")
    lines.append(f"Search engine: {context.get('search_engine', '-')}")
    lines.append("")
    lines.append("Talent summaries:")

    for talent in context.get("talents", []):
        lines.append(
            "- "
            f"{talent.get('name')} | "
            f"Talent Score: {talent.get('talent_score')}% | "
            f"Average Match: {talent.get('average_score')}% | "
            f"Highest Match: {talent.get('highest_score')}% | "
            f"Confidence: {talent.get('average_confidence')}% | "
            f"Applications: {talent.get('application_count')} | "
            f"Progression: {talent.get('progression_trend')}"
        )

        financial = talent.get("financial_data", {}) or {}
        if financial.get("expected_salary") or financial.get("budget_max"):
            lines.append(
                f"  Financial: expected salary {financial.get('expected_salary')} "
                f"{financial.get('currency')}, budget max {financial.get('budget_max')} "
                f"{financial.get('currency')}"
            )

        skills = talent.get("skills", {}) or {}
        if skills:
            skill_parts = []
            for category, values in skills.items():
                skill_parts.append(f"{category}: {', '.join(values)}")
            lines.append("  Skills: " + " | ".join(skill_parts))

    lines.append("")
    lines.append("Response requirements:")
    for rule in context.get("instructions", {}).get("rules", []):
        lines.append(f"- {rule}")

    return "\n".join(lines)
