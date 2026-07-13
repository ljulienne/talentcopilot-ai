from talentcopilot.services.official_score_service import get_official_candidate_score

from talentcopilot.models.recruitment_workspace import (
    PipelineStage,
    RecruitmentWorkspaceReport,
    TimelineEvent,
    WorkspaceCandidate,
)


class RecruitmentWorkspaceService:
    def build(self, session=None) -> RecruitmentWorkspaceReport:
        if session is None:
            return self._empty_report()

        candidates = []
        for analysis in getattr(session, "ranked_analyses", []):
            recommendation = "-"
            if getattr(analysis, "decision_report", None):
                recommendation = getattr(
                    analysis.decision_report.recommendation,
                    "value",
                    analysis.decision_report.recommendation,
                )

            if getattr(analysis, "rank", 0) == 1:
                stage = "Shortlisted"
            elif get_official_candidate_score(analysis) >= 70:
                stage = "Screening"
            else:
                stage = "Review"

            candidates.append(
                WorkspaceCandidate(
                    rank=getattr(analysis, "rank", 0),
                    name=getattr(analysis, "candidate_name", "Candidate"),
                    stage=stage,
                    match_score=get_official_candidate_score(analysis),
                    recommendation=str(recommendation),
                )
            )

        shortlisted = len([c for c in candidates if c.stage == "Shortlisted"])
        screening = len([c for c in candidates if c.stage == "Screening"])
        review = len([c for c in candidates if c.stage == "Review"])

        return RecruitmentWorkspaceReport(
            role_title=getattr(session, "role_title", "Recruitment"),
            session_id=getattr(session, "session_id", "session"),
            status="Screening",
            candidates_count=getattr(session, "candidate_count", len(candidates)),
            analyzed_count=getattr(session, "analyzed_count", len(candidates)),
            pipeline=[
                PipelineStage("Imported", getattr(session, "candidate_count", len(candidates)), "done"),
                PipelineStage("Analyzed", getattr(session, "analyzed_count", len(candidates)), "done"),
                PipelineStage("Shortlisted", shortlisted, "active"),
                PipelineStage("Screening", screening, "active"),
                PipelineStage("Review", review, "pending"),
            ],
            candidates=candidates,
            timeline=[
                TimelineEvent("Job defined", "done", "Role requirements are available."),
                TimelineEvent("Candidates imported", "done", "Candidate list is loaded."),
                TimelineEvent("AI analysis completed", "done", "Ranking and recommendations are available."),
                TimelineEvent("Hiring manager review", "active", "Operational fit must be validated."),
                TimelineEvent("Decision board", "pending", "Final decision has not been completed."),
            ],
            next_actions=[
                "Review the top-ranked candidate evidence.",
                "Prepare Hiring Manager interview questions.",
                "Open Decision Center to validate recommendation.",
            ],
        )

    def _empty_report(self) -> RecruitmentWorkspaceReport:
        return RecruitmentWorkspaceReport(
            role_title="No active recruitment",
            session_id="-",
            status="Not started",
            candidates_count=0,
            analyzed_count=0,
            pipeline=[
                PipelineStage("Imported", 0, "pending"),
                PipelineStage("Analyzed", 0, "pending"),
                PipelineStage("Shortlisted", 0, "pending"),
            ],
            candidates=[],
            timeline=[
                TimelineEvent("Load demo or create recruitment", "pending", "No recruitment is active yet.")
            ],
            next_actions=["Load Enterprise Demo from this page or from the Command Center."],
        )
