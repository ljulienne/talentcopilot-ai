from talentcopilot.models.enterprise_demo_final import (
    DemoReadinessItem,
    DemoWorkspaceStep,
    EnterpriseDemoFinalReport,
)


class EnterpriseDemoFinalService:
    def build(self, session=None) -> EnterpriseDemoFinalReport:
        steps = [
            DemoWorkspaceStep(1, "Product Overview", "What is TalentCopilot?", "Position as an AI Hiring Decision Platform.", 3),
            DemoWorkspaceStep(2, "Recruitment Command Center", "What needs attention today?", "Show AI priorities and next best action.", 3),
            DemoWorkspaceStep(3, "Recruitment Workspace", "Where is the recruitment?", "Show pipeline, tasks and progress.", 4),
            DemoWorkspaceStep(4, "Candidate Workspace", "Who is this candidate?", "Review evidence, skills, risks and summary.", 4),
            DemoWorkspaceStep(5, "Comparison Workspace", "Who is stronger?", "Compare shortlist and decision signals.", 3),
            DemoWorkspaceStep(6, "Interview Workspace", "What must we validate?", "Show questions, scorecard and post-interview evaluation.", 5),
            DemoWorkspaceStep(7, "Hiring Budget", "Can we afford this hire?", "Show budget fit separate from candidate fit.", 3),
            DemoWorkspaceStep(8, "Decision Board", "Are we ready to decide?", "Show collaborative decision signals.", 3),
            DemoWorkspaceStep(9, "Analytics Dashboard", "Is recruitment healthy?", "Show readiness, funnel and analytics signals.", 3),
            DemoWorkspaceStep(10, "Executive Reporting", "How do we justify the decision?", "Export stakeholder-ready summary.", 3),
        ]

        readiness_items = self._readiness_items(session)
        ok = len([item for item in readiness_items if item.status == "OK"])
        score = int((ok / max(1, len(readiness_items))) * 100)

        return EnterpriseDemoFinalReport(
            title="TalentCopilot Enterprise Demo — Release 1.1",
            positioning="An AI Hiring Decision Platform for explainable, collaborative and evidence-based recruitment decisions.",
            total_duration_minutes=sum(step.expected_duration_minutes for step in steps),
            readiness_score=score,
            steps=steps,
            readiness_items=readiness_items,
            closing_message=(
                "TalentCopilot connects recruitment operations, candidate analysis, interview preparation, "
                "budget feasibility, decision governance and executive reporting into one coherent workflow."
            ),
        )

    def _readiness_items(self, session=None):
        items = [
            DemoReadinessItem("Enterprise navigation", "OK", "All key workspaces are visible."),
            DemoReadinessItem("Design system", "OK", "Enterprise UI foundation is active."),
            DemoReadinessItem("Stable tests", "OK", "Stable test suite is available."),
        ]

        if session is None:
            items.extend([
                DemoReadinessItem("Demo session", "WARN", "Load Enterprise Demo before presentation."),
                DemoReadinessItem("Candidate ranking", "WARN", "No active ranked analyses yet."),
            ])
            return items

        ranked = getattr(session, "ranked_analyses", []) or []
        items.append(DemoReadinessItem("Demo session", "OK", getattr(session, "role_title", "Recruitment")))
        items.append(DemoReadinessItem("Candidate ranking", "OK" if ranked else "WARN", f"{len(ranked)} ranked candidate(s)."))
        return items
