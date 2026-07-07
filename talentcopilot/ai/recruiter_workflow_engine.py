from typing import Any, List

from talentcopilot.models.recruiter_workflow import (
    RecruiterWorkflowReport,
    WorkflowStage,
    WorkflowStageName,
    WorkflowStageStatus,
)


class RecruiterWorkflowEngine:
    """
    Derives a recruiter-facing workflow from a RecruitmentSession.
    """

    def build_workflow(self, session: Any) -> RecruiterWorkflowReport:
        role_title = getattr(session, "role_title", "Role")
        session_id = getattr(session, "session_id", "session")
        analyses = list(getattr(session, "analyses", []) or [])
        candidates = list(getattr(session, "candidates", []) or [])

        stages = [
            self._intake_stage(session),
            self._analysis_stage(candidates, analyses),
            self._shortlist_stage(analyses),
            self._decision_stage(analyses),
            self._interview_stage(analyses),
            self._reporting_stage(analyses),
        ]

        blockers = [stage.explanation for stage in stages if stage.status == WorkflowStageStatus.BLOCKED]
        shortlist = self._shortlist(analyses)
        overall = self._overall_status(stages)
        next_action = self._next_action(stages)

        return RecruiterWorkflowReport(
            role_title=role_title,
            session_id=session_id,
            overall_status=overall,
            stages=stages,
            recommended_next_action=next_action,
            shortlist_candidate_names=shortlist,
            blockers=blockers,
        )

    def _intake_stage(self, session: Any) -> WorkflowStage:
        job = getattr(session, "job", {}) or {}
        title = job.get("title")
        required = job.get("required_skills") or job.get("skills") or job.get("competencies")

        if title and required:
            return WorkflowStage(
                name=WorkflowStageName.INTAKE,
                status=WorkflowStageStatus.COMPLETED,
                explanation="Role title and requirements are available.",
                next_action="Continue candidate analysis.",
            )

        return WorkflowStage(
            name=WorkflowStageName.INTAKE,
            status=WorkflowStageStatus.BLOCKED,
            explanation="Role intake is incomplete.",
            next_action="Add role title and required skills.",
        )

    def _analysis_stage(self, candidates: List[Any], analyses: List[Any]) -> WorkflowStage:
        if not candidates:
            return WorkflowStage(
                name=WorkflowStageName.CANDIDATE_ANALYSIS,
                status=WorkflowStageStatus.BLOCKED,
                explanation="No candidates are available.",
                next_action="Add candidates to the session.",
            )

        analyzed = [a for a in analyses if getattr(a, "is_analyzed", False)]
        if len(analyzed) == len(candidates):
            return WorkflowStage(
                name=WorkflowStageName.CANDIDATE_ANALYSIS,
                status=WorkflowStageStatus.COMPLETED,
                explanation="All candidates have been analyzed.",
                next_action="Review shortlist.",
            )

        if analyzed:
            return WorkflowStage(
                name=WorkflowStageName.CANDIDATE_ANALYSIS,
                status=WorkflowStageStatus.IN_PROGRESS,
                explanation=f"{len(analyzed)} of {len(candidates)} candidates analyzed.",
                next_action="Complete remaining candidate analyses.",
            )

        return WorkflowStage(
            name=WorkflowStageName.CANDIDATE_ANALYSIS,
            status=WorkflowStageStatus.READY,
            explanation="Candidates are available but not analyzed yet.",
            next_action="Run Enterprise Pipeline.",
        )

    def _shortlist_stage(self, analyses: List[Any]) -> WorkflowStage:
        shortlist = self._shortlist(analyses)
        if shortlist:
            return WorkflowStage(
                name=WorkflowStageName.SHORTLIST,
                status=WorkflowStageStatus.READY,
                explanation=f"{len(shortlist)} candidate(s) are shortlist-ready.",
                next_action="Review shortlist and compare candidates.",
            )

        return WorkflowStage(
            name=WorkflowStageName.SHORTLIST,
            status=WorkflowStageStatus.NOT_STARTED,
            explanation="No shortlist-ready candidate yet.",
            next_action="Analyze candidates or adjust criteria.",
        )

    def _decision_stage(self, analyses: List[Any]) -> WorkflowStage:
        decisions = [getattr(a, "decision_report", None) for a in analyses if getattr(a, "decision_report", None)]
        if decisions:
            return WorkflowStage(
                name=WorkflowStageName.DECISION_REVIEW,
                status=WorkflowStageStatus.READY,
                explanation=f"{len(decisions)} decision report(s) available.",
                next_action="Open Decision Workspace.",
            )

        return WorkflowStage(
            name=WorkflowStageName.DECISION_REVIEW,
            status=WorkflowStageStatus.NOT_STARTED,
            explanation="No decision report available yet.",
            next_action="Run Decision Intelligence.",
        )

    def _interview_stage(self, analyses: List[Any]) -> WorkflowStage:
        copilot = [getattr(a, "recruiter_copilot_report", None) for a in analyses if getattr(a, "recruiter_copilot_report", None)]
        if copilot:
            return WorkflowStage(
                name=WorkflowStageName.INTERVIEW_PLANNING,
                status=WorkflowStageStatus.READY,
                explanation=f"{len(copilot)} recruiter copilot report(s) available.",
                next_action="Prepare interviews using Copilot guidance.",
            )

        return WorkflowStage(
            name=WorkflowStageName.INTERVIEW_PLANNING,
            status=WorkflowStageStatus.NOT_STARTED,
            explanation="No recruiter copilot guidance available yet.",
            next_action="Generate recruiter guidance.",
        )

    def _reporting_stage(self, analyses: List[Any]) -> WorkflowStage:
        analyzed = [a for a in analyses if getattr(a, "is_analyzed", False)]
        if analyzed:
            return WorkflowStage(
                name=WorkflowStageName.REPORTING,
                status=WorkflowStageStatus.READY,
                explanation="Analysis data is available for reporting.",
                next_action="Generate recruitment report.",
            )

        return WorkflowStage(
            name=WorkflowStageName.REPORTING,
            status=WorkflowStageStatus.NOT_STARTED,
            explanation="No analysis data available for reporting.",
            next_action="Analyze candidates first.",
        )

    def _shortlist(self, analyses: List[Any]) -> List[str]:
        shortlist = []
        for analysis in analyses:
            score = float(getattr(analysis, "match_score", 0) or 0)
            if score >= 70:
                shortlist.append(getattr(analysis, "candidate_name", "Candidate"))
        return shortlist

    def _overall_status(self, stages: List[WorkflowStage]) -> WorkflowStageStatus:
        if any(stage.status == WorkflowStageStatus.BLOCKED for stage in stages):
            return WorkflowStageStatus.BLOCKED
        if all(stage.status == WorkflowStageStatus.COMPLETED for stage in stages):
            return WorkflowStageStatus.COMPLETED
        if any(stage.status in {WorkflowStageStatus.READY, WorkflowStageStatus.IN_PROGRESS} for stage in stages):
            return WorkflowStageStatus.IN_PROGRESS
        return WorkflowStageStatus.NOT_STARTED

    def _next_action(self, stages: List[WorkflowStage]) -> str:
        priority = [
            WorkflowStageStatus.BLOCKED,
            WorkflowStageStatus.READY,
            WorkflowStageStatus.IN_PROGRESS,
            WorkflowStageStatus.NOT_STARTED,
        ]
        for status in priority:
            for stage in stages:
                if stage.status == status and stage.next_action:
                    return stage.next_action
        return "Continue recruitment workflow."
