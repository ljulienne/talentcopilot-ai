from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Optional

from talentcopilot.services.candidate_workspace_service import CandidateWorkspaceService
from talentcopilot.services.competency_matrix_service import CompetencyMatrixService


@dataclass(frozen=True)
class CandidateOverview:
    candidate_id: str
    candidate_name: str
    official_rank: int
    official_match_score: float
    confidence_score: Optional[float]
    recommendation: str
    pre_interview_alignment: Optional[float]
    post_interview_alignment: Optional[float]
    alignment_delta: Optional[float]
    interview_progress: int
    interview_status: str
    evidence_coverage: Optional[int]
    competency_scores_pre: tuple[tuple[str, float], ...]
    competency_scores_post: tuple[tuple[str, float], ...]
    critical_gaps: tuple[str, ...]
    additional_competencies: tuple[str, ...]


@dataclass(frozen=True)
class CompetencyCoverage:
    competency: str
    pre_interview_coverage: int
    post_interview_coverage: Optional[int]
    candidate_count: int
    assessed_candidate_count: int


@dataclass(frozen=True)
class RecruitmentOverview:
    session_id: str
    role_title: str
    candidate_count: int
    analyzed_count: int
    strong_fit_count: int
    potential_fit_count: int
    partial_fit_count: int
    low_fit_count: int
    shortlisted_count: int
    interview_completed_count: int
    interview_in_progress_count: int
    ready_for_decision_count: int
    candidates: tuple[CandidateOverview, ...]
    competency_coverage: tuple[CompetencyCoverage, ...]
    next_action_title: str
    next_action_detail: str
    next_action_page: str
    next_action_button: str

    @property
    def has_analysis(self) -> bool:
        return bool(self.candidates)

    @property
    def has_post_interview_data(self) -> bool:
        return any(item.post_interview_alignment is not None for item in self.candidates)


