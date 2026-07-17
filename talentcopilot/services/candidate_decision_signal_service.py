"""Evidence-based recruiter signals derived from the official recruitment session.

This service never recalculates the official match score or rank. It converts
existing candidate evidence, required skills, decision reports and confidence
into concise recruiter-facing signals for comparison views.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional, Sequence


@dataclass(frozen=True)
class CandidateDecisionSignals:
    recommendation: str
    key_strength: str
    key_risk: str
    executive_summary: str
    confidence: Optional[float]
    evidence: tuple[str, ...] = ()


class CandidateDecisionSignalService:
    """Build deterministic, evidence-grounded candidate decision signals."""

    _GENERIC_VALUES = {
        "review",
        "review carefully",
        "review required",
        "relevant experience",
        "requires validation",
    }

    def build(self, analysis: Any, session: Any) -> CandidateDecisionSignals:
        score = self._number(
            getattr(analysis, "official_match_score", None),
            getattr(analysis, "match_score", None),
            default=0.0,
        )
        confidence = self._confidence(analysis)
        candidate = self._candidate_record(analysis, session)
        required_skills = self._strings(
            self._mapping(getattr(session, "job", {})).get("required_skills", [])
        )
        candidate_skills = self._strings(candidate.get("skills", []))
        achievements = self._strings(candidate.get("achievements", []))

        matched, missing = self._skill_alignment(required_skills, candidate_skills)
        decision_report = getattr(analysis, "decision_report", None)

        recommendation = self._report_recommendation(decision_report)
        if not recommendation:
            recommendation = self._recommendation(score, confidence)

        key_strength = self._report_strength(decision_report)
        if not key_strength:
            key_strength = self._strength(matched, candidate_skills, achievements, score)

        key_risk = self._report_risk(decision_report)
        if not key_risk:
            key_risk = self._risk(missing, confidence, required_skills, score)

        candidate_name = str(
            getattr(analysis, "candidate_name", "Candidate") or "Candidate"
        )
        summary = (
            f"{candidate_name} has an official match of {score:.0f}%"
            f"{self._confidence_phrase(confidence)}. "
            f"{key_strength} Main validation point: {key_risk}"
        )

        evidence = tuple((achievements + matched + candidate_skills)[:5])
        return CandidateDecisionSignals(
            recommendation=recommendation,
            key_strength=key_strength,
            key_risk=key_risk,
            executive_summary=summary,
            confidence=confidence,
            evidence=evidence,
        )

    def _recommendation(self, score: float, confidence: Optional[float]) -> str:
        if confidence is not None and confidence < 50:
            return "Manual review required"
        if score >= 80:
            return "Strong shortlist"
        if score >= 60:
            return "Shortlist with targeted validation"
        if score >= 40:
            return "Consider for adjacent fit"
        if score >= 20:
            return "Low fit — significant gaps"
        return "Do not prioritize"

    def _strength(
        self,
        matched: Sequence[str],
        skills: Sequence[str],
        achievements: Sequence[str],
        score: float,
    ) -> str:
        if matched:
            return "Verified alignment on " + ", ".join(matched[:3])
        if achievements:
            return "Documented evidence: " + self._clip(achievements[0], 110)
        if skills:
            return "Relevant capability in " + ", ".join(skills[:3])
        if score >= 60:
            return "Strong overall role alignment in the official assessment"
        return "No role-specific strength has been evidenced yet"

    def _risk(
        self,
        missing: Sequence[str],
        confidence: Optional[float],
        required: Sequence[str],
        score: float,
    ) -> str:
        if missing:
            return "Validate missing evidence for " + ", ".join(missing[:3])
        if confidence is not None and confidence < 65:
            return "Evidence confidence is limited; confirm claims in interview"
        if required:
            return "Confirm depth, ownership and measurable outcomes in interview"
        if score < 40:
            return "Role alignment is limited and requires substantive validation"
        return "No major gap detected; validate scope and impact"

    def _report_recommendation(self, report: Any) -> str:
        if report is None:
            return ""
        raw = getattr(report, "recommendation", "")
        value = str(getattr(raw, "value", raw) or "").strip()
        if value.casefold() in self._GENERIC_VALUES:
            return ""
        return value

    def _report_strength(self, report: Any) -> str:
        if report is None:
            return ""
        strengths = list(getattr(report, "strengths", []) or [])
        if not strengths:
            return ""
        value = str(getattr(strengths[0], "title", strengths[0]) or "").strip()
        return "" if value.casefold() in self._GENERIC_VALUES else value

    def _report_risk(self, report: Any) -> str:
        if report is None:
            return ""
        concerns = list(getattr(report, "concerns", []) or [])
        if not concerns:
            return ""
        value = str(getattr(concerns[0], "title", concerns[0]) or "").strip()
        return "" if value.casefold() in self._GENERIC_VALUES else value

    def _candidate_record(self, analysis: Any, session: Any) -> Mapping[str, Any]:
        candidate_id = str(getattr(analysis, "candidate_id", "") or "")
        candidate_name = str(getattr(analysis, "candidate_name", "") or "").casefold()
        for item in list(getattr(session, "candidates", []) or []):
            record = self._mapping(item)
            record_id = str(record.get("candidate_id", "") or "")
            record_name = str(record.get("name", "") or "").casefold()
            if candidate_id and record_id == candidate_id:
                return record
            if candidate_name and record_name == candidate_name:
                return record
        return {}

    def _confidence(self, analysis: Any) -> Optional[float]:
        value = getattr(analysis, "official_confidence_score", None)
        if value is None:
            value = self._mapping(getattr(analysis, "score_breakdown", {})).get(
                "confidence"
            )
        return self._optional_number(value)

    def _skill_alignment(
        self, required: Sequence[str], candidate: Sequence[str]
    ) -> tuple[list[str], list[str]]:
        candidate_by_key = {self._normalise(value): value for value in candidate}
        matched, missing = [], []
        for skill in required:
            key = self._normalise(skill)
            if key in candidate_by_key:
                matched.append(skill)
            else:
                missing.append(skill)
        return matched, missing

    def _confidence_phrase(self, confidence: Optional[float]) -> str:
        return "" if confidence is None else f" and AI confidence of {confidence:.0f}%"

    def _strings(self, values: Iterable[Any]) -> list[str]:
        result = []
        for value in values or []:
            text = str(value or "").strip()
            if text and text not in result:
                result.append(text)
        return result

    def _mapping(self, value: Any) -> Mapping[str, Any]:
        return value if isinstance(value, Mapping) else {}

    def _number(self, *values: Any, default: float) -> float:
        for value in values:
            parsed = self._optional_number(value)
            if parsed is not None:
                return parsed
        return default

    def _optional_number(self, value: Any) -> Optional[float]:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _normalise(self, value: str) -> str:
        return " ".join(str(value or "").casefold().replace("-", " ").split())

    def _clip(self, value: str, limit: int) -> str:
        text = " ".join(str(value or "").split())
        return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"
