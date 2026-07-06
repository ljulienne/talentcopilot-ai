from dataclasses import dataclass, field
from typing import List

from talentcopilot.ai.reasoning_engine import CandidateReasoningReport


@dataclass
class CandidateDecisionSummary:
    candidate_name: str
    role_title: str
    recommendation: str
    decision_score: float
    demonstrated_skills: int
    missing_skills: int
    risk_count: int
    uncertainty_count: int
    evidence_items: int


@dataclass
class TradeOff:
    title: str
    explanation: str
    candidates_involved: List[str] = field(default_factory=list)


@dataclass
class AlternativeScenario:
    scenario: str
    preferred_candidate: str
    rationale: str


@dataclass
class DecisionRisk:
    title: str
    explanation: str
    candidate_name: str


@dataclass
class RecommendationReport:
    role_title: str
    recommended_candidate: str
    executive_summary: str
    ranking: List[CandidateDecisionSummary]
    trade_offs: List[TradeOff]
    decision_risks: List[DecisionRisk]
    alternative_scenarios: List[AlternativeScenario]
    challenge: str
    interview_priorities: List[str]
    evidence_trace: List[str]


class RecommendationEngine:
    """
    Multi-candidate recommendation engine.

    This engine does not read CVs directly.
    It only consumes CandidateReasoningReport objects.
    """

    def build_recommendation(
        self,
        reports: List[CandidateReasoningReport],
    ) -> RecommendationReport:
        if not reports:
            raise ValueError("At least one CandidateReasoningReport is required.")

        role_title = reports[0].role_title

        summaries = [self._summarize_candidate(report) for report in reports]
        ranking = sorted(summaries, key=lambda item: item.decision_score, reverse=True)

        recommended = ranking[0]

        trade_offs = self._build_trade_offs(ranking)
        decision_risks = self._build_decision_risks(reports)
        alternative_scenarios = self._build_alternative_scenarios(ranking)
        interview_priorities = self._build_interview_priorities(reports)
        evidence_trace = self._build_evidence_trace(reports)

        executive_summary = self._build_executive_summary(ranking)
        challenge = self._build_challenge(ranking, decision_risks)

        return RecommendationReport(
            role_title=role_title,
            recommended_candidate=recommended.candidate_name,
            executive_summary=executive_summary,
            ranking=ranking,
            trade_offs=trade_offs,
            decision_risks=decision_risks,
            alternative_scenarios=alternative_scenarios,
            challenge=challenge,
            interview_priorities=interview_priorities,
            evidence_trace=evidence_trace,
        )

    def _summarize_candidate(
        self,
        report: CandidateReasoningReport,
    ) -> CandidateDecisionSummary:
        demonstrated_skills = len([
            skill for skill in report.skill_assessment
            if skill.status == "demonstrated"
        ])

        mentioned_skills = len([
            skill for skill in report.skill_assessment
            if skill.status == "mentioned"
        ])

        missing_skills = len([
            skill for skill in report.skill_assessment
            if skill.status == "missing"
        ])

        evidence_items = len(report.evidence_assessment)
        risk_count = len(report.risks)
        uncertainty_count = len(report.uncertainties)

        decision_score = (
            demonstrated_skills * 25
            + mentioned_skills * 10
            + evidence_items * 8
            - missing_skills * 15
            - risk_count * 5
            - uncertainty_count * 4
        )

        if "Strong candidate" in report.recommendation:
            decision_score += 15
        elif "targeted validation" in report.recommendation:
            decision_score += 8

        return CandidateDecisionSummary(
            candidate_name=report.candidate_name,
            role_title=report.role_title,
            recommendation=report.recommendation,
            decision_score=round(decision_score, 2),
            demonstrated_skills=demonstrated_skills,
            missing_skills=missing_skills,
            risk_count=risk_count,
            uncertainty_count=uncertainty_count,
            evidence_items=evidence_items,
        )

    def _build_executive_summary(
        self,
        ranking: List[CandidateDecisionSummary],
    ) -> str:
        top = ranking[0]

        if len(ranking) == 1:
            return (
                f"{top.candidate_name} is the candidate to prioritize for this role based on "
                f"the current reasoning report. This recommendation remains human-led and "
                f"should be validated through interview evidence."
            )

        second = ranking[1]

        return (
            f"{top.candidate_name} is recommended ahead of {second.candidate_name} because "
            f"the current decision profile shows a stronger balance of demonstrated skills, "
            f"evidence quality, and manageable risk. The difference should still be validated "
            f"through targeted interviews, especially if the organization values long-term "
            f"potential differently from immediate readiness."
        )

    def _build_trade_offs(
        self,
        ranking: List[CandidateDecisionSummary],
    ) -> List[TradeOff]:
        if len(ranking) < 2:
            return [
                TradeOff(
                    title="Single-candidate decision",
                    explanation=(
                        "No candidate-to-candidate trade-off is available. The recruiter should "
                        "validate whether this candidate meets the role requirements."
                    ),
                    candidates_involved=[ranking[0].candidate_name],
                )
            ]

        top = ranking[0]
        second = ranking[1]

        return [
            TradeOff(
                title="Immediate readiness vs alternative potential",
                explanation=(
                    f"{top.candidate_name} appears stronger for immediate prioritization, while "
                    f"{second.candidate_name} may still be relevant if the organization values "
                    f"potential, adaptability, or different strengths not fully captured in the "
                    f"current evidence."
                ),
                candidates_involved=[top.candidate_name, second.candidate_name],
            ),
            TradeOff(
                title="Evidence quality vs uncertainty",
                explanation=(
                    "The recruiter should compare not only skills, but also the quality of the "
                    "evidence supporting those skills. A candidate with fewer but stronger proofs "
                    "may be less risky than a candidate with many unsupported claims."
                ),
                candidates_involved=[item.candidate_name for item in ranking[:2]],
            ),
        ]

    def _build_decision_risks(
        self,
        reports: List[CandidateReasoningReport],
    ) -> List[DecisionRisk]:
        risks = []

        for report in reports:
            for risk in report.risks[:2]:
                risks.append(
                    DecisionRisk(
                        title=risk.title,
                        explanation=risk.explanation,
                        candidate_name=report.candidate_name,
                    )
                )

        return risks

    def _build_alternative_scenarios(
        self,
        ranking: List[CandidateDecisionSummary],
    ) -> List[AlternativeScenario]:
        top = ranking[0]

        scenarios = [
            AlternativeScenario(
                scenario="If the priority is immediate readiness",
                preferred_candidate=top.candidate_name,
                rationale=(
                    "The top-ranked candidate should be prioritized when the role requires fast "
                    "autonomy, lower onboarding risk, and stronger demonstrated alignment."
                ),
            )
        ]

        if len(ranking) >= 2:
            second = ranking[1]
            scenarios.append(
                AlternativeScenario(
                    scenario="If the priority is development potential",
                    preferred_candidate=second.candidate_name,
                    rationale=(
                        "The second-ranked candidate may become a credible alternative if the "
                        "organization is willing to invest in onboarding, coaching, or capability "
                        "development."
                    ),
                )
            )

        return scenarios

    def _build_challenge(
        self,
        ranking: List[CandidateDecisionSummary],
        decision_risks: List[DecisionRisk],
    ) -> str:
        top = ranking[0]

        risk_text = ""
        if decision_risks:
            risk_text = f" The main risk to validate is: {decision_risks[0].title.lower()}."

        return (
            f"The recommendation of {top.candidate_name} should be challenged rather than accepted "
            f"automatically. It assumes that the current evidence accurately reflects real ownership, "
            f"impact, and role readiness.{risk_text} Recruiters should test this assumption through "
            f"structured interviews before making a final decision."
        )

    def _build_interview_priorities(
        self,
        reports: List[CandidateReasoningReport],
    ) -> List[str]:
        priorities = []

        for report in reports:
            if report.missing_information:
                priorities.append(
                    f"{report.candidate_name}: validate {report.missing_information[0]}"
                )
            elif report.risks:
                priorities.append(
                    f"{report.candidate_name}: test {report.risks[0].title.lower()}"
                )

        return priorities

    def _build_evidence_trace(
        self,
        reports: List[CandidateReasoningReport],
    ) -> List[str]:
        trace = []

        for report in reports:
            for evidence in report.evidence_assessment[:3]:
                trace.append(
                    f"{report.candidate_name}: {evidence.text} "
                    f"→ {evidence.interpretation}"
                )

        return trace
