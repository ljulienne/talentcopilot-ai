from typing import List

from talentcopilot.models.governance import EvidenceQualitySummary
from talentcopilot.models.uncertainty import CandidateUncertaintySummary, UncertaintyItem


class UncertaintyEngine:
    """
    Detects weak, missing or ambiguous evidence.
    """

    def assess(self, evidence_quality: EvidenceQualitySummary) -> CandidateUncertaintySummary:
        items: List[UncertaintyItem] = []

        for eq in evidence_quality.assessments:
            missing = []
            reasons = []

            if eq.evidence_count == 0:
                missing.append(f"Evidence for {eq.competency}")
                reasons.append("No evidence found")
            elif eq.evidence_count == 1:
                missing.append(f"Additional evidence for {eq.competency}")
                reasons.append("Only one evidence point found")

            if eq.quality_score < 50:
                reasons.append("Evidence quality is weak")
                missing.append("More specific or measurable achievements")

            uncertainty = self._score_uncertainty(eq.evidence_count, eq.quality_score)

            if uncertainty >= 30:
                items.append(
                    UncertaintyItem(
                        competency=eq.competency,
                        uncertainty_score=uncertainty,
                        reason="; ".join(reasons) if reasons else "Moderate uncertainty detected",
                        missing_information=missing,
                        recommendation=f"Validate {eq.competency} during interview.",
                    )
                )

        overall = round(
            sum(i.uncertainty_score for i in items) / len(items),
            2,
        ) if items else 0.0

        explanation = (
            f"Overall uncertainty is {overall}/100."
            if items
            else "No major uncertainty detected."
        )

        return CandidateUncertaintySummary(
            overall_uncertainty=overall,
            uncertainties=items,
            explanation=explanation,
        )

    def _score_uncertainty(self, evidence_count: int, quality_score: float) -> float:
        if evidence_count == 0:
            return 95.0
        if evidence_count == 1 and quality_score < 50:
            return 75.0
        if evidence_count == 1:
            return 55.0
        if quality_score < 50:
            return 50.0
        if quality_score < 70:
            return 35.0
        return 15.0