class RecruitmentOverviewService:
    """Build a visual, presentation-only recruitment overview.

    Official match scores and ranks are read from the RecruitmentSession and are
    never recalculated. Competency alignment is a separate advisory indicator:
    it compares role-required levels with the pre-interview AI estimate and, when
    available, the interviewer level stored in the versioned competency matrix.
    """

    STRONG_FIT = 75.0
    POTENTIAL_FIT = 55.0
    PARTIAL_FIT = 35.0

    def __init__(
        self,
        *,
        candidate_service: CandidateWorkspaceService | None = None,
        competency_service: CompetencyMatrixService | None = None,
    ) -> None:
        self.candidate_service = candidate_service or CandidateWorkspaceService()
        self.competency_service = competency_service or CompetencyMatrixService()

    def build(self, session: Any, workflow_context: Any = None) -> RecruitmentOverview:
        if session is None:
            raise ValueError("An active RecruitmentSession is required.")

        reports = self.candidate_service.build_all(session)
        evaluations = dict(getattr(workflow_context, "interview_evaluations", {}) or {})
        assessed_ids = set(getattr(workflow_context, "interview_assessed_candidate_ids", []) or [])
        shortlisted_ids = list(
            getattr(workflow_context, "finalist_candidate_ids", [])
            or getattr(workflow_context, "shortlisted_candidate_ids", [])
            or []
        )

        candidates: list[CandidateOverview] = []
        for report in reports:
            candidate_id = str(getattr(report, "candidate_id", "") or report.candidate_name)
            matrix = self.competency_service.build(report, session)
            required = [
                item
                for item in matrix.active_competencies()
                if item.is_job_requirement and float(item.required_level or 0.0) > 0
            ]

            pre_scores = tuple(
                (item.competency_name, self._alignment(item.ai_estimated_level, item.required_level))
                for item in required
            )
            pre_alignment = self._average(value for _, value in pre_scores)

            assessed_required = [item for item in required if item.interviewer_level is not None]
            has_interview = bool(assessed_required) or candidate_id in assessed_ids or candidate_id in evaluations
            post_scores = tuple(
                (
                    item.competency_name,
                    self._alignment(
                        item.interviewer_level
                        if item.interviewer_level is not None
                        else item.ai_estimated_level,
                        item.required_level,
                    ),
                )
                for item in required
            ) if has_interview else ()
            post_alignment = self._average(value for _, value in post_scores) if post_scores else None
            delta = (
                round(post_alignment - pre_alignment, 1)
                if post_alignment is not None and pre_alignment is not None
                else None
            )

            progress = int(round(100 * len(assessed_required) / max(1, len(required)))) if required else 0
            matrix_status = str(getattr(matrix, "status", "pre_interview") or "pre_interview")
            if matrix_status == "post_interview" or candidate_id in assessed_ids:
                interview_status = "Completed"
            elif progress > 0 or matrix_status == "interview_in_progress":
                interview_status = "In progress"
            else:
                interview_status = "Not started"

            evaluation = evaluations.get(candidate_id, {})
            evidence_coverage = evaluation.get("evidence_coverage")
            try:
                evidence_coverage = int(evidence_coverage) if evidence_coverage is not None else None
            except (TypeError, ValueError):
                evidence_coverage = None

            active_gaps = tuple(
                item.competency_name
                for item in required
                if (
                    item.interviewer_level
                    if item.interviewer_level is not None
                    else item.ai_estimated_level
                ) < item.required_level
            )
            additions = tuple(
                item.competency_name
                for item in matrix.active_competencies()
                if not item.is_job_requirement
            )

            confidence = self._confidence(report)
            candidates.append(
                CandidateOverview(
                    candidate_id=candidate_id,
                    candidate_name=str(report.candidate_name),
                    official_rank=int(getattr(report, "rank", 0) or 0),
                    official_match_score=float(getattr(report, "match_score", 0.0) or 0.0),
                    confidence_score=confidence,
                    recommendation=str(getattr(report, "recommendation_label", "") or getattr(report, "recommendation", "Review required")),
                    pre_interview_alignment=pre_alignment,
                    post_interview_alignment=post_alignment,
                    alignment_delta=delta,
                    interview_progress=progress,
                    interview_status=interview_status,
                    evidence_coverage=evidence_coverage,
                    competency_scores_pre=pre_scores,
                    competency_scores_post=post_scores,
                    critical_gaps=active_gaps,
                    additional_competencies=additions,
                )
            )

        candidates.sort(key=lambda item: (item.official_rank or 9999, -item.official_match_score, item.candidate_name.casefold()))
        coverage = self._coverage(candidates)

        strong = sum(item.official_match_score >= self.STRONG_FIT for item in candidates)
        potential = sum(self.POTENTIAL_FIT <= item.official_match_score < self.STRONG_FIT for item in candidates)
        partial = sum(self.PARTIAL_FIT <= item.official_match_score < self.POTENTIAL_FIT for item in candidates)
        low = sum(item.official_match_score < self.PARTIAL_FIT for item in candidates)
        completed = sum(item.interview_status == "Completed" for item in candidates)
        in_progress = sum(item.interview_status == "In progress" for item in candidates)
        ready = sum(
            item.interview_status == "Completed" and item.interview_progress >= 80
            for item in candidates
        )

        shortlist_count = len(shortlisted_ids) if shortlisted_ids else min(3, len(candidates))
        next_title, next_detail, next_page, next_button = self._next_action(
            candidates,
            completed=completed,
            in_progress=in_progress,
            ready=ready,
        )

        return RecruitmentOverview(
            session_id=str(getattr(session, "session_id", "session") or "session"),
            role_title=str(getattr(session, "role_title", "Recruitment") or "Recruitment"),
            candidate_count=int(getattr(session, "candidate_count", len(candidates)) or len(candidates)),
            analyzed_count=int(getattr(session, "analyzed_count", len(candidates)) or len(candidates)),
            strong_fit_count=strong,
            potential_fit_count=potential,
            partial_fit_count=partial,
            low_fit_count=low,
            shortlisted_count=shortlist_count,
            interview_completed_count=completed,
            interview_in_progress_count=in_progress,
            ready_for_decision_count=ready,
            candidates=tuple(candidates),
            competency_coverage=coverage,
            next_action_title=next_title,
            next_action_detail=next_detail,
            next_action_page=next_page,
            next_action_button=next_button,
        )

    @staticmethod
    def _alignment(level: float, required: float) -> float:
        required_value = float(required or 0.0)
        if required_value <= 0:
            return 0.0
        return round(max(0.0, min(100.0, 100.0 * float(level or 0.0) / required_value)), 1)

    @staticmethod
    def _average(values: Iterable[float]) -> Optional[float]:
        numbers = [float(value) for value in values]
        if not numbers:
            return None
        return round(sum(numbers) / len(numbers), 1)

    @staticmethod
    def _confidence(report: Any) -> Optional[float]:
        breakdown = dict(getattr(report, "score_breakdown", {}) or {})
        value = breakdown.get("confidence")
        try:
            return float(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    def _coverage(self, candidates: list[CandidateOverview]) -> tuple[CompetencyCoverage, ...]:
        names: list[str] = []
        for candidate in candidates:
            for name, _ in candidate.competency_scores_pre:
                if name not in names:
                    names.append(name)

        rows: list[CompetencyCoverage] = []
        for name in names:
            pre = [dict(item.competency_scores_pre).get(name) for item in candidates]
            pre_values = [value for value in pre if value is not None]
            post = [dict(item.competency_scores_post).get(name) for item in candidates if item.competency_scores_post]
            post_values = [value for value in post if value is not None]
            rows.append(
                CompetencyCoverage(
                    competency=name,
                    # Use the same normalized values as the heatmap. A score of
                    # 92% therefore contributes 92%, instead of disappearing
                    # behind a binary 100%-only threshold.
                    pre_interview_coverage=int(round(sum(pre_values) / max(1, len(pre_values)))),
                    post_interview_coverage=(
                        int(round(sum(post_values) / max(1, len(post_values))))
                        if post_values
                        else None
                    ),
                    candidate_count=len(pre_values),
                    assessed_candidate_count=len(post_values),
                )
            )
        return tuple(sorted(rows, key=lambda item: (item.pre_interview_coverage, item.competency.casefold())))

    @staticmethod
    def _next_action(
        candidates: list[CandidateOverview],
        *,
        completed: int,
        in_progress: int,
        ready: int,
    ) -> tuple[str, str, str, str]:
        if not candidates:
            return (
                "Analyse the candidate pool",
                "Upload the job description and candidate CVs to create the visual overview.",
                "Recruitment Workspace",
                "Open recruitment workspace",
            )
        if completed == 0 and in_progress == 0:
            return (
                "Review the leading candidates",
                "Open Candidate Intelligence to validate the strongest matches and select interview priorities.",
                "Candidate Intelligence",
                "Review candidates",
            )
        if ready < 2:
            remaining = max(1, 2 - ready)
            return (
                "Complete interview evidence",
                f"At least {remaining} additional candidate assessment(s) should be completed before finalist comparison.",
                "Interview Intelligence",
                "Continue interviews",
            )
        return (
            "Compare the finalists",
            "Two or more candidates have sufficiently complete post-interview assessments for a structured comparison.",
            "Comparison",
            "Compare finalists",
        )


__all__ = [
    "CandidateOverview",
    "CompetencyCoverage",
    "RecruitmentOverview",
    "RecruitmentOverviewService",
]
