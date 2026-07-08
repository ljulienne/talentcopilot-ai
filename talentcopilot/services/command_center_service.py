from talentcopilot.models.command_center import (
    CommandCenterActivity,
    CommandCenterMetric,
    CommandCenterPriority,
    CommandCenterReport,
    RecruitmentHealth,
)


class CommandCenterService:
    def build(self, session=None) -> CommandCenterReport:
        if session is None:
            return self._empty_report()

        best_candidate = "-"
        if getattr(session, "ranked_analyses", None):
            best_candidate = session.ranked_analyses[0].candidate_name

        return CommandCenterReport(
            role_title=getattr(session, "role_title", "Recruitment"),
            session_id=getattr(session, "session_id", "session"),
            metrics=[
                CommandCenterMetric("Active Recruitments", "1", "Demo"),
                CommandCenterMetric("Candidates", str(getattr(session, "candidate_count", 0)), "Analyzed"),
                CommandCenterMetric("Pending Decisions", "1", "Human review"),
                CommandCenterMetric("Best Match", best_candidate, "AI ranking"),
            ],
            priorities=[
                CommandCenterPriority(
                    "Review top-ranked candidate",
                    f"{best_candidate} is currently the strongest profile. Review evidence before moving forward.",
                    "AI Priority",
                    "High",
                ),
                CommandCenterPriority(
                    "Prepare Hiring Manager interview",
                    "Use recruiter guidance to validate leadership, stakeholder management and operational readiness.",
                    "Next Step",
                    "High",
                ),
                CommandCenterPriority(
                    "Generate executive summary",
                    "A structured report can be generated from the current session.",
                    "Report Ready",
                    "Medium",
                ),
            ],
            activities=[
                CommandCenterActivity("09:41", "Recruitment session loaded", getattr(session, "role_title", "Recruitment")),
                CommandCenterActivity("09:42", "Candidates analyzed", f"{getattr(session, 'analyzed_count', 0)} analysis result(s)"),
                CommandCenterActivity("09:43", "Ranking updated", f"Best match: {best_candidate}"),
                CommandCenterActivity("09:44", "Decision review ready", "Open Decision Center when ready"),
            ],
            health=RecruitmentHealth(
                overall_score=91,
                evidence_coverage=96,
                interview_readiness=88,
                decision_confidence=94,
                bias_risk="Very Low",
                data_completeness=100,
            ),
            next_action_title=f"Review {best_candidate}",
            next_action_body="Open Candidate Workspace and validate the evidence behind the recommendation.",
        )

    def _empty_report(self) -> CommandCenterReport:
        return CommandCenterReport(
            role_title="No active recruitment",
            session_id="-",
            metrics=[
                CommandCenterMetric("Active Recruitments", "0", "Load demo"),
                CommandCenterMetric("Candidates", "0", "-"),
                CommandCenterMetric("Pending Decisions", "0", "-"),
                CommandCenterMetric("Best Match", "-", "-"),
            ],
            priorities=[
                CommandCenterPriority(
                    "Load Enterprise Demo",
                    "Start a realistic Transformation Lead recruitment scenario.",
                    "Demo Mode",
                    "High",
                )
            ],
            activities=[
                CommandCenterActivity("Now", "No active recruitment", "Load the Enterprise Demo to begin.")
            ],
            health=RecruitmentHealth(
                overall_score=0,
                evidence_coverage=0,
                interview_readiness=0,
                decision_confidence=0,
                bias_risk="-",
                data_completeness=0,
            ),
            next_action_title="Load Enterprise Demo",
            next_action_body="Start with a complete scenario to explore the recruitment decision workflow.",
        )
