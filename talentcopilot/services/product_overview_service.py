from talentcopilot.models.product_overview import ProductOverview, ProductPersona, ProductWorkspace


class ProductOverviewService:
    def build(self) -> ProductOverview:
        return ProductOverview(
            tagline="Better Hiring Decisions. Explained.",
            value_proposition=(
                "TalentCopilot Enterprise helps hiring teams transform candidate data into "
                "clear, explainable and evidence-based recruitment decisions."
            ),
            principles=[
                "AI assists. Humans decide.",
                "Every recommendation must be explainable.",
                "Every workspace answers one business question.",
                "Evidence matters more than opaque scoring.",
                "Recruitment is collaborative.",
            ],
            workspaces=[
                ProductWorkspace("Recruitment Command Center", "What needs attention today?", "Daily priorities and AI-guided next actions."),
                ProductWorkspace("Recruitment Workspace", "Where is this recruitment?", "Pipeline, candidates and timeline."),
                ProductWorkspace("Candidate Workspace", "Who is this candidate?", "Evidence, skills, risks and interview focus."),
                ProductWorkspace("Comparison Workspace", "Who is stronger?", "Ranking, gaps and decision matrix."),
                ProductWorkspace("Decision Board", "Are we ready to decide?", "AI, recruiter, manager and HR decision signals."),
                ProductWorkspace("Recruiter Copilot", "What should I do next?", "Actions, interview questions and stakeholder summary."),
                ProductWorkspace("Executive Reporting", "How do we share the decision?", "Stakeholder-ready report and export."),
            ],
            personas=[
                ProductPersona("Recruiter", "Move faster while staying evidence-based.", "Command Center / Recruiter Copilot"),
                ProductPersona("Hiring Manager", "Understand operational fit and interview focus.", "Candidate Workspace / Decision Board"),
                ProductPersona("HR Director", "Validate defensible decisions.", "Decision Board / Executive Reporting"),
                ProductPersona("HRIS Administrator", "Ensure app health and readiness.", "Release Readiness / Session Health"),
            ],
            demo_flow=[
                "Load Enterprise Demo.",
                "Open Recruitment Command Center.",
                "Review Recruitment Workspace.",
                "Open Candidate Workspace.",
                "Compare shortlist.",
                "Validate Decision Board.",
                "Export Executive Report.",
            ],
        )
