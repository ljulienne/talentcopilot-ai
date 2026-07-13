"""Presentation model for the Recruitment Workspace cockpit.

This service reads the official RecruitmentSession and the existing
RecruitmentWorkspaceReport. It does not recalculate matching, ranking, evidence,
or recommendations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class WorkflowStepView:
    key: str
    label: str
    status: str
    detail: str


@dataclass(frozen=True)
class RecruitmentCockpitView:
    role_title: str
    session_id: str
    candidates_count: int
    analyzed_count: int
    top_candidate_name: str
    top_candidate_score: float
    progress_percent: int
    current_stage: str
    next_action_title: str
    next_action_detail: str
    workflow_steps: tuple[WorkflowStepView, ...]


class RecruitmentCockpitService:
    """Build a decision-oriented view from already-computed session results."""

    def build(self, session, workspace_report) -> RecruitmentCockpitView:
        ranked = list(getattr(session, "ranked_analyses", []) or [])
        ranked = sorted(
            ranked,
            key=lambda item: (
                int(getattr(item, "rank", 9999) or 9999),
                -float(getattr(item, "match_score", 0.0) or 0.0),
            ),
        )

        candidate_count = int(
            getattr(workspace_report, "candidates_count", 0)
            or getattr(session, "candidate_count", 0)
            or len(ranked)
        )
        analyzed_count = int(
            getattr(workspace_report, "analyzed_count", 0)
            or getattr(session, "analyzed_count", 0)
            or len(ranked)
        )

        top = ranked[0] if ranked else None
        top_name = str(getattr(top, "candidate_name", "") or "Not available")
        top_score = float(getattr(top, "match_score", 0.0) or 0.0)

        job_ready = bool(
            str(getattr(session, "role_title", "") or "").strip()
            and str(getattr(session, "role_title", "") or "").strip().lower()
            not in {"untitled recruitment", "recruitment"}
        )
        candidates_ready = candidate_count > 0
        analysis_ready = analyzed_count > 0 and bool(ranked)

        interview_ready = self._has_interview_output(session)
        decision_ready = self._has_decision_output(session)

        steps = (
            WorkflowStepView(
                "mission",
                "Mission",
                "done" if job_ready else "active",
                "Job description and recruitment context are ready."
                if job_ready
                else "Upload or define the job description.",
            ),
            WorkflowStepView(
                "candidates",
                "Candidates",
                "done" if candidates_ready else ("active" if job_ready else "pending"),
                f"{candidate_count} candidate{'s' if candidate_count != 1 else ''} imported."
                if candidates_ready
                else "Upload one or more candidate CVs.",
            ),
            WorkflowStepView(
                "analysis",
                "AI Analysis",
                "done" if analysis_ready else ("active" if candidates_ready else "pending"),
                f"{analyzed_count} candidate{'s' if analyzed_count != 1 else ''} analysed."
                if analysis_ready
                else "Run the official matching and ranking pipeline.",
            ),
            WorkflowStepView(
                "interview",
                "Interview",
                "done" if interview_ready else ("active" if analysis_ready else "pending"),
                "Interview preparation is available."
                if interview_ready
                else "Review the leading candidate and prepare the interview.",
            ),
            WorkflowStepView(
                "decision",
                "Decision",
                "done" if decision_ready else ("active" if interview_ready else "pending"),
                "Decision output is available."
                if decision_ready
                else "Compare finalists and complete human validation.",
            ),
        )

        completed = sum(1 for step in steps if step.status == "done")
        progress = int(round((completed / len(steps)) * 100))

        active = next(
            (step for step in steps if step.status == "active"),
            steps[-1],
        )
        next_title, next_detail = self._next_action(
            job_ready=job_ready,
            candidates_ready=candidates_ready,
            analysis_ready=analysis_ready,
            interview_ready=interview_ready,
            decision_ready=decision_ready,
            top_name=top_name,
        )

        return RecruitmentCockpitView(
            role_title=str(
                getattr(workspace_report, "role_title", "")
                or getattr(session, "role_title", "")
                or "Active recruitment"
            ),
            session_id=str(
                getattr(workspace_report, "session_id", "")
                or getattr(session, "session_id", "")
                or "-"
            ),
            candidates_count=candidate_count,
            analyzed_count=analyzed_count,
            top_candidate_name=top_name,
            top_candidate_score=top_score,
            progress_percent=progress,
            current_stage=active.label,
            next_action_title=next_title,
            next_action_detail=next_detail,
            workflow_steps=steps,
        )

    def _has_interview_output(self, session) -> bool:
        for attribute in (
            "interview_reports",
            "interview_guides",
            "interview_results",
            "interview_context",
        ):
            value = getattr(session, attribute, None)
            if value:
                return True
        return False

    def _has_decision_output(self, session) -> bool:
        for attribute in (
            "decision_report",
            "decision_board",
            "final_decision",
            "executive_report",
        ):
            value = getattr(session, attribute, None)
            if value:
                return True
        return False

    def _next_action(
        self,
        *,
        job_ready: bool,
        candidates_ready: bool,
        analysis_ready: bool,
        interview_ready: bool,
        decision_ready: bool,
        top_name: str,
    ) -> tuple[str, str]:
        if not job_ready:
            return (
                "Define the mission",
                "Upload the job description so TalentCopilot can establish the official recruitment context.",
            )
        if not candidates_ready:
            return (
                "Add candidates",
                "Upload candidate CVs to create the official recruitment session.",
            )
        if not analysis_ready:
            return (
                "Run AI analysis",
                "Launch the official matching pipeline to create scores and ranking.",
            )
        if not interview_ready:
            return (
                f"Review {top_name}",
                "Open Candidate Intelligence, validate the evidence, then prepare the interview strategy.",
            )
        if not decision_ready:
            return (
                "Compare and decide",
                "Compare finalists and complete the human decision review.",
            )
        return (
            "Generate the decision report",
            "Review the executive summary and export the final evidence-led report.",
        )
