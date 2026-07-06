from dataclasses import dataclass, field
from typing import List

from talentcopilot.ai.reasoning_engine import CandidateReasoningReport
from talentcopilot.ai.interview_intelligence import InterviewGuide
from talentcopilot.ai.recommendation_engine import RecommendationReport


@dataclass
class DecisionTimelineStep:
    name: str
    status: str
    description: str


@dataclass
class DecisionMetric:
    label: str
    value: str
    explanation: str


@dataclass
class DecisionWorkspaceViewModel:
    candidate_name: str
    role_title: str
    recommendation: str
    executive_summary: str
    decision_confidence: int
    decision_readiness: int
    timeline: List[DecisionTimelineStep] = field(default_factory=list)
    metrics: List[DecisionMetric] = field(default_factory=list)
    reasoning_report: CandidateReasoningReport | None = None
    interview_guide: InterviewGuide | None = None
    recommendation_report: RecommendationReport | None = None


class DecisionWorkspaceBuilder:
    def build(
        self,
        reasoning_report: CandidateReasoningReport,
        interview_guide: InterviewGuide,
        recommendation_report: RecommendationReport,
    ) -> DecisionWorkspaceViewModel:
        confidence = self._calculate_decision_confidence(reasoning_report)
        readiness = self._calculate_decision_readiness(reasoning_report, interview_guide)

        return DecisionWorkspaceViewModel(
            candidate_name=reasoning_report.candidate_name,
            role_title=reasoning_report.role_title,
            recommendation=reasoning_report.recommendation,
            executive_summary=reasoning_report.executive_summary,
            decision_confidence=confidence,
            decision_readiness=readiness,
            timeline=self._build_timeline(reasoning_report, interview_guide, recommendation_report),
            metrics=self._build_metrics(reasoning_report, confidence, readiness),
            reasoning_report=reasoning_report,
            interview_guide=interview_guide,
            recommendation_report=recommendation_report,
        )

    def _calculate_decision_confidence(self, report: CandidateReasoningReport) -> int:
        demonstrated = len([s for s in report.skill_assessment if s.status == "demonstrated"])
        mentioned = len([s for s in report.skill_assessment if s.status == "mentioned"])
        missing = len([s for s in report.skill_assessment if s.status == "missing"])
        evidence = len(report.evidence_assessment)
        uncertainty = len(report.uncertainties)

        raw = 50 + demonstrated * 12 + mentioned * 5 + evidence * 4 - missing * 10 - uncertainty * 5
        return max(0, min(100, int(raw)))

    def _calculate_decision_readiness(
        self,
        report: CandidateReasoningReport,
        guide: InterviewGuide,
    ) -> int:
        has_summary = bool(report.executive_summary)
        has_risks = bool(report.risks)
        has_questions = bool(guide.questions)
        has_missing_info = bool(report.missing_information)

        raw = 40
        raw += 15 if has_summary else 0
        raw += 15 if has_risks else 0
        raw += 20 if has_questions else 0
        raw += 10 if has_missing_info else 0

        return max(0, min(100, int(raw)))

    def _build_timeline(
        self,
        report: CandidateReasoningReport,
        guide: InterviewGuide,
        recommendation_report: RecommendationReport,
    ) -> List[DecisionTimelineStep]:
        return [
            DecisionTimelineStep("Evidence", "completed", "Candidate evidence has been collected."),
            DecisionTimelineStep("Evidence Quality", "completed", "Evidence strength has been assessed."),
            DecisionTimelineStep("Competencies", "completed", "Target skills have been evaluated."),
            DecisionTimelineStep("Risks", "completed", "Decision risks have been identified."),
            DecisionTimelineStep("Uncertainty", "completed", "Missing information has been detected."),
            DecisionTimelineStep("Interview", "completed" if guide.questions else "attention", "Interview strategy is available."),
            DecisionTimelineStep("Recommendation", "completed", "AI recommendation has been generated."),
            DecisionTimelineStep("Challenge", "completed" if recommendation_report.challenge else "attention", "Recommendation has been challenged."),
        ]

    def _build_metrics(
        self,
        report: CandidateReasoningReport,
        confidence: int,
        readiness: int,
    ) -> List[DecisionMetric]:
        demonstrated = len([s for s in report.skill_assessment if s.status == "demonstrated"])
        missing = len([s for s in report.skill_assessment if s.status == "missing"])

        return [
            DecisionMetric(
                label="Decision Confidence",
                value=f"{confidence}%",
                explanation="Confidence in the current recommendation based on evidence, skills, risks and uncertainty.",
            ),
            DecisionMetric(
                label="Decision Readiness",
                value=f"{readiness}%",
                explanation="Readiness to move to the next recruiting step with a structured decision process.",
            ),
            DecisionMetric(
                label="Demonstrated Skills",
                value=str(demonstrated),
                explanation="Target skills supported by evidence.",
            ),
            DecisionMetric(
                label="Missing Skills",
                value=str(missing),
                explanation="Target skills not clearly visible in the available candidate information.",
            ),
        ]
