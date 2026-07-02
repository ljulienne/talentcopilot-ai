from __future__ import annotations

from typing import Any, Dict, List


class RecruiterAgent:
    def __init__(self, talents: List[Dict[str, Any]]):
        self.talents = talents or []

    def answer(self, question: str) -> Dict[str, Any]:
        q = question.lower().strip()

        if not q:
            return self._unknown_question()

        if any(keyword in q for keyword in ["best", "top", "strongest"]):
            return self._best_candidate()

        if any(keyword in q for keyword in ["budget", "salary", "cost", "financial"]):
            return self._budget_candidates()

        if any(keyword in q for keyword in ["skill", "skills", "competence", "competencies"]):
            return self._skills_summary()

        if any(keyword in q for keyword in ["interview", "meet", "shortlist"]):
            return self._interview_priority()

        if any(keyword in q for keyword in ["risk", "gap", "weakness"]):
            return self._risk_summary()

        return self._unknown_question()

    def _unknown_question(self) -> Dict[str, Any]:
        return {
            "title": "Question not understood",
            "answer": (
                "I can currently answer questions about:\n\n"
                "- best candidate\n"
                "- budget or salary\n"
                "- skills\n"
                "- interview priority\n"
                "- risks or gaps"
            ),
        }

    def _best_candidate(self) -> Dict[str, Any]:
        if not self.talents:
            return {
                "title": "No candidates",
                "answer": "No candidates are available in the Talent Pool yet.",
            }

        best = max(self.talents, key=lambda talent: talent.get("talent_score", 0))

        return {
            "title": "Best Candidate",
            "answer": (
                f"**{best.get('name', 'Unknown Candidate')}** is currently the strongest talent "
                f"with a Talent Score of **{best.get('talent_score', 0)}%**.\n\n"
                f"Average match: **{best.get('average_score', 0)}%** · "
                f"Highest match: **{best.get('highest_score', 0)}%** · "
                f"Average confidence: **{best.get('average_confidence', 0)}%**."
            ),
        }

    def _budget_candidates(self) -> Dict[str, Any]:
        over_budget = []
        within_budget = []

        for talent in self.talents:
            financial = talent.get("financial_data", {}) or {}
            expected = financial.get("expected_salary", 0) or 0
            maximum = financial.get("budget_max", 0) or 0
            currency = financial.get("currency", "EUR")

            if expected <= 0 or maximum <= 0:
                continue

            if expected > maximum:
                gap = expected - maximum
                over_budget.append(
                    f"- **{talent.get('name', 'Unknown Candidate')}**: "
                    f"{gap:,.0f} {currency} above budget"
                )
            else:
                within_budget.append(
                    f"- **{talent.get('name', 'Unknown Candidate')}**: within budget"
                )

        if not over_budget and not within_budget:
            return {
                "title": "Budget Analysis",
                "answer": "No financial data is available yet for the current Talent Pool.",
            }

        answer_parts = []

        if over_budget:
            answer_parts.append("Candidates above budget:\n" + "\n".join(over_budget))

        if within_budget:
            answer_parts.append("Candidates within budget:\n" + "\n".join(within_budget))

        return {
            "title": "Budget Analysis",
            "answer": "\n\n".join(answer_parts),
        }

    def _skills_summary(self) -> Dict[str, Any]:
        skills_by_category: Dict[str, set] = {}

        for talent in self.talents:
            detected = talent.get("detected_skills", {}) or {}

            for category, skills in detected.items():
                skills_by_category.setdefault(category, set()).update(skills)

        if not skills_by_category:
            return {
                "title": "Skills Summary",
                "answer": "No structured skills have been detected yet.",
            }

        lines = []

        for category, skills in sorted(skills_by_category.items()):
            lines.append(f"**{category}**: {', '.join(sorted(skills))}")

        return {
            "title": "Skills Summary",
            "answer": "\n\n".join(lines),
        }

    def _interview_priority(self) -> Dict[str, Any]:
        if not self.talents:
            return {
                "title": "Interview Priority",
                "answer": "No talent is available for interview prioritization.",
            }

        ranked = sorted(
            self.talents,
            key=lambda talent: talent.get("talent_score", 0),
            reverse=True,
        )

        lines = [
            f"{index}. **{talent.get('name', 'Unknown Candidate')}** — "
            f"{talent.get('talent_score', 0)}% Talent Score"
            for index, talent in enumerate(ranked[:5], start=1)
        ]

        return {
            "title": "Interview Priority",
            "answer": "Suggested interview order:\n\n" + "\n".join(lines),
        }

    def _risk_summary(self) -> Dict[str, Any]:
        risks = []

        for talent in self.talents:
            average_score = talent.get("average_score", 0)
            average_confidence = talent.get("average_confidence", 0)

            if average_score < 75:
                risks.append(
                    f"- **{talent.get('name', 'Unknown Candidate')}**: average match below 75%"
                )

            if average_confidence < 80:
                risks.append(
                    f"- **{talent.get('name', 'Unknown Candidate')}**: AI confidence below 80%"
                )

        if not risks:
            return {
                "title": "Risk Summary",
                "answer": "No major score or confidence risk detected in the current Talent Pool.",
            }

        return {
            "title": "Risk Summary",
            "answer": "\n".join(risks),
        }
