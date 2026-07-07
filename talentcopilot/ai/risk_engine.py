from typing import List

from talentcopilot.models.governance import EvidenceQualitySummary
from talentcopilot.models.risk import CandidateRiskSummary, RiskItem
from talentcopilot.models.uncertainty import CandidateUncertaintySummary


class RiskEngine:
    """
    Converts evidence weaknesses and uncertainty into recruiter-friendly risks.
    """

    def assess(self, evidence_quality: EvidenceQualitySummary, uncertainty: CandidateUncertaintySummary) -> CandidateRiskSummary:
        risks: List[RiskItem] = []

        for eq in evidence_quality.assessments:
            if eq.evidence_count == 0:
                risks.append(
                    RiskItem(
                        competency=eq.competency,
                        risk_level="High",
                        reason=f"No evidence found for {eq.competency}.",
                        mitigation=f"Ask targeted interview questions about {eq.competency}.",
                    )
                )
            elif eq.evidence_count == 1:
                risks.append(
                    RiskItem(
                        competency=eq.competency,
                        risk_level="Medium",
                        reason=f"Only one evidence point supports {eq.competency}.",
                        mitigation=f"Request concrete examples of {eq.competency}.",
                    )
                )

            if eq.quality_score < 50 and eq.evidence_count > 0:
                risks.append(
                    RiskItem(
                        competency=eq.competency,
                        risk_level="Medium",
                        reason=f"Evidence for {eq.competency} is not specific or measurable enough.",
                        mitigation="Validate with behavioral questions and examples.",
                    )
                )

        for item in uncertainty.uncertainties:
            if item.uncertainty_score >= 70:
                risks.append(
                    RiskItem(
                        competency=item.competency,
                        risk_level="High",
                        reason=item.reason,
                        mitigation=item.recommendation,
                    )
                )

        overall = self._overall_risk(risks)

        return CandidateRiskSummary(
            overall_risk_level=overall,
            risks=risks,
            explanation=f"{len(risks)} risk(s) detected. Overall risk level: {overall}.",
        )

    def _overall_risk(self, risks: List[RiskItem]) -> str:
        if any(r.risk_level == "High" for r in risks):
            return "High"
        if len([r for r in risks if r.risk_level == "Medium"]) >= 2:
            return "Medium"
        if risks:
            return "Low"
        return "Low"
