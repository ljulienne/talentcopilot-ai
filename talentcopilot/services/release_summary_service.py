from talentcopilot.models.release_summary import ReleaseSummary, ReleaseWorkspaceStatus


class ReleaseSummaryService:
    def build(self) -> ReleaseSummary:
        return ReleaseSummary(
            release_name="TalentCopilot Enterprise Release 1.0",
            version="v1.0.0-alpha-p",
            summary=(
                "Release 1.0 transformed TalentCopilot from a collection of Streamlit pages "
                "into a more coherent Enterprise workspace-based product experience."
            ),
            workspaces=[
                ReleaseWorkspaceStatus("Recruitment Command Center", "Delivered", "Daily cockpit and AI priorities."),
                ReleaseWorkspaceStatus("Recruitment Workspace", "Delivered", "Pilot one recruitment workflow."),
                ReleaseWorkspaceStatus("Candidate Workspace", "Delivered", "Review a candidate with evidence and risks."),
                ReleaseWorkspaceStatus("Talent Intelligence", "Delivered", "Understand talent coverage and sourcing readiness."),
                ReleaseWorkspaceStatus("Comparison Workspace", "Delivered", "Compare candidates through decision signals."),
                ReleaseWorkspaceStatus("Decision Board", "Delivered", "Collaborative decision review."),
                ReleaseWorkspaceStatus("Recruiter Copilot", "Delivered", "Action-oriented recruiter guidance."),
                ReleaseWorkspaceStatus("Executive Reporting", "Delivered", "Stakeholder-ready reporting."),
                ReleaseWorkspaceStatus("Demo Experience", "Delivered", "Reliable demo journey."),
                ReleaseWorkspaceStatus("Release Readiness", "Delivered", "Health and deployment checks."),
            ],
            next_release_focus=[
                "Deepen Recruitment Workspace with richer pipeline actions.",
                "Improve Candidate Workspace with stronger evidence visualization.",
                "Restore and modernize recruitment creation flow.",
                "Start reducing legacy files and v2 module dependencies.",
            ],
        )
