from dataclasses import dataclass, field
from typing import List

from talentcopilot.ai.evidence_intelligence import EvidenceIntelligenceEngine


@dataclass
class CompetencyArgument:
    competency: str
    conclusion: str
    confidence_score: int
    evidence: List[str] = field(default_factory=list)
    rationale: str = ""
    limitations: List[str] = field(default_factory=list)
    interview_validation: List[str] = field(default_factory=list)


@dataclass
class CompetencyReasoningReport:
    arguments: List[CompetencyArgument]
    summary: str


class CompetencyReasoningEngine:
    """
    Builds competency-level reasoning from evidence.

    It does not infer competencies from keywords alone.
    It links each competency to evidence quality, limitations, and validation needs.
    """

    def analyze(self, evidence_texts: List[str], target_competencies: List[str]) -> CompetencyReasoningReport:
        evidence_report = EvidenceIntelligenceEngine().analyze(evidence_texts)

        arguments = []

        for competency in target_competencies:
            related_items = [
                item for item in evidence_report.evidence_items
                if competency.lower() in [c.lower() for c in item.inferred_competencies]
                or competency.lower() in item.text.lower()
            ]

            if related_items:
                avg_quality = round(sum(item.quality.score for item in related_items if item.quality) / len(related_items))
                limitations = []
                for item in related_items:
                    limitations.extend(item.limitations)

                limitations = list(dict.fromkeys(limitations))

                conclusion = self._conclusion_from_score(avg_quality)
                rationale = (
                    f"{competency} is supported by {len(related_items)} evidence item(s). "
                    f"The average evidence quality is {avg_quality}/100. "
                    "This conclusion is based on observed responsibilities, context, impact, and measurable details."
                )

                arguments.append(
                    CompetencyArgument(
                        competency=competency,
                        conclusion=conclusion,
                        confidence_score=avg_quality,
                        evidence=[item.text for item in related_items],
                        rationale=rationale,
                        limitations=limitations,
                        interview_validation=self._validation_questions(competency, limitations),
                    )
                )
            else:
                arguments.append(
                    CompetencyArgument(
                        competency=competency,
                        conclusion="not demonstrated",
                        confidence_score=20,
                        evidence=[],
                        rationale=(
                            f"{competency} is not clearly demonstrated by the available evidence. "
                            "This should not be treated as a rejection criterion, but as a validation point."
                        ),
                        limitations=["No direct evidence found for this competency."],
                        interview_validation=[
                            f"Can you describe a concrete example where you demonstrated {competency}?",
                            f"What was your exact role and measurable impact related to {competency}?",
                        ],
                    )
                )

        return CompetencyReasoningReport(
            arguments=arguments,
            summary=self._build_summary(arguments),
        )

    def _conclusion_from_score(self, score: int) -> str:
        if score >= 85:
            return "strongly demonstrated"
        if score >= 70:
            return "demonstrated"
        if score >= 50:
            return "partially demonstrated"
        return "weakly demonstrated"

    def _validation_questions(self, competency: str, limitations: List[str]) -> List[str]:
        questions = []

        if any("measurable" in limitation.lower() for limitation in limitations):
            questions.append(
                f"Can you quantify the impact of your work related to {competency}?"
            )

        if any("ownership" in limitation.lower() for limitation in limitations):
            questions.append(
                f"What decisions were directly under your responsibility when demonstrating {competency}?"
            )

        if any("scale" in limitation.lower() or "scope" in limitation.lower() for limitation in limitations):
            questions.append(
                f"What was the scale, scope, team size, or stakeholder complexity involved in this {competency} example?"
            )

        if not questions:
            questions.append(
                f"Can you walk through one specific example that best demonstrates {competency}?"
            )

        return questions

    def _build_summary(self, arguments: List[CompetencyArgument]) -> str:
        demonstrated = len([
            arg for arg in arguments
            if arg.conclusion in {"strongly demonstrated", "demonstrated"}
        ])

        not_demonstrated = len([
            arg for arg in arguments
            if arg.conclusion == "not demonstrated"
        ])

        return (
            f"{demonstrated} competency/competencies are demonstrated by evidence. "
            f"{not_demonstrated} competency/competencies are not clearly demonstrated and should be validated. "
            "The analysis prioritizes evidence quality over keyword presence."
        )
