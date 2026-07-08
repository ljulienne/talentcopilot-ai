from talentcopilot.models.recruitment_pipeline import (
    RecruitmentPipelineAction,
    RecruitmentPipelineReport,
    RecruitmentPipelineStage,
)


class RecruitmentPipelineService:
    def build(self, session=None) -> RecruitmentPipelineReport:
        if session is None:
            return self._empty_report()

        candidate_count = int(getattr(session, "candidate_count", 0) or 0)
        analyzed_count = int(getattr(session, "analyzed_count", 0) or 0)
        ranked = getattr(session, "ranked_analyses", []) or []

        top_score = 0
        if ranked:
            top_score = float(getattr(ranked[0], "match_score", 0) or 0)

        shortlisted_count = len([item for item in ranked if float(getattr(item, "match_score", 0) or 0) >= 80])
        review_count = max(0, analyzed_count - shortlisted_count)

        stages = [
            RecruitmentPipelineStage(
                "Job Definition",
                "Done",
                1,
                100,
                RecruitmentPipelineAction("Validate role criteria", "Recruiter", "Low", "Role requirements are already available."),
            ),
            RecruitmentPipelineStage(
                "Candidate Import",
                "Done" if candidate_count else "Pending",
                candidate_count,
                100 if candidate_count else 0,
                RecruitmentPipelineAction("Import candidates", "Recruiter", "High", "Candidates are required before AI analysis."),
            ),
            RecruitmentPipelineStage(
                "AI Screening",
                "Done" if analyzed_count else "Pending",
                analyzed_count,
                95 if analyzed_count else 0,
                RecruitmentPipelineAction("Review AI ranking", "Recruiter", "High", "Ranking must be reviewed before decision."),
            ),
            RecruitmentPipelineStage(
                "Shortlist",
                "Active" if shortlisted_count else "Pending",
                shortlisted_count,
                85 if shortlisted_count else 35,
                RecruitmentPipelineAction("Confirm shortlist", "Recruiter", "High", "Shortlisted candidates should be validated with evidence."),
            ),
            RecruitmentPipelineStage(
                "Hiring Manager Review",
                "Active" if top_score >= 75 else "Pending",
                review_count,
                70 if top_score >= 75 else 30,
                RecruitmentPipelineAction("Schedule manager review", "Hiring Manager", "High", "Operational fit needs human validation."),
            ),
            RecruitmentPipelineStage(
                "Decision",
                "Pending",
                0,
                45,
                RecruitmentPipelineAction("Open Decision Board", "Recruiter", "Medium", "Decision is not final until stakeholder signals are aligned."),
            ),
        ]

        readiness = int(sum(stage.readiness for stage in stages) / max(1, len(stages)))
        blockers = []
        if not candidate_count:
            blockers.append("No candidates imported.")
        if not analyzed_count:
            blockers.append("No AI analysis available.")
        if not shortlisted_count and analyzed_count:
            blockers.append("No candidate currently above shortlist threshold.")

        return RecruitmentPipelineReport(
            role_title=getattr(session, "role_title", "Recruitment"),
            session_id=getattr(session, "session_id", "session"),
            overall_readiness=readiness,
            stages=stages,
            blockers=blockers,
            next_actions=[
                stage.action for stage in stages
                if stage.status in {"Active", "Pending"}
            ][:4],
        )

    def _empty_report(self) -> RecruitmentPipelineReport:
        return RecruitmentPipelineReport(
            role_title="No active recruitment",
            session_id="-",
            overall_readiness=0,
            stages=[
                RecruitmentPipelineStage(
                    "Load Demo",
                    "Pending",
                    0,
                    0,
                    RecruitmentPipelineAction("Load Enterprise Demo", "Recruiter", "High", "A session is required to populate the pipeline."),
                )
            ],
            blockers=["No active recruitment session."],
            next_actions=[
                RecruitmentPipelineAction("Load Enterprise Demo", "Recruiter", "High", "Start a demo scenario to validate the workflow.")
            ],
        )
