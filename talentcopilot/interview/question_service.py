from __future__ import annotations

from typing import Iterable, Optional

from talentcopilot.interview.models import InterviewCompetency, InterviewQuestion


class InterviewQuestionService:
    """Build varied evidence-grounded questions without an LLM call."""

    ENGINE_VERSION = "3.1.1C"

    def build(
        self,
        competencies: list[InterviewCompetency],
        *,
        role_title: str = "the role",
        candidate: Optional[dict] = None,
        mission_requirements: Optional[Iterable[str]] = None,
    ) -> list[InterviewQuestion]:
        candidate = candidate or {}
        requirements = [
            str(item).strip()
            for item in (mission_requirements or [])
            if str(item).strip()
        ]
        achievements = [
            str(item).strip()
            for item in candidate.get("achievements", [])
            if str(item).strip()
        ]
        years = candidate.get("years_experience", 0)

        target = [c for c in competencies if c.validate_in_interview]
        if not target:
            target = competencies[:3]

        return [
            self._build_question(
                competency,
                role_title=role_title,
                requirements=requirements,
                achievements=achievements,
                years=years,
                index=index,
            )
            for index, competency in enumerate(target[:6])
        ]

    def _build_question(
        self,
        competency: InterviewCompetency,
        *,
        role_title: str,
        requirements: list[str],
        achievements: list[str],
        years,
        index: int,
    ) -> InterviewQuestion:
        name = competency.name
        requirement = self._matching_requirement(name, requirements) or name
        evidence = self._matching_evidence(name, achievements)
        archetype = self._archetype(name, index)

        question, expected, positives, warnings, follow_ups = self._question_pack(
            archetype=archetype,
            competency=name,
            requirement=requirement,
            evidence=evidence,
            role_title=role_title,
        )

        experience_note = (
            f" The CV indicates approximately {years:g} years of experience."
            if isinstance(years, (int, float)) and years
            else ""
        )
        rationale = competency.rationale or "Current evidence requires interview validation."

        return InterviewQuestion(
            competency=name,
            question=question,
            objective=(
                f"Validate {name} using a {archetype.replace('_', ' ')} lens."
                f"{experience_note} Evidence basis: {rationale}"
            ),
            expected_evidence=expected,
            positive_signals=positives,
            warning_signals=warnings,
            follow_ups=follow_ups,
        )

    def _question_pack(
        self,
        *,
        archetype: str,
        competency: str,
        requirement: str,
        evidence: str,
        role_title: str,
    ):
        prefix = (
            f"Your CV states: ‘{self._shorten(evidence, 155)}’. "
            if evidence
            else f"The mission requires {requirement}. "
        )

        if archetype == "technical":
            return (
                prefix
                + f"Describe the most technically demanding {competency} situation you handled. "
                  "Which systems, modules, interfaces or data flows were involved, "
                  "which technical decisions did you personally make, how did you validate the solution, "
                  "what defect or limitation was hardest to resolve, and which measurable reliability, quality, or delivery result improved?",
                [
                    "Specific systems, modules and configuration scope",
                    "Testing or validation approach",
                    "Concrete technical constraint and resolution",
                    "Evidence of production quality or stability",
                ],
                [
                    "Shows clear technical ownership of design and configuration decisions",
                    "Explains architecture, configuration and validation precisely",
                    "Distinguishes design choices from vendor defaults",
                    "Shows diagnostic depth and technical accountability",
                ],
                [
                    "Cannot name the systems or modules involved",
                    "Describes only coordination with no technical understanding",
                    "No evidence of testing or quality controls",
                ],
                [
                    "Which interface or data dependency created the highest risk?",
                    "What did you reject or redesign, and why?",
                    "Which test result or production metric confirmed that your solution worked?",
                ],
            )

        if archetype == "data":
            return (
                prefix
                + f"Describe a {competency} deliverable that influenced an HR or business decision. "
                  "What source data did you personally validate, how did you ensure reliability, "
                  "which KPI mattered most, what measurable change did the analysis reveal, and what decision changed because of it?",
                [
                    "Source systems and data model",
                    "Data-quality controls",
                    "Relevant KPI definition",
                    "Decision or action enabled",
                ],
                [
                    "Shows clear ownership of data validation and KPI definitions",
                    "Explains lineage and validation checks",
                    "Chooses KPIs tied to a business decision",
                    "Shows how stakeholders used the output",
                ],
                [
                    "Focuses only on dashboard appearance",
                    "Cannot explain data quality or KPI definitions",
                    "No evidence that the analysis changed a decision",
                ],
                [
                    "Which data-quality issue could have changed the conclusion?",
                    "How did you prevent users from misinterpreting the KPI?",
                    "Which stakeholder decision was directly influenced by the result?",
                ],
            )

        if archetype == "change":
            return (
                prefix
                + f"Choose one transformation where adoption of {competency} was uncertain. "
                  "Which user groups resisted, what did you personally change in the communication or training approach, "
                  "and which measurable adoption or behavioural indicator proved that the change worked?",
                [
                    "Stakeholder segmentation",
                    "Resistance diagnosis",
                    "Targeted change actions",
                    "Adoption metrics or behavioural evidence",
                ],
                [
                    "Shows clear ownership of the change strategy and adoption actions",
                    "Names distinct populations and resistance patterns",
                    "Links interventions to measured adoption",
                    "Shows adaptation rather than generic communication",
                ],
                [
                    "Relies only on training attendance",
                    "Cannot explain resistance or stakeholder differences",
                    "No measurable adoption outcome",
                ],
                [
                    "Which population required a different approach?",
                    "What early signal showed the change plan was not working?",
                    "Which adoption metric improved after you changed the approach?",
                ],
            )

        if archetype == "stakeholder":
            return (
                prefix
                + f"For the {role_title} context, describe a situation where stakeholders had "
                  f"conflicting priorities around {competency}. Who disagreed, "
                  "how did you personally influence the decision, what framework did you use, "
                  "how did you secure commitment, and what measurable delivery or business outcome followed?",
                [
                    "Stakeholder map and competing interests",
                    "Decision criteria",
                    "Influencing approach",
                    "Documented agreement or governance outcome",
                ],
                [
                    "Shows clear ownership of stakeholder alignment and final decision-making",
                    "Explains power dynamics and competing incentives",
                    "Uses explicit criteria to arbitrate",
                    "Secures a concrete commitment or governance decision",
                ],
                [
                    "Avoids conflict rather than resolving it",
                    "Escalates without attempting influence",
                    "Cannot explain the final decision rationale",
                ],
                [
                    "Which stakeholder had the strongest veto power?",
                    "What concession did you make, and what did you protect?",
                    "How did you verify that the final commitment was translated into action?",
                ],
            )

        if archetype == "leadership":
            return (
                prefix
                + f"Give an example where you had to develop or redirect another person while "
                  f"delivering {competency}. What capability gap did you personally identify, "
                  "what did you delegate, and which measurable performance or autonomy indicator improved?",
                [
                    "Initial capability or performance gap",
                    "Delegation and coaching approach",
                    "Feedback cadence",
                    "Observable performance improvement",
                ],
                [
                    "Shows clear ownership of team development and performance improvement",
                    "Adapts coaching to the individual",
                    "Delegates meaningful responsibility with controls",
                    "Shows measurable improvement or independence",
                ],
                [
                    "Equates management with task assignment",
                    "No feedback or development approach",
                    "Cannot describe the person's progress",
                ],
                [
                    "What did you stop doing personally once the person improved?",
                    "How did you handle underperformance?",
                    "Which measurable behaviour showed that the person had become more autonomous?",
                ],
            )

        if archetype == "risk":
            return (
                prefix
                + f"Describe the highest-risk situation you encountered in {competency}. "
                  "Which early warning indicators did you personally monitor, what mitigation options "
                  "did you compare, what residual risk did you accept, and what measurable impact did the mitigation prevent or reduce?",
                [
                    "Risk statement and impact",
                    "Early warning indicators",
                    "Alternative mitigations",
                    "Residual-risk decision",
                ],
                [
                    "Shows clear ownership of risk identification, mitigation and escalation",
                    "Quantifies probability and impact",
                    "Compares options and trade-offs",
                    "Escalates with a recommendation, not just a problem",
                ],
                [
                    "Identifies the risk only after it materialised",
                    "No alternative options considered",
                    "Cannot explain residual risk acceptance",
                ],
                [
                    "Which mitigation did you reject and why?",
                    "At what threshold would you have escalated differently?",
                    "Which indicator confirmed that the residual risk remained acceptable?",
                ],
            )

        return (
            prefix
            + f"Describe one example that best proves your personal contribution to {competency}. "
              "What responsibility did you personally own, what did you deliver, "
              "and which measurable result was used to assess success?",
            [
                "Personal accountability",
                "Concrete deliverable",
                "Decision or action taken",
                "Outcome assessment",
            ],
            [
                "Shows clear ownership of the deliverable and its outcome",
                "Separates personal contribution from team activity",
                "Uses evidence to demonstrate impact",
            ],
            [
                "Uses only collective language",
                "Cannot identify a personal deliverable",
                "No objective success measure",
            ],
            [
                "What would not have happened without your contribution?",
                "Who can verify the result?",
                "Which measurable outcome is most directly attributable to your work?",
            ],
        )

    def _archetype(self, competency: str, index: int) -> str:
        value = competency.lower()
        if any(token in value for token in ("power bi", "analytics", "report", "data", "dashboard")):
            return "data"
        if any(token in value for token in ("change", "adoption", "training", "transformation")):
            return "change"
        if any(token in value for token in ("stakeholder", "vendor", "committee", "communication")):
            return "stakeholder"
        if any(token in value for token in ("management", "leadership", "coaching", "team")):
            return "leadership"
        if any(token in value for token in ("risk", "quality", "compliance", "governance")):
            return "risk"
        if any(token in value for token in ("hris", "core hr", "successfactors", "interface", "integration", "testing")):
            return "technical"
        return ("ownership", "risk", "stakeholder")[index % 3]

    def _matching_requirement(self, competency: str, requirements: list[str]) -> str:
        needle = competency.lower()
        for requirement in requirements:
            lower = requirement.lower()
            if needle in lower or lower in needle:
                return requirement
        return ""

    def _matching_evidence(self, competency: str, achievements: list[str]) -> str:
        tokens = {
            token
            for token in competency.lower().replace("/", " ").split()
            if len(token) > 3
        }
        for achievement in achievements:
            lower = achievement.lower()
            if tokens and any(token in lower for token in tokens):
                return achievement
        return achievements[0] if achievements else ""

    def _shorten(self, value: str, limit: int) -> str:
        clean = " ".join(str(value).split())
        return clean if len(clean) <= limit else clean[: limit - 1].rstrip() + "…"
