"""Premium Candidate Intelligence presentation model.

This service organises existing CandidateWorkspaceReport and
CandidateIntelligenceSnapshot outputs. It never recalculates the official score,
official rank, matching, evidence graph, or interview questions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class CandidateDecisionBrief:
    candidate_id: str
    candidate_name: str
    official_match_score: float
    official_rank: int
    recommendation: str
    recommendation_label: str
    confidence_score: int
    confidence_label: str
    evidence_coverage: int
    potential_signal: int
    executive_summary: str
    recommendation_explanation: str
    strengths: tuple[str, ...]
    transferable_evidence: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    hiring_risks: tuple[str, ...]
    interview_priorities: tuple[str, ...]
    evidence_summary: str


class CandidateIntelligenceViewService:
    """Build a decision brief from already-computed candidate outputs."""

    def build(self, report, intelligence) -> CandidateDecisionBrief:
        official_score = float(
            getattr(report, "official_match_score", None)
            or getattr(report, "match_score", 0.0)
            or 0.0
        )
        official_rank = int(
            getattr(report, "official_rank", None)
            or getattr(report, "rank", 0)
            or 0
        )

        score_breakdown = dict(
            getattr(report, "score_breakdown", {}) or {}
        )
        canonical_confidence = score_breakdown.get("confidence")
        if canonical_confidence is None:
            canonical_confidence = getattr(
                intelligence,
                "decision_confidence",
                0,
            )

        try:
            confidence_score = int(
                max(0, min(100, round(float(canonical_confidence))))
            )
        except (TypeError, ValueError):
            confidence_score = 0

        recommendation = self._clean(
            getattr(intelligence, "recommendation", None)
            or getattr(report, "recommendation", None),
            "Human validation required",
        )

        strengths = self._unique(
            getattr(intelligence, "strengths", ())
            or self._skill_names(report, minimum_level=75)
        )[:5]

        transferable = self._transferable_skills(report, strengths)[:4]

        missing = self._unique(
            getattr(intelligence, "missing_evidence", ())
        )[:4]

        risks = self._risk_summaries(
            getattr(intelligence, "risks", ())
        )[:4]

        interview = self._unique(
            getattr(intelligence, "interview_strategy", ())
            or getattr(report, "interview_focus", ())
        )[:5]

        return CandidateDecisionBrief(
            candidate_id=self._clean(
                getattr(report, "candidate_id", ""),
                "",
            ),
            candidate_name=self._clean(
                getattr(report, "candidate_name", ""),
                "Candidate",
            ),
            official_match_score=official_score,
            official_rank=official_rank,
            recommendation=recommendation,
            recommendation_label=self._recommendation_label(
                recommendation,
                official_score,
            ),
            confidence_score=confidence_score,
            confidence_label=self._confidence_label(confidence_score),
            evidence_coverage=int(
                max(
                    0,
                    min(
                        100,
                        int(
                            getattr(
                                intelligence,
                                "evidence_coverage",
                                0,
                            )
                            or 0
                        ),
                    ),
                )
            ),
            potential_signal=int(
                max(
                    0,
                    min(
                        100,
                        int(
                            getattr(
                                intelligence,
                                "potential_signal",
                                0,
                            )
                            or 0
                        ),
                    ),
                )
            ),
            executive_summary=self._clean(
                getattr(report, "executive_summary", ""),
                "No executive summary is available yet.",
            ),
            recommendation_explanation=self._clean(
                getattr(
                    intelligence,
                    "recommendation_explanation",
                    "",
                ),
                "The recommendation requires human validation.",
            ),
            strengths=tuple(strengths),
            transferable_evidence=tuple(transferable),
            missing_evidence=tuple(missing),
            hiring_risks=tuple(risks),
            interview_priorities=tuple(interview),
            evidence_summary=self._clean(
                getattr(intelligence, "evidence_summary", ""),
                "Evidence summary is not available.",
            ),
        )

    def _skill_names(self, report, minimum_level: int) -> list[str]:
        values = []
        for skill in getattr(report, "skills", []) or []:
            level = int(getattr(skill, "level", 0) or 0)
            if level >= minimum_level:
                values.append(
                    self._clean(
                        getattr(skill, "name", ""),
                        "Relevant capability",
                    )
                )
        return self._unique(values)

    def _transferable_skills(
        self,
        report,
        strengths: Iterable[str],
    ) -> list[str]:
        strength_keys = {
            self._normalise(value)
            for value in strengths
        }
        transferable = []

        for skill in getattr(report, "skills", []) or []:
            name = self._clean(
                getattr(skill, "name", ""),
                "",
            )
            if not name:
                continue

            level = int(getattr(skill, "level", 0) or 0)
            evidence = self._clean(
                getattr(skill, "evidence", ""),
                "",
            )

            # This is a presentation category only. The existing skill level and
            # evidence are preserved; no new fit score is created.
            if (
                50 <= level < 75
                and self._normalise(name) not in strength_keys
            ):
                label = name
                if evidence:
                    label = f"{name} — related evidence available"
                transferable.append(label)

        return self._unique(transferable)

    def _risk_summaries(self, risks) -> list[str]:
        summaries = []
        for risk in risks or []:
            title = self._clean(
                getattr(risk, "title", ""),
                "Evidence to validate",
            )
            detail = self._clean(
                getattr(risk, "detail", ""),
                "Current evidence is limited.",
            )
            summaries.append(f"{title}: {detail}")
        return self._unique(summaries)

    def _recommendation_label(
        self,
        recommendation: str,
        official_score: float,
    ) -> str:
        value = recommendation.lower()

        if any(
            token in value
            for token in (
                "strong",
                "recommend",
                "proceed",
                "advance",
                "shortlist",
            )
        ):
            return "Proceed with human validation"

        if any(
            token in value
            for token in (
                "hold",
                "review",
                "validate",
                "conditional",
            )
        ):
            return "Focused validation required"

        if any(
            token in value
            for token in (
                "reject",
                "do not",
                "not recommend",
            )
        ):
            return "Material gaps require review"

        if official_score >= 75:
            return "Proceed with human validation"
        if official_score >= 50:
            return "Focused validation required"
        return "Material gaps require review"

    def _confidence_label(self, score: int) -> str:
        if score >= 80:
            return "High"
        if score >= 60:
            return "Moderate"
        if score >= 40:
            return "Limited"
        return "Low"

    def _unique(self, values) -> list[str]:
        output = []
        seen = set()

        for value in values or []:
            clean = self._clean(value, "")
            key = self._normalise(clean)

            if clean and key not in seen:
                output.append(clean)
                seen.add(key)

        return output

    def _clean(
        self,
        value,
        fallback: str,
    ) -> str:
        text = " ".join(str(value or "").split())
        return text or fallback

    def _normalise(self, value: str) -> str:
        return " ".join(str(value or "").lower().split())
