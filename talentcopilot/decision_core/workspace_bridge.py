from talentcopilot.decision_core.orchestrator import DecisionCoreOrchestrator
from talentcopilot.decision_core.orchestrator_models import DecisionCoreInput
from talentcopilot.decision_core.workspace_bridge_models import WorkspaceBridgeReport


class DecisionCoreWorkspaceBridge:
    def build_from_session(self, session=None) -> WorkspaceBridgeReport:
        if session is None:
            return WorkspaceBridgeReport(
                role_title="No active recruitment",
                total_candidates=0,
                profiles_created=0,
                outputs=[],
                status="No session",
            )

        role_title = getattr(session, "role_title", "Recruitment")
        candidates = getattr(session, "candidates", []) or []
        job = getattr(session, "job", {}) or {}

        required_skills = job.get("required_skills", []) if isinstance(job, dict) else []
        preferred_skills = job.get("preferred_skills", []) if isinstance(job, dict) else []
        minimum_years = int(job.get("minimum_years_experience", 0) or job.get("years_experience", 0) or 0) if isinstance(job, dict) else 0

        inputs = []
        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            inputs.append(
                DecisionCoreInput(
                    candidate=candidate,
                    role_title=role_title,
                    required_skills=required_skills,
                    preferred_skills=preferred_skills,
                    minimum_years_experience=minimum_years,
                )
            )

        outputs = DecisionCoreOrchestrator().analyze_many(inputs) if inputs else []

        return WorkspaceBridgeReport(
            role_title=role_title,
            total_candidates=len(candidates),
            profiles_created=len(outputs),
            outputs=outputs,
            status="Ready" if outputs else "No candidates",
        )

    def build_demo(self) -> WorkspaceBridgeReport:
        candidates = [
            {
                "name": "Alice Martin",
                "skills": ["Project Management", "Stakeholder Management", "HRIS"],
                "years_experience": 8,
                "achievements": ["Improved adoption by 35%"],
            },
            {
                "name": "David Smith",
                "skills": ["Graphic Design"],
                "years_experience": 1,
            },
        ]

        class DemoSession:
            pass

        demo_session = DemoSession()
        demo_session.role_title = "Transformation Lead"
        demo_session.job = {
            "required_skills": ["Project Management", "Stakeholder Management"],
            "preferred_skills": ["HRIS"],
            "minimum_years_experience": 6,
        }
        demo_session.candidates = candidates

        return self.build_from_session(demo_session)
