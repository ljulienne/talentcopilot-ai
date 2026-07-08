from talentcopilot.models.release_1_1_summary import BlueprintReadinessItem, Release11Summary, ReleaseModule


class Release11SummaryService:
    def build(self) -> Release11Summary:
        modules = [
            ReleaseModule("Recruitment Pipeline", "Delivered", "Operational recruitment stages and readiness."),
            ReleaseModule("Recruitment Tasks", "Delivered", "Task ownership, priorities and blockers."),
            ReleaseModule("Interview Workspace", "Delivered", "Structured preparation, questions and live notes."),
            ReleaseModule("Interview Evaluation", "Delivered", "Post-interview scorecards and decision impact."),
            ReleaseModule("Hiring Budget", "Delivered", "Budget fit separated from candidate fit."),
            ReleaseModule("Analytics Dashboard", "Delivered", "Recruitment health, funnel and readiness KPIs."),
            ReleaseModule("Enterprise Demo Final", "Delivered", "20–30 minute demo script and checklist."),
            ReleaseModule("UI Polish", "Delivered", "Final navigation and release summary."),
        ]

        readiness = [
            BlueprintReadinessItem("UI Workspaces", "Ready", "Core Enterprise workflow is complete for demo."),
            BlueprintReadinessItem("Stable Tests", "Ready", "Stable test suite protects core imports and services."),
            BlueprintReadinessItem("Decision Core", "Pending", "Blueprint must define CandidateDecisionProfile and engine contracts."),
            BlueprintReadinessItem("Real Data", "Pending", "Real parsing and analysis will come after Decision Core."),
            BlueprintReadinessItem("Market Intelligence", "Planned", "To be implemented after Blueprint."),
            BlueprintReadinessItem("Talent Locator", "Planned", "To be implemented after Blueprint."),
        ]

        return Release11Summary(
            title="TalentCopilot Enterprise — Release 1.1 Complete",
            version="v1.1.0-alpha-h",
            product_message=(
                "Release 1.1 completes the Enterprise demo workflow from recruitment pipeline "
                "to interview, budget, analytics, decision and executive reporting."
            ),
            modules=modules,
            blueprint_readiness=readiness,
            next_steps=[
                "Run full Streamlit demo from Enterprise Demo Final.",
                "Fix any visual or runtime issue found during testing.",
                "Freeze UI changes except bug fixes.",
                "Create TalentCopilot Enterprise Blueprint.",
                "Design Decision Intelligence Core v2.",
            ],
        )
