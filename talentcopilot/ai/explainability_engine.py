from typing import List

from talentcopilot.models.governance import AIDecisionCard
from talentcopilot.models.confidence import CandidateConfidenceSummary
from talentcopilot.models.governance import EvidenceQualitySummary
from talentcopilot.models.risk import CandidateRiskSummary
from talentcopilot.models.uncertainty import CandidateUncertaintySummary


class ExplainabilityEngine:
    """
    Produces human-readable explanations for the decision card.
    """

    def build_decision_card(
        self,
        candidate_name: str,
        role_title: str,
        match_score: float,
        confidence: CandidateConfidenceSummary,
        evidence_quality: EvidenceQualitySummary,
        risk: CandidateRiskSummary,
        uncertainty: CandidateUncertaintySummary,
    ) -> AIDecisionCard:
        decision = self._decision(match_score, confidence.overall_confidence, risk.overall_risk_level)
        human_validation = self._human_validation(risk.overall_risk_level, uncertainty.uncertainty_level)
        strengths = self._strengths(confidence, evidence_quality)
        risks = [r.reason for r in risk.risks[:5]]
        missing = []
        interview_focus = []

        for item in uncertainty.uncertainties:
            missing.extend(item.missing_information)
            interview_focus.append(item.recommendation)

        executive_summary = self._summary(decision, match_score, confidence, evidence_quality, risk, uncertainty)

        return AIDecisionCard(
            candidate_name=candidate_name,
            role_title=role_title,
            match_score=round(match_score, 2),
            decision=decision,
            confidence_score=confidence.overall_confidence,
            evidence_quality_score=evidence_quality.overall_quality_score,
            risk_level=risk.overall_risk_level,
            uncertainty_level=uncertainty.uncertainty_level,
            human_validation=human_validation,
            executive_summary=executive_summary,
            strengths=strengths,
            risks=risks,
            missing_information=list(dict.fromkeys(missing)),
            interview_focus=list(dict.fromkeys(interview_focus)),
        )

    def _decision(self, match_score: float, confidence_score: float, risk_level: str) -> str:
        if match_score >= 85 and confidence_score >= 80 and risk_level != "High":
            return "Strong Hire"
        if match_score >= 70 and confidence_score >= 60:
            return "Hire / Continue Process"
        if match_score >= 55:
            return "Review Carefully"
        return "Not Recommended"

    def _human_validation(self, risk_level: str, uncertainty_level: str) -> str:
        if risk_level == "High" or uncertainty_level == "High":
            return "Strongly Recommended"
        if risk_level == "Medium" or uncertainty_level == "Medium":
            return "Recommended"
        return "Standard Review"

    def _strengths(self, confidence: CandidateConfidenceSummary, evidence_quality: EvidenceQualitySummary) -> List[str]:
        strengths = []
        for assessment in confidence.assessments:
            if assessment.confidence_score >= 80:
                strengths.append(f"High confidence on {assessment.competency}")
        for assessment in evidence_quality.assessments:
            if assessment.quality_score >= 80:
                strengths.append(f"Strong evidence quality on {assessment.competency}")
        return strengths[:5]

    def _summary(self, decision, match_score, confidence, evidence_quality, risk, uncertainty) -> str:
        return (
            f"Decision: {decision}. Match score is {round(match_score, 2)}/100, "
            f"confidence is {confidence.overall_confidence}/100, evidence quality is "
            f"{evidence_quality.overall_quality_score}/100, overall risk is {risk.overall_risk_level}, "
            f"and uncertainty level is {uncertainty.uncertainty_level}."
        )
