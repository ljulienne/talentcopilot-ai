from typing import Any, List

from talentcopilot.models.confidence import (
    CandidateConfidenceSummary,
    ConfidenceAssessment,
    ConfidenceFactor,
)
from talentcopilot.models.governance import EvidenceQualitySummary


class ConfidenceEngine:
    """
    Computes confidence from evidence quality, evidence volume and match signal.
    """

    def assess(self, candidate: Any, job: Any, evidence_quality: EvidenceQualitySummary, match_score: float = 0.0) -> CandidateConfidenceSummary:
        assessments: List[ConfidenceAssessment] = []

        for eq in evidence_quality.assessments:
            evidence_volume_score = min(100.0, eq.evidence_count * 25.0)
            quality_score = eq.quality_score
            match_component = max(0.0, min(100.0, match_score))

            confidence = round(
                (quality_score * 0.50) +
                (evidence_volume_score * 0.30) +
                (match_component * 0.20),
                2,
            )

            factors = [
                ConfidenceFactor(
                    name="Evidence quality",
                    score=quality_score,
                    explanation=f"Evidence quality for {eq.competency} is {quality_score}/100.",
                ),
                ConfidenceFactor(
                    name="Evidence volume",
                    score=evidence_volume_score,
                    explanation=f"{eq.evidence_count} evidence point(s) detected.",
                ),
                ConfidenceFactor(
                    name="Match signal",
                    score=match_component,
                    explanation=f"Candidate match signal is {match_component}/100.",
                ),
            ]

            assessments.append(
                ConfidenceAssessment(
                    competency=eq.competency,
                    confidence_score=confidence,
                    evidence_count=eq.evidence_count,
                    evidence_quality_score=quality_score,
                    factors=factors,
                    explanation=f"Confidence for {eq.competency} is {confidence}/100.",
                )
            )

        overall = round(
            sum(a.confidence_score for a in assessments) / len(assessments),
            2,
        ) if assessments else 0.0

        return CandidateConfidenceSummary(
            overall_confidence=overall,
            assessments=assessments,
            explanation=f"Overall confidence is {overall}/100.",
        )
