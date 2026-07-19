"""Presentation state for the mission-centric recruitment workspace.

This module is deliberately independent from Streamlit and from matching engines.
It consumes the official RecruitmentSession and never recalculates scores or ranks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Optional, Tuple

from talentcopilot.models.recruitment_session import RecruitmentSession


@dataclass(frozen=True)
class CandidateMissionView:
    candidate_id: str
    name: str
    rank: int
    match_score: float
    decision_score: Optional[float]
    confidence_score: Optional[float]
    recommendation: str
    rationale: str
    strengths: Tuple[str, ...]
    risks: Tuple[str, ...]


@dataclass(frozen=True)
class RecruitmentMissionState:
    session_id: str
    role_title: str
    status: str
    candidate_count: int
    analyzed_count: int
    progress_percent: int
    stage: str
    candidates: Tuple[CandidateMissionView, ...]
    recommended_candidate: str
    recommended_score: float
    average_confidence: Optional[float]
    summary: str

    @property
    def has_analysis(self) -> bool:
        return bool(self.candidates)


def _clean_lines(values: Iterable[Any]) -> Tuple[str, ...]:
    cleaned = []
    for value in values or ():
        text = str(value or "").strip()
        if text and text not in cleaned:
            cleaned.append(text)
    return tuple(cleaned)


def _candidate_payload(session: RecruitmentSession, candidate_id: str, name: str) -> dict:
    for candidate in session.candidates or []:
        if str(candidate.get("candidate_id", "")) == candidate_id:
            return candidate
        if str(candidate.get("name", "")) == name:
            return candidate
    return {}


def _recommendation_and_rationale(analysis: Any, candidate: dict) -> tuple[str, str]:
    recommendation = str(candidate.get("upload_recommendation", "") or "").strip()
    rationale = str(candidate.get("upload_rationale", "") or "").strip()

    for note in getattr(analysis, "notes", []) or []:
        text = str(note or "").strip()
        if text.lower().startswith("recommendation:") and not recommendation:
            recommendation = text.split(":", 1)[1].strip()
        elif text and not text.lower().startswith("created from") and not text.lower().startswith("recommendation:"):
            if not rationale:
                rationale = text

    return recommendation or "Review required", rationale


def _progress(session: RecruitmentSession) -> tuple[int, str]:
    if not session.candidate_count:
        return 10, "Mission setup"
    if not session.analyzed_count:
        return 30, "Candidate intake"
    if session.analyzed_count < session.candidate_count:
        ratio = session.analyzed_count / max(1, session.candidate_count)
        return int(35 + ratio * 35), "Analysis in progress"
    if session.ranked_analyses:
        return 80, "Decision preparation"
    return 65, "Analysis complete"


def _summary(role_title: str, candidates: Tuple[CandidateMissionView, ...]) -> str:
    if not candidates:
        return (
            f"The {role_title} mission is ready for candidate documents. "
            "Upload the job description and CVs to begin the official analysis."
        )

    lead = candidates[0]
    alternative = candidates[1] if len(candidates) > 1 else None
    message = (
        f"{lead.name} is currently the leading candidate with an official match of "
        f"{lead.match_score:.0f}%. {lead.rationale or lead.recommendation}"
    )
    if alternative:
        message += (
            f" {alternative.name} is the closest alternative at "
            f"{alternative.match_score:.0f}%."
        )
    return message


def build_recruitment_mission_state(session: RecruitmentSession) -> RecruitmentMissionState:
    """Build UI state from the official source of truth without recalculation."""
    if session is None:
        raise ValueError("An official RecruitmentSession is required.")

    views = []
    for index, analysis in enumerate(session.ranked_analyses, start=1):
        candidate = _candidate_payload(
            session,
            str(getattr(analysis, "candidate_id", "") or ""),
            str(getattr(analysis, "candidate_name", "Candidate") or "Candidate"),
        )
        recommendation, rationale = _recommendation_and_rationale(analysis, candidate)
        strengths = _clean_lines(candidate.get("achievements", []) or [])[:3]
        risks = _clean_lines(getattr(analysis, "errors", []) or [])[:3]
        views.append(
            CandidateMissionView(
                candidate_id=str(getattr(analysis, "candidate_id", "") or ""),
                name=str(getattr(analysis, "candidate_name", "Candidate") or "Candidate"),
                rank=int(getattr(analysis, "official_rank", None) or index),
                match_score=float(getattr(analysis, "official_match_score", 0.0) or 0.0),
                decision_score=getattr(analysis, "official_decision_score", None),
                confidence_score=getattr(analysis, "official_confidence_score", None),
                recommendation=recommendation,
                rationale=rationale,
                strengths=strengths,
                risks=risks,
            )
        )

    candidates = tuple(sorted(views, key=lambda item: (item.rank, -item.match_score, item.name.casefold())))
    progress, stage = _progress(session)
    confidences = [item.confidence_score for item in candidates if item.confidence_score is not None]
    average_confidence = round(sum(confidences) / len(confidences), 1) if confidences else None
    lead = candidates[0] if candidates else None

    return RecruitmentMissionState(
        session_id=str(session.session_id),
        role_title=str(session.role_title),
        status=str(getattr(session.status, "value", session.status)),
        candidate_count=int(session.candidate_count),
        analyzed_count=int(session.analyzed_count),
        progress_percent=progress,
        stage=stage,
        candidates=candidates,
        recommended_candidate=lead.name if lead else "Not available",
        recommended_score=lead.match_score if lead else 0.0,
        average_confidence=average_confidence,
        summary=_summary(str(session.role_title), candidates),
    )
