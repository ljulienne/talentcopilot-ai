from __future__ import annotations

from typing import Any, Dict, Iterable, List

from talentcopilot.calibrated_scoring.models import CalibratedScoreResult


class CalibratedMissionScoringEngine:
    """Job-aware calibration that preserves Mission Fit as the dominant signal."""

    version = "calibrated-mission-scoring-v1.1-universal"

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
        industry = self._number(getattr(comparative, "industry_depth", 0))
        comparative_score = self._number(getattr(comparative, "score", 0))
        family = str(getattr(comparative, "job_family", "general") or "general")

        differentiators = [str(value) for value in differentiators if str(value).strip()]
        validation_points = [str(value) for value in validation_points if str(value).strip()]
        evidence_factor = self._evidence_factor(differentiators, validation_points, breakdown)

        # Preserve the established Sales Manager benchmark while making every
        # other family continuous and Mission-Fit dominant.
        if family == "sales":
            score, cap, limiting = self._legacy_sales_calibration(
                base, breakdown, comparative, evidence_factor
            )
        else:
            score, cap, limiting = self._universal_calibration(
                base, comparative_score, evidence_factor, role, industry,
                comparative, validation_points
            )

        confidence = self._confidence(evidence_factor, validation_points, score, breakdown)
        critical_values = [
            self._number(breakdown.get("industry", industry)),
            self._number(breakdown.get("function", role)),
            self._number(breakdown.get("experience", 0)),
            role,
            industry,
        ]
        coverage_factor = round(sum(critical_values) / max(1, len(critical_values)), 2)

        return CalibratedScoreResult(
            score=round(score, 2),
            confidence=confidence,
            band=self._band(score),
            raw_mission_fit=round(base, 2),
            comparative_scope=round(comparative_score, 2),
            coverage_factor=coverage_factor,
            evidence_factor=evidence_factor,
            critical_cap=cap,
            limiting_factors=limiting + validation_points[:4],
            strengths=differentiators[:4],
        )

    def _universal_calibration(
        self,
        base: float,
        comparative_score: float,
        evidence_factor: float,
        role: float,
        industry: float,
        comparative: Any,
        validation_points: List[str],
    ):
        # Continuous formula: primary evidence 78%, bounded scope 14%,
        # evidence completeness 8%. No discrete bands.
        target = base * 0.78 + comparative_score * 0.14 + evidence_factor * 0.08
        cap = 96.0
        limiting = []

        if role < 25:
            cap = min(cap, 22.0)
            limiting.append("Target function or seniority is not evidenced")
        elif role < 50:
            cap = min(cap, 55.0)
            limiting.append("Role scope is adjacent or below target")

        if industry < 25:
            cap = min(cap, 25.0)
            limiting.append("Target job-family experience is not evidenced")
        elif industry < 60:
            cap = min(cap, 68.0)
            limiting.append("Domain experience is transferable rather than direct")

        if getattr(comparative, "geography_required", False) and getattr(comparative, "geographic_scope", 0) < 55:
            cap = min(cap, 72.0)
            limiting.append("Required geographic scope is not evidenced")
        if getattr(comparative, "leadership_required", False) and getattr(comparative, "leadership_scope", 0) < 55:
            cap = min(cap, 72.0)
            limiting.append("Required leadership scope is not evidenced")
        if getattr(comparative, "commercial_required", False) and getattr(comparative, "commercial_scope", 0) < 55:
            cap = min(cap, 72.0)
            limiting.append("Required commercial ownership is not evidenced")

        if base < 35:
            cap = min(cap, 35.0)

        return max(0.0, min(cap, target)), cap, limiting

    def _legacy_sales_calibration(self, base, breakdown, comparative, evidence_factor):
        role = self._number(getattr(comparative, "role_level", 0))
        geography = self._number(getattr(comparative, "geographic_scope", 0))
        leadership = self._number(getattr(comparative, "leadership_scope", 0))
        commercial = self._number(getattr(comparative, "commercial_scope", 0))
        industry = self._number(getattr(comparative, "industry_depth", 0))
        comparative_score = self._number(getattr(comparative, "score", 0))
        critical_values = [
            self._number(breakdown.get("industry", industry)),
            self._number(breakdown.get("function", role)),
            self._number(breakdown.get("experience", 0)),
            role, industry,
        ]
        coverage = sum(critical_values) / max(1, len(critical_values))
        cap, limiting = self._sales_cap(base, role, industry, geography, leadership, commercial)

        if base < 20 or (role <= 20 and industry <= 20):
            target = 4.0 + 0.04 * base
        elif role >= 98 and comparative_score >= 88 and industry >= 90:
            target = 91.0 + 0.025 * coverage + 0.015 * evidence_factor
        elif role >= 90 and comparative_score >= 82 and industry >= 85:
            target = 76.0 + 0.035 * coverage + 0.020 * evidence_factor
        elif role >= 70 and industry >= 80:
            target = 56.0 + 0.050 * coverage + 0.025 * evidence_factor
        elif role >= 40 and (industry >= 45 or geography >= 75):
            target = 25.0 + 0.060 * coverage + 0.030 * evidence_factor
        else:
            target = 10.0 + 0.10 * coverage + 0.03 * evidence_factor
        target += (base - 70.0) * 0.04
        return max(0.0, min(cap, target)), cap, limiting

    def _sales_cap(self, base, role, industry, geography, leadership, commercial):
        cap = 96.0
        factors = []
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
            factors.append("Director-level scope is partially evidenced")
        if industry < 25:
            cap = min(cap, 12.0)
            factors.append("Target industry experience is not evidenced")
        elif industry < 65:
            cap = min(cap, 42.0)
            factors.append("Industry experience is transferable but not direct")
        if geography < 60:
            cap = min(cap, 70.0)
        if leadership < 60:
            cap = min(cap, 70.0)
        if commercial < 55:
            cap = min(cap, 70.0)
        if base < 40:
            cap = min(cap, 20.0)
        return cap, factors

    def _evidence_factor(self, differentiators, validation_points, breakdown):
        values = [self._number(v) for v in breakdown.values() if isinstance(v, (int, float))]
        completeness = sum(1 for value in values if value > 0) / max(1, len(values))
        value = 45 + len(differentiators) * 9 + completeness * 20 - len(validation_points) * 4
        return round(max(20.0, min(100.0, value)), 2)

    def _confidence(self, evidence_factor, validation_points, score, breakdown):
        populated = sum(1 for value in breakdown.values() if self._number(value) > 0)
        total = max(1, len(breakdown))
        completeness = populated / total
        confidence = 55 + evidence_factor * 0.25 + completeness * 18 - len(validation_points) * 2
        if score <= 12:
            confidence += 5
        return int(round(max(50, min(97, confidence))))

    def _band(self, score):
        if score >= 90: return "Excellent Fit"
        if score >= 75: return "Strong Fit"
        if score >= 58: return "Good Fit"
        if score >= 40: return "Potential Fit"
        if score >= 20: return "Limited Fit"
        return "Poor Fit"

    def _number(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _clamp(self, value: Any) -> float:
        return max(0.0, min(100.0, self._number(value)))
