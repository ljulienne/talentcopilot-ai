from __future__ import annotations

from typing import Any, List

from .models import DecisionRankingAssessment


class DecisionRankingPolicy:
    """Convert objective and career evidence into interview priority.

    Mission Fit remains the official objective score. This policy only produces
    the separate decision score used to order interviews. It deliberately gives
    meaningful weight to recent role continuity and career drift so a small raw
    Mission Fit advantage cannot silently outweigh a material career mismatch.
    """

    version = "decision-ranking-policy-v1.2"

    def evaluate(
        self,
        *,
        mission_fit: float,
        career: Any,
        recruiter_fit: float,
        confidence: float,
    ) -> DecisionRankingAssessment:
        mission = self._clamp(mission_fit)
        career_fit = self._clamp(getattr(career, "score", 0))
        recruiter = self._clamp(recruiter_fit)
        evidence_confidence = self._clamp(confidence)

        recent = self._clamp(getattr(career, "recent_role_alignment", career_fit))
        persistence = self._clamp(getattr(career, "domain_persistence", career_fit))
        drift = self._clamp(getattr(career, "career_drift", 100 - career_fit))
        seniority = self._clamp(getattr(career, "seniority_alignment", career_fit))
        functional = self._clamp(getattr(career, "functional_alignment", career_fit))
        transferability = self._clamp(getattr(career, "transferability", career_fit))

        # Balanced decision score: objective fit is still the largest component,
        # but career continuity has enough influence to change interview order.
        base = (
            mission * 0.58
            + career_fit * 0.16
            + recent * 0.07
            + persistence * 0.04
            + functional * 0.03
            + recruiter * 0.07
            + evidence_confidence * 0.05
        )

        blockers: List[str] = []
        adjustment = 0.0

        if recent < 45:
            adjustment -= 8.0
            blockers.append("limited recent-role alignment")
        elif recent < 58:
            adjustment -= 2.0

        if drift > 65:
            adjustment -= 8.0
            blockers.append("material career drift from the target domain")
        elif drift > 52:
            adjustment -= 2.0

        if persistence < 45:
            adjustment -= 3.0
            blockers.append("limited target-domain persistence")

        if seniority < 45:
            adjustment -= 5.0
            blockers.append("material seniority mismatch")

        # Reward clear, recent operational continuity without creating a second
        # opaque score. These signals are already present in Career Intelligence.
        if recent >= 75 and drift <= 30:
            adjustment += 2.0
        if persistence >= 75 and functional >= 75:
            adjustment += 1.0
        if transferability < 45:
            adjustment -= 2.0
            blockers.append("limited evidence of transferability")

        # A material combination of recent-role mismatch and career drift is
        # more decision-relevant than either signal in isolation. This is a
        # generic trajectory rule and never depends on candidate names/titles.
        if recent < 50 and drift > 60:
            adjustment -= 5.0
            blockers.append("combined recent-role mismatch and domain drift")

        final = round(self._clamp(base + adjustment), 2)
        rationale = self._rationale(final, recent, persistence, drift, seniority, blockers)
        return DecisionRankingAssessment(
            score=final,
            base_score=round(base, 2),
            alignment_adjustment=round(adjustment, 2),
            components={
                "mission_fit": mission,
                "career_fit": career_fit,
                "recent_role_alignment": recent,
                "domain_persistence": persistence,
                "functional_alignment": functional,
                "career_drift": drift,
                "seniority_alignment": seniority,
                "transferability": transferability,
                "recruiter_fit": recruiter,
                "confidence": evidence_confidence,
            },
            blockers=blockers,
            rationale=rationale,
            version=self.version,
        )

    def _rationale(
        self,
        score: float,
        recent: float,
        persistence: float,
        drift: float,
        seniority: float,
        blockers: List[str],
    ) -> str:
        band = "high" if score >= 75 else "credible" if score >= 60 else "conditional"
        text = (
            f"{band.capitalize()} interview priority based on objective Mission Fit and "
            f"career continuity (recent role {recent:.0f}, persistence {persistence:.0f}, "
            f"career drift {drift:.0f}, seniority alignment {seniority:.0f})."
        )
        if blockers:
            text += " Priority validation: " + ", ".join(blockers[:3]) + "."
        return text

    @staticmethod
    def _clamp(value: float) -> float:
        try:
            number = float(value or 0)
        except (TypeError, ValueError):
            number = 0.0
        return max(0.0, min(100.0, number))
