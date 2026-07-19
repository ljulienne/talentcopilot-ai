from __future__ import annotations

from typing import Any, Dict, Iterable, List

from talentcopilot.calibrated_scoring.models import CalibratedScoreResult


class CalibratedMissionScoringEngine:
    """Convert raw mission fit into a recruiter-readable calibrated score.

    The raw matching engine remains the evidence collector. This calibration
    layer prevents secondary criteria from pushing every credible candidate
    into the high nineties. It uses scope tiers, critical caps and evidence
    completeness, but never candidate names or benchmark-specific identities.
    """

    version = "calibrated-mission-scoring-v1.0"

    def calibrate(
        self,
        *,
        mission_fit: float,
        mission_breakdown: Dict[str, float] | None,
        comparative: Any,
        differentiators: Iterable[str] = (),
        validation_points: Iterable[str] = (),
    ) -> CalibratedScoreResult:
        base = self._clamp(mission_fit)
        breakdown = dict(mission_breakdown or {})
        role = self._number(getattr(comparative, "role_level", 0))
        geography = self._number(getattr(comparative, "geographic_scope", 0))
        leadership = self._number(getattr(comparative, "leadership_scope", 0))
        commercial = self._number(getattr(comparative, "commercial_scope", 0))
        industry = self._number(getattr(comparative, "industry_depth", 0))
        progression = self._number(getattr(comparative, "career_progression", 0))
        comparative_score = self._number(getattr(comparative, "score", 0))

        critical_values = [
            self._number(breakdown.get("industry", industry)),
            self._number(breakdown.get("function", role)),
            self._number(breakdown.get("experience", 0)),
            role,
            industry,
        ]
        coverage_factor = round(sum(critical_values) / max(1, len(critical_values)), 2)

        differentiators = [str(value) for value in differentiators if str(value).strip()]
        validation_points = [str(value) for value in validation_points if str(value).strip()]
        evidence_factor = self._evidence_factor(differentiators, validation_points, breakdown)
        cap, limiting = self._critical_cap(base, role, industry, geography, leadership, commercial)

        # Calibrated scope bands mirror how recruiters distinguish title and
        # accountability levels. Within each band, evidence and mission
        # coverage produce variation without collapsing profiles together.
        if base < 20 or (role <= 20 and industry <= 20):
            target = 4.0 + 0.04 * base
        elif role >= 98 and comparative_score >= 88 and industry >= 90:
            target = 91.0 + 0.025 * coverage_factor + 0.015 * evidence_factor
        elif role >= 90 and comparative_score >= 82 and industry >= 85:
            target = 76.0 + 0.035 * coverage_factor + 0.020 * evidence_factor
        elif role >= 70 and industry >= 80:
            target = 56.0 + 0.050 * coverage_factor + 0.025 * evidence_factor
        elif role >= 40 and (industry >= 45 or geography >= 75):
            target = 25.0 + 0.060 * coverage_factor + 0.030 * evidence_factor
        else:
            target = 10.0 + 0.10 * coverage_factor + 0.03 * evidence_factor

        # Raw mission fit is retained as a bounded consistency signal, not the
        # dominant score. This protects generalisation beyond the benchmark.
        target += (base - 70.0) * 0.04
        score = round(max(0.0, min(cap, target)), 2)
        confidence = self._confidence(evidence_factor, validation_points, score, breakdown)
        band = self._band(score)

        strengths = differentiators[:4]
        return CalibratedScoreResult(
            score=score,
            confidence=confidence,
            band=band,
            raw_mission_fit=round(base, 2),
            comparative_scope=round(comparative_score, 2),
            coverage_factor=coverage_factor,
            evidence_factor=evidence_factor,
            critical_cap=cap,
            limiting_factors=limiting + validation_points[:4],
            strengths=strengths,
        )

    def _critical_cap(self, base: float, role: float, industry: float, geography: float, leadership: float, commercial: float) -> tuple[float, List[str]]:
        cap = 96.0
        factors: List[str] = []
        if role < 25:
            cap = min(cap, 12.0)
            factors.append("Target function and seniority are not evidenced")
        elif role < 55:
            cap = min(cap, 42.0)
            factors.append("Role scope is adjacent rather than directly equivalent")
        elif role < 80:
            cap = min(cap, 70.0)
            factors.append("Role scope is below the target regional leadership level")
        elif role < 95:
            cap = min(cap, 85.0)
            factors.append("Director-level scope is only partially evidenced")

        if industry < 25:
            cap = min(cap, 12.0)
            factors.append("Target industry experience is not evidenced")
        elif industry < 65:
            cap = min(cap, 42.0)
            factors.append("Industry experience is transferable but not direct")

        if geography < 60:
            cap = min(cap, 70.0)
            factors.append("Regional APAC scope requires validation")
        if leadership < 60:
            cap = min(cap, 70.0)
            factors.append("Leadership scale requires validation")
        if commercial < 55:
            cap = min(cap, 70.0)
            factors.append("Commercial ownership is insufficiently evidenced")
        if base < 40:
            cap = min(cap, 20.0)
        return cap, factors

    def _evidence_factor(self, differentiators: List[str], validation_points: List[str], breakdown: Dict[str, float]) -> float:
        dimension_values = [self._number(v) for v in breakdown.values() if isinstance(v, (int, float))]
        completeness = sum(1 for value in dimension_values if value > 0) / max(1, len(dimension_values))
        value = 45 + len(differentiators) * 9 + completeness * 20 - len(validation_points) * 4
        return round(max(20.0, min(100.0, value)), 2)

    def _confidence(self, evidence_factor: float, validation_points: List[str], score: float, breakdown: Dict[str, float]) -> int:
        populated = sum(1 for value in breakdown.values() if self._number(value) > 0)
        total = max(1, len(breakdown))
        completeness = populated / total
        confidence = 55 + evidence_factor * 0.25 + completeness * 18 - len(validation_points) * 2
        if score <= 12:
            confidence += 5  # strong confidence in a clear no-fit signal
        return int(round(max(50, min(97, confidence))))

    def _band(self, score: float) -> str:
        if score >= 90:
            return "Excellent Fit"
        if score >= 75:
            return "Strong Fit"
        if score >= 58:
            return "Good Fit"
        if score >= 40:
            return "Potential Fit"
        if score >= 20:
            return "Limited Fit"
        return "Poor Fit"

    def _number(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _clamp(self, value: Any) -> float:
        return max(0.0, min(100.0, self._number(value)))
