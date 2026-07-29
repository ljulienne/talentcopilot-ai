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
    strongest_area: str
    primary_risk: str
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
            strongest_area = self._strongest_area(report, required, pre_scores, post_scores)
            primary_risk = self._primary_risk(
                report,
                strongest_area=strongest_area,
                required=required,
            )
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
                    strongest_area=strongest_area,
                    primary_risk=primary_risk,
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


    @classmethod
    def _strongest_area(
        cls,
        report: Any,
        required: list[Any],
        pre_scores: tuple[tuple[str, float], ...],
        post_scores: tuple[tuple[str, float], ...],
    ) -> str:
        """Return a candidate-grounded strength instead of the first role requirement.

        CandidateWorkspaceService orders skills by evidence strength. We still
        rank explicitly here so the dashboard cannot silently fall back to the
        first requirement in the job description. When the profile has no
        differentiated evidence, we state that rather than inventing a strength.
        """

        skills = list(getattr(report, "skills", []) or [])
        role_skills = [
            item
            for item in skills
            if str(getattr(item, "requirement_type", "")).casefold() == "role requirement"
        ]
        pool = role_skills or skills
        if pool:
            ranked = sorted(
                pool,
                key=lambda item: (
                    -float(getattr(item, "level", 0) or 0),
                    cls._evidence_priority(getattr(item, "status", "")),
                    str(getattr(item, "name", "")).casefold(),
                ),
            )
            best = ranked[0]
            best_level = float(getattr(best, "level", 0) or 0)
            second_level = (
                float(getattr(ranked[1], "level", 0) or 0)
                if len(ranked) > 1
                else None
            )
            name = cls._clean_label(getattr(best, "name", ""))
            if name and (
                best_level >= 55
                or second_level is None
                or best_level > second_level
            ):
                return name

        scores = post_scores or pre_scores
        if scores:
            ranked_scores = sorted(scores, key=lambda item: (-float(item[1]), item[0].casefold()))
            best_name, best_score = ranked_scores[0]
            second_score = float(ranked_scores[1][1]) if len(ranked_scores) > 1 else None
            if float(best_score) >= 55 and (second_score is None or float(best_score) > second_score):
                return cls._clean_label(best_name)

        return "No differentiated strength established"

    @classmethod
    def _primary_risk(
        cls,
        report: Any,
        *,
        strongest_area: str,
        required: list[Any],
    ) -> str:
        """Return the highest-priority candidate-specific risk.

        Risks from Candidate Intelligence are preferred because they preserve
        the decision engine's evidence basis and severity. The strongest area is
        not reused as a generic risk when another grounded concern exists.
        """

        risks = list(getattr(report, "risks", []) or [])
        severity = {"high": 0, "medium": 1, "low": 2}
        ranked = sorted(
            risks,
            key=lambda item: (
                severity.get(str(getattr(item, "severity", "medium")).casefold(), 1),
                str(getattr(item, "classification", "")).casefold() != "confirmed risk",
                str(getattr(item, "title", "")).casefold(),
            ),
        )
        strongest_key = cls._normalise_label(strongest_area)
        duplicate_title = ""
        for item in ranked:
            title = cls._clean_label(getattr(item, "title", ""))
            related = cls._clean_label(getattr(item, "related_requirement", ""))
            if not title and related:
                title = f"{related} requires validation"
            if not title:
                continue
            if cls._normalise_label(title) != strongest_key:
                return title
            duplicate_title = title

        if duplicate_title:
            return f"{duplicate_title} requires validation"

        shortfalls = []
        for item in required:
            required_level = float(getattr(item, "required_level", 0) or 0)
            effective = (
                getattr(item, "interviewer_level", None)
                if getattr(item, "interviewer_level", None) is not None
                else getattr(item, "ai_estimated_level", 0)
            )
            gap = required_level - float(effective or 0)
            if gap > 0:
                shortfalls.append((gap, cls._clean_label(getattr(item, "competency_name", ""))))
        shortfalls.sort(key=lambda item: (-item[0], item[1].casefold()))
        for _, name in shortfalls:
            if name and cls._normalise_label(name) != strongest_key:
                return f"{name} requires validation"
        if shortfalls and shortfalls[0][1]:
            return f"{shortfalls[0][1]} requires validation"
        return "No critical risk identified"

    @staticmethod
    def _evidence_priority(status: Any) -> int:
        priorities = {
            "strong evidence": 0,
            "moderate evidence": 1,
            "limited evidence": 2,
            "not demonstrated": 3,
        }
        return priorities.get(str(status or "").casefold(), 4)

    @staticmethod
    def _clean_label(value: Any) -> str:
        return " ".join(str(value or "").split())

    @staticmethod
    def _normalise_label(value: Any) -> str:
        return "".join(character for character in str(value or "").casefold() if character.isalnum())

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
