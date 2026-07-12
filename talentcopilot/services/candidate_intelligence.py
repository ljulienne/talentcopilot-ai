"""Build explainable Candidate Intelligence from existing workspace reports.

The service is deliberately presentation-oriented. It keeps the existing match
score unchanged and derives supporting indicators only from data already
available in ``CandidateWorkspaceReport``.
"""

from __future__ import annotations

from talentcopilot.models.candidate_intelligence import (
    CandidateIntelligenceRisk,
    CandidateIntelligenceSnapshot,
    CandidateRiskType,
)


def _clamp(value: float) -> int:
    return max(0, min(100, int(round(value))))


def _clean(value: object, fallback: str = "Not available") -> str:
    text = str(value or "").strip()
    return text or fallback


class CandidateIntelligenceService:
    """Convert an existing candidate report into a decision-oriented view."""

    def build(self, report) -> CandidateIntelligenceSnapshot:
        skills = list(getattr(report, "skills", []) or [])
        evidence = list(getattr(report, "evidence", []) or [])
        source_risks = list(getattr(report, "risks", []) or [])
        interview_focus = list(getattr(report, "interview_focus", []) or [])

        mission_fit = float(getattr(report, "match_score", 0.0) or 0.0)

        useful_evidence = [
            item
            for item in evidence
            if "not available" not in _clean(getattr(item, "title", "")).lower()
            and "no detailed" not in _clean(getattr(item, "detail", "")).lower()
        ]
        high_evidence = sum(
            1
            for item in useful_evidence
            if _clean(getattr(item, "strength", "Medium")).lower() == "high"
        )
        evidenced_skills = sum(
            1 for skill in skills if _clean(getattr(skill, "evidence", ""), "")
        )

        evidence_coverage = _clamp(
            min(60, len(useful_evidence) * 12)
            + min(30, evidenced_skills * 5)
            + min(10, high_evidence * 5)
        )

        contradiction_penalty = min(20, len(source_risks) * 5)
        decision_confidence = _clamp(
            (mission_fit * 0.55) + (evidence_coverage * 0.45) - contradiction_penalty
        )

        skill_levels = [
            max(0, min(100, int(getattr(skill, "level", 0) or 0)))
            for skill in skills
        ]
        average_skill = sum(skill_levels) / len(skill_levels) if skill_levels else 0
        breadth = min(20, len(skills) * 3)
        potential_signal = _clamp((average_skill * 0.65) + breadth + (high_evidence * 3))

        ranked_skills = sorted(
            skills,
            key=lambda skill: int(getattr(skill, "level", 0) or 0),
            reverse=True,
        )
        strengths = tuple(
            _clean(getattr(skill, "name", "Relevant capability"))
            for skill in ranked_skills[:4]
        )
        if not strengths:
            strengths = tuple(
                _clean(getattr(item, "title", "Candidate evidence"))
                for item in useful_evidence[:3]
            )

        risks = tuple(
            CandidateIntelligenceRisk(
                title=_clean(getattr(item, "title", "Risk to validate")),
                detail=_clean(getattr(item, "detail", "Validate during human review.")),
                severity=_clean(getattr(item, "severity", "Medium")),
                risk_type=CandidateRiskType.EVIDENCED,
            )
            for item in source_risks[:4]
        )

        missing_evidence: list[str] = []
        for skill in reversed(ranked_skills):
            level = int(getattr(skill, "level", 0) or 0)
            evidence_text = _clean(getattr(skill, "evidence", ""), "")
            if level < 75 or not evidence_text:
                item = f"Validate depth of {_clean(getattr(skill, 'name', None), 'this capability')}"
                if item not in missing_evidence:
                    missing_evidence.append(item)
            if len(missing_evidence) >= 3:
                break

        generic_unknowns = (
            "Quantified scope and measurable impact",
            "Stakeholder context and individual contribution",
            "Current motivation and role constraints",
        )
        for item in generic_unknowns:
            if len(missing_evidence) >= 3:
                break
            if item not in missing_evidence:
                missing_evidence.append(item)

        unknown_risks = tuple(
            CandidateIntelligenceRisk(
                title=item,
                detail="No conclusive evidence is available in the current profile.",
                severity="Unknown",
                risk_type=CandidateRiskType.UNKNOWN,
            )
            for item in missing_evidence[:3]
        )
        combined_risks = risks + unknown_risks

        if not interview_focus:
            interview_focus = [
                f"Validate {_clean(getattr(skill, 'name', None), 'the strongest capability')} with a concrete example."
                for skill in ranked_skills[:2]
            ]
        if not interview_focus:
            interview_focus = ["Validate the candidate's most important claims with measurable examples."]

        recommendation = _clean(getattr(report, "recommendation", None), "Human review required")
        top_strength = strengths[0] if strengths else "the available profile evidence"
        if evidence_coverage < 45:
            explanation = (
                f"The existing mission fit is {mission_fit:.0f}%, supported mainly by {top_strength}. "
                "Evidence coverage remains limited, so the recommendation should be validated through structured interview evidence."
            )
        elif combined_risks:
            explanation = (
                f"The existing mission fit is {mission_fit:.0f}% and is supported by {top_strength}. "
                f"Decision confidence is moderated by {len(combined_risks)} risk or uncertainty signal(s) requiring human validation."
            )
        else:
            explanation = (
                f"The existing mission fit is {mission_fit:.0f}% with consistent evidence led by {top_strength}. "
                "The final decision remains subject to human validation."
            )

        evidence_summary = (
            f"{len(useful_evidence)} usable evidence item(s), {evidenced_skills} skill signal(s), "
            f"and {len(source_risks)} documented risk(s)."
        )

        return CandidateIntelligenceSnapshot(
            candidate_name=_clean(getattr(report, "candidate_name", None), "Candidate"),
            mission_fit=mission_fit,
            evidence_coverage=evidence_coverage,
            decision_confidence=decision_confidence,
            potential_signal=potential_signal,
            recommendation=recommendation,
            recommendation_explanation=explanation,
            strengths=strengths,
            risks=combined_risks,
            missing_evidence=tuple(missing_evidence[:3]),
            interview_strategy=tuple(_clean(item) for item in interview_focus[:5]),
            evidence_summary=evidence_summary,
        )
