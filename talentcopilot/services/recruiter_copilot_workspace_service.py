from talentcopilot.services.official_score_service import get_official_candidate_score

from talentcopilot.models.recruiter_copilot_workspace import (
    CandidateCopilotSummary,
    CopilotAction,
    CopilotAlert,
    CopilotQuestion,
    RecruiterCopilotWorkspaceReport,
)


class RecruiterCopilotWorkspaceService:
    def build(self, session=None) -> RecruiterCopilotWorkspaceReport:
        if session is None or not getattr(session, "ranked_analyses", None):
            return self._empty_report()

        candidates = []

        for analysis in session.ranked_analyses:
            copilot = getattr(analysis, "recruiter_copilot_report", None)

            headline = "Candidate ready for recruiter review"
            recruiter_summary = "Review candidate evidence and prepare next steps."
            actions = []
            questions = []
            alerts = []
            stakeholder_summary = ""

            if copilot:
                headline = getattr(copilot, "headline", headline)
                recruiter_summary = getattr(copilot, "recruiter_summary", recruiter_summary)
                stakeholder_summary = getattr(copilot, "stakeholder_summary", "")

                for action in getattr(copilot, "actions", []) or []:
                    actions.append(
                        CopilotAction(
                            title=getattr(action, "title", "Recruiter action"),
                            rationale=getattr(action, "rationale", ""),
                            priority=getattr(action, "priority", "Medium"),
                            owner=getattr(action, "owner", "Recruiter"),
                        )
                    )

                for question in getattr(copilot, "interview_questions", []) or []:
                    questions.append(
                        CopilotQuestion(
                            question=getattr(question, "question", str(question)),
                            purpose=getattr(question, "purpose", "Validate candidate fit."),
                            expected_signal=getattr(question, "expected_signal", ""),
                        )
                    )

                for alert in getattr(copilot, "alerts", []) or []:
                    alerts.append(
                        CopilotAlert(
                            title=getattr(alert, "title", "Alert"),
                            detail=getattr(alert, "detail", ""),
                            severity=getattr(alert, "severity", "Medium"),
                        )
                    )

            if not actions:
                actions = [
                    CopilotAction("Review evidence", "Validate the evidence behind the AI recommendation.", "High"),
                    CopilotAction("Prepare interview", "Use targeted questions to validate critical competencies.", "High"),
                ]

            if not questions:
                questions = [
                    CopilotQuestion(
                        "Describe a project where you had to align several stakeholders with conflicting expectations.",
                        "Validate stakeholder management and communication.",
                        "Structured example with clear role, actions and measurable outcome.",
                    ),
                    CopilotQuestion(
                        "What would be your first 30 days plan in this role?",
                        "Assess operational readiness and prioritization.",
                        "Clear onboarding plan, risk awareness and stakeholder mapping.",
                    ),
                ]

            if not alerts and get_official_candidate_score(analysis) < 75:
                alerts.append(
                    CopilotAlert(
                        "Moderate match score",
                        "Candidate may require deeper validation before moving forward.",
                        "Medium",
                    )
                )

            if not stakeholder_summary:
                stakeholder_summary = (
                    f"{getattr(analysis, 'candidate_name', 'Candidate')} should be reviewed with focus on evidence, "
                    "operational readiness and hiring manager validation."
                )

            candidates.append(
                CandidateCopilotSummary(
                    candidate_name=getattr(analysis, "candidate_name", "Candidate"),
                    rank=int(getattr(analysis, "rank", 0) or 0),
                    match_score=get_official_candidate_score(analysis),
                    headline=str(headline),
                    recruiter_summary=str(recruiter_summary),
                    actions=actions,
                    questions=questions,
                    alerts=alerts,
                    stakeholder_summary=str(stakeholder_summary),
                )
            )

        return RecruiterCopilotWorkspaceReport(
            role_title=getattr(session, "role_title", "Recruitment"),
            session_id=getattr(session, "session_id", "session"),
            candidates=candidates,
            global_actions=[
                CopilotAction("Review top candidate", "Start with the highest ranked candidate and validate evidence.", "High"),
                CopilotAction("Prepare hiring manager review", "Share interview focus before manager interview.", "High"),
                CopilotAction("Update decision board", "Keep stakeholder decisions aligned.", "Medium"),
            ],
        )

    def _empty_report(self) -> RecruiterCopilotWorkspaceReport:
        return RecruiterCopilotWorkspaceReport(
            role_title="No active recruitment",
            session_id="-",
            candidates=[],
            global_actions=[
                CopilotAction("Load Enterprise Demo", "Start a demo recruitment to activate the Copilot.", "High")
            ],
        )
