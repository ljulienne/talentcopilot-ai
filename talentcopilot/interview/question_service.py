from __future__ import annotations

from typing import Iterable, Optional

from talentcopilot.interview.models import InterviewCompetency, InterviewQuestion


class InterviewQuestionService:
    """Build evidence-grounded interview questions without an LLM call.

    The service is intentionally deterministic and fast. It consumes the
    official candidate/session context and turns evidence gaps into structured
    interview probes. It never recalculates the candidate fit score.
    """

    ENGINE_VERSION = "3.1.1B"

    def build(
        self,
        competencies: list[InterviewCompetency],
        *,
        role_title: str = "the role",
        candidate: Optional[dict] = None,
        mission_requirements: Optional[Iterable[str]] = None,
    ) -> list[InterviewQuestion]:
        candidate = candidate or {}
        requirements = [str(item).strip() for item in (mission_requirements or []) if str(item).strip()]
        achievements = [str(item).strip() for item in candidate.get("achievements", []) if str(item).strip()]
        years = candidate.get("years_experience", 0)

        target_competencies = [c for c in competencies if c.validate_in_interview]
        if not target_competencies:
            target_competencies = competencies[:3]

        questions: list[InterviewQuestion] = []
        for competency in target_competencies[:6]:
            questions.append(
                self._build_question(
                    competency,
                    role_title=role_title,
                    requirements=requirements,
                    achievements=achievements,
                    years=years,
                )
            )

        return questions

    def _build_question(
        self,
        competency: InterviewCompetency,
        *,
        role_title: str,
        requirements: list[str],
        achievements: list[str],
        years,
    ) -> InterviewQuestion:
        name = competency.name
        evidence_level = str(competency.evidence_level or "Low").lower()
        matching_requirement = self._matching_requirement(name, requirements)
        evidence_excerpt = self._matching_evidence(name, achievements)

        if evidence_excerpt:
            question = (
                f"Your CV states: ‘{self._shorten(evidence_excerpt, 180)}’. "
                f"For the {role_title} mission, explain the exact scope you personally owned, "
                f"the decisions you made, the most difficult trade-off, and the measurable outcome. "
                f"How does this demonstrate {name}?"
            )
            objective = (
                f"Verify that the stated evidence demonstrates personal ownership and sufficient depth in {name}, "
                "rather than team-level participation."
            )
        elif evidence_level == "low":
            requirement_text = matching_requirement or name
            question = (
                f"The mission requires {requirement_text}, but the available CV evidence is limited. "
                f"Describe the most comparable situation in which you applied {name}. "
                "What was the context, what did you personally decide, which stakeholders were affected, "
                "and what measurable result did you deliver?"
            )
            objective = f"Resolve a material evidence gap for {name} before a hiring decision."
        else:
            question = (
                f"For the {role_title} mission, walk me through your strongest example of {name}. "
                "Separate your own contribution from the team's work, explain one difficult decision, "
                "and quantify the result."
            )
            objective = f"Confirm the depth, scale and transferability of the candidate's experience in {name}."

        experience_note = f" The CV indicates approximately {years:g} years of experience." if isinstance(years, (int, float)) and years else ""
        rationale = competency.rationale or "Current evidence requires interview validation."

        return InterviewQuestion(
            competency=name,
            question=question,
            objective=f"{objective}{experience_note} Evidence basis: {rationale}",
            expected_evidence=[
                "A specific situation with scope, scale and constraints",
                "Clear distinction between personal ownership and team contribution",
                "Decisions and trade-offs made by the candidate",
                "Stakeholders involved and how resistance or conflict was handled",
                "A measurable outcome and lessons learned",
            ],
            positive_signals=[
                "Uses precise scope, timelines, stakeholders and metrics",
                "Explains personal decisions and accountability",
                "Connects the example directly to the mission requirement",
                "Acknowledges risks, trade-offs and lessons learned",
                "Clear ownership of scope, decisions, and outcomes",
            ],
            warning_signals=[
                "Describes only collective activity with no personal ownership",
                "Cannot quantify the outcome or explain the decision process",
                "Uses generic claims that are not supported by a concrete example",
                "Example is materially smaller or less complex than the target mission",
            ],
            follow_ups=[
                "What evidence or deliverable could verify your contribution?",
                "Which stakeholder disagreed with you, and how did you respond?",
                "What would have happened if your chosen approach had failed?",
                "What would you do differently in this mission?",
            ],
        )

    def _matching_requirement(self, competency: str, requirements: list[str]) -> str:
        needle = competency.lower()
        for requirement in requirements:
            lower = requirement.lower()
            if needle in lower or lower in needle:
                return requirement
        return ""

    def _matching_evidence(self, competency: str, achievements: list[str]) -> str:
        tokens = {token for token in competency.lower().replace("/", " ").split() if len(token) > 3}
        for achievement in achievements:
            lower = achievement.lower()
            if tokens and any(token in lower for token in tokens):
                return achievement
        return achievements[0] if achievements else ""

    def _shorten(self, value: str, limit: int) -> str:
        clean = " ".join(str(value).split())
        return clean if len(clean) <= limit else clean[: limit - 1].rstrip() + "…"
