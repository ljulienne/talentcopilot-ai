from talentcopilot.models.recruitment_tasks import RecruitmentTask, RecruitmentTaskReport


class RecruitmentTasksService:
    def build(self, session=None) -> RecruitmentTaskReport:
        if session is None:
            return RecruitmentTaskReport(
                role_title="No active recruitment",
                session_id="-",
                total_tasks=1,
                open_tasks=1,
                blockers=["No active recruitment session."],
                tasks=[
                    RecruitmentTask(
                        "Load Enterprise Demo",
                        "Recruiter",
                        "High",
                        "Open",
                        "Load a demo session to populate recruitment tasks.",
                    )
                ],
            )

        ranked = getattr(session, "ranked_analyses", []) or []
        role_title = getattr(session, "role_title", "Recruitment")
        session_id = getattr(session, "session_id", "session")

        tasks = [
            RecruitmentTask(
                "Review AI shortlist",
                "Recruiter",
                "High",
                "Open",
                "Validate the ranking and evidence before contacting stakeholders.",
            ),
            RecruitmentTask(
                "Prepare hiring manager interview",
                "Recruiter",
                "High",
                "Open",
                "Generate or review targeted interview questions for the top candidate.",
            ),
            RecruitmentTask(
                "Confirm decision criteria",
                "Hiring Manager",
                "Medium",
                "Open",
                "Validate what matters most operationally before final comparison.",
            ),
            RecruitmentTask(
                "Prepare executive summary",
                "HR Director",
                "Medium",
                "Pending",
                "Generate a stakeholder-ready summary after decision board validation.",
            ),
        ]

        blockers = []
        if not ranked:
            blockers.append("No ranked analyses available.")
        else:
            top = ranked[0]
            if float(getattr(top, "match_score", 0) or 0) < 75:
                blockers.append("Top candidate score is below recommended threshold.")

        open_tasks = len([task for task in tasks if task.status.lower() == "open"])

        return RecruitmentTaskReport(
            role_title=role_title,
            session_id=session_id,
            total_tasks=len(tasks),
            open_tasks=open_tasks,
            blockers=blockers,
            tasks=tasks,
        )
