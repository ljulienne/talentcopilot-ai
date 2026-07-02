from __future__ import annotations

from typing import Any, Dict, List


def build_semantic_document(talent: Dict[str, Any]) -> str:
    lines = []

    lines.append(talent.get("name", ""))

    lines.append(
        f"Talent Score: {talent.get('talent_score', 0)}"
    )

    lines.append(
        f"Average Match: {talent.get('average_score', 0)}"
    )

    lines.append(
        f"Highest Match: {talent.get('highest_score', 0)}"
    )

    lines.append(
        f"Applications: {talent.get('application_count', 0)}"
    )

    if talent.get("last_recruitment_title"):
        lines.append(
            f"Latest Recruitment: {talent['last_recruitment_title']}"
        )

    skills = talent.get("detected_skills", {}) or {}

    if skills:
        lines.append("Skills:")

        for category, values in skills.items():
            lines.append(f"{category}: {', '.join(values)}")

    financial = talent.get("financial_data", {}) or {}

    if financial:
        lines.append(
            f"Expected Salary: {financial.get('expected_salary')}"
        )

        lines.append(
            f"Budget Max: {financial.get('budget_max')}"
        )

    history = talent.get("application_history", []) or []

    for record in history:
        summary = record.get("executive_summary")

        if summary:
            lines.append(summary)

    return "\n".join(lines)


def build_semantic_index(
    talents: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    index = []

    for talent in talents:
        index.append(
            {
                "candidate_key": talent.get("candidate_key"),
                "name": talent.get("name"),
                "document": build_semantic_document(talent),
                "talent": talent,
            }
        )

    return index
