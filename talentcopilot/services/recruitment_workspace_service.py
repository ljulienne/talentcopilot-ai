from talentcopilot.recruitment_source_of_truth import RecruitmentSourceOfTruthService
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
        source = RecruitmentSourceOfTruthService().get(session)
        analyses_by_id = {
            str(getattr(item, "candidate_id", "")): item
            for item in getattr(session, "analyses", [])
        }
        for record in sorted(source.candidates, key=lambda item: item.interview_priority):
            analysis = analyses_by_id.get(record.candidate_id)
            recommendation = "-"
            if analysis is not None and getattr(analysis, "decision_report", None):
                recommendation = getattr(
                    analysis.decision_report.recommendation,
                    "value",
                    analysis.decision_report.recommendation,
                )
            elif analysis is not None:
                notes = [str(item) for item in (getattr(analysis, "notes", []) or [])]
                recommendation = next(
                    (item.split(":", 1)[1].strip() for item in notes if item.startswith("Recommendation:")),
                    "Review",
                )

            if record.interview_priority == 1:
                stage = "Priority interview"
            elif record.interview_priority <= 3:
                stage = "Shortlist"
            else:
                stage = "Review"

            candidates.append(
                WorkspaceCandidate(
                    rank=record.interview_priority,
                    name=record.candidate_name,
                    stage=stage,
                    match_score=record.mission_fit_score,
                    recommendation=str(recommendation),
                    mission_rank=record.mission_rank,
                    interview_priority=record.interview_priority,
                    career_fit_score=record.career_fit_score,
                    confidence=record.confidence,
                )
            )

        shortlisted = len([c for c in candidates if c.stage in {"Priority interview", "Shortlist"}])
        screening = len([c for c in candidates if c.stage == "Shortlist"])
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
