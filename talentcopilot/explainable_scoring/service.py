from __future__ import annotations

from typing import Any, Dict, Iterable, List

from .models import CandidateScoreBreakdown, ScoreDimension, ScoreEvidence


class ExplainableScoringService:
    """Explain the canonical Mission Fit without recalculating or replacing it."""

    LABELS = {
        "industry": "Domain / industry fit",
        "function": "Functional fit",
        "leadership": "Leadership fit",
        "experience": "Experience fit",
        "business_scope": "Mission capabilities",
        "tools": "Tools fit",
        "geography": "Geographic fit",
        "education_languages": "Education and languages",
    }

    WEIGHTS = {
        "industry": 0.12,
        "function": 0.20,
        "leadership": 0.12,
        "experience": 0.14,
        "business_scope": 0.20,
        "tools": 0.08,
        "geography": 0.07,
        "education_languages": 0.07,
    }

    def build(self, report: Any) -> CandidateScoreBreakdown:
        breakdown = dict(getattr(report, "score_breakdown", {}) or {})
        mission_fit = self._number(
            getattr(report, "match_score", breakdown.get("role_fit", 0.0))
        )
        confidence = self._number(breakdown.get("confidence", 0.0))
        dimensions = self._dimensions(breakdown, mission_fit)

        positives: List[ScoreEvidence] = []
        penalties: List[ScoreEvidence] = []
        for dimension in dimensions:
            if dimension.status == "Strong":
                positives.append(ScoreEvidence(
                    label=dimension.label,
                    detail=f"{dimension.score:.0f}% alignment contributes {dimension.contribution:.1f} points.",
                    impact=dimension.contribution,
                    kind="positive",
                ))
            elif dimension.status in {"Limited", "Gap"}:
                shortfall = round(dimension.weight * 100 - dimension.contribution, 2)
                penalties.append(ScoreEvidence(
                    label=dimension.label,
                    detail=f"{dimension.score:.0f}% alignment leaves {shortfall:.1f} weighted points unconfirmed.",
                    impact=-shortfall,
                    kind="penalty",
                ))

        rationale = self._rationale(mission_fit, confidence, dimensions)
        return CandidateScoreBreakdown(
            candidate_id=str(getattr(report, "candidate_id", "")),
            candidate_name=str(getattr(report, "candidate_name", "Candidate")),
            mission_fit=mission_fit,
            confidence=confidence,
            dimensions=dimensions,
            positive_contributions=positives[:4],
            penalties=penalties[:4],
            rationale=rationale,
        )

    def _dimensions(self, breakdown: Dict[str, Any], mission_fit: float) -> List[ScoreDimension]:
        available = {
            key: self._number(breakdown.get(f"mission_fit_{key}"))
            for key in self.WEIGHTS
            if f"mission_fit_{key}" in breakdown
        }
        if not available:
            return [ScoreDimension(
                key="official_mission_fit",
                label="Official Mission Fit",
                score=mission_fit,
                weight=1.0,
                contribution=mission_fit,
                status=self._status(mission_fit),
                evidence=[ScoreEvidence(
                    label="Canonical score",
                    detail="The active RecruitmentSession contains the official score but no dimension-level trace yet.",
                )],
            )]

        raw = []
        for key, score in available.items():
            weight = self.WEIGHTS[key]
            raw.append((key, score, weight, round(score * weight, 2)))

        raw_total = sum(item[3] for item in raw)
        scale = (mission_fit / raw_total) if raw_total > 0 else 0.0
        dimensions = []
        for key, score, weight, contribution in raw:
            canonical_contribution = round(contribution * scale, 2)
            dimensions.append(ScoreDimension(
                key=key,
                label=self.LABELS[key],
                score=score,
                weight=weight,
                contribution=canonical_contribution,
                status=self._status(score),
                evidence=[ScoreEvidence(
                    label="Weighted contribution",
                    detail=f"Dimension score {score:.0f}% × weight {weight:.0%}, reconciled to the immutable official Mission Fit.",
                    impact=canonical_contribution,
                )],
            ))

        difference = round(mission_fit - sum(item.contribution for item in dimensions), 2)
        if dimensions and difference:
            last = dimensions[-1]
            dimensions[-1] = ScoreDimension(
                key=last.key,
                label=last.label,
                score=last.score,
                weight=last.weight,
                contribution=round(last.contribution + difference, 2),
                status=last.status,
                evidence=last.evidence,
            )
        return dimensions

    def _rationale(self, mission_fit: float, confidence: float, dimensions: Iterable[ScoreDimension]) -> str:
        values = list(dimensions)
        strongest = max(values, key=lambda item: item.contribution).label if values else "available evidence"
        weakest = min(values, key=lambda item: item.score).label if values else "unconfirmed evidence"
        confidence_text = f" Confidence is {confidence:.0f}%." if confidence else ""
        return (
            f"The official Mission Fit remains {mission_fit:.0f}% and is not recalculated here. "
            f"The strongest weighted contribution is {strongest}; the main area to validate is {weakest}."
            f"{confidence_text}"
        )

    def _status(self, score: float) -> str:
        if score >= 80:
            return "Strong"
        if score >= 60:
            return "Supported"
        if score >= 35:
            return "Limited"
        return "Gap"

    def _number(self, value: Any) -> float:
        try:
            return round(float(value or 0.0), 2)
        except (TypeError, ValueError):
            return 0.0
