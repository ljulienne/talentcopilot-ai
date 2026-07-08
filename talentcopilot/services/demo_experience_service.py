from talentcopilot.models.demo_experience import DemoCheck, DemoExperienceReport, DemoStep


class DemoExperienceService:
    def build(self, session=None) -> DemoExperienceReport:
        checks = self._checks(session)
        passed = len([check for check in checks if check.status == "OK"])
        readiness = int((passed / max(1, len(checks))) * 100)

        return DemoExperienceReport(
            scenario_name="Transformation Lead Enterprise Demo",
            role_title=getattr(session, "role_title", "No active recruitment") if session else "No active recruitment",
            session_id=getattr(session, "session_id", "-") if session else "-",
            readiness_score=readiness,
            checks=checks,
            steps=[
                DemoStep(1, "Recruitment Command Center", "Show daily priorities", "The recruiter sees what to do first."),
                DemoStep(2, "Recruitment Workspace", "Show recruitment status", "The hiring workflow is easy to understand."),
                DemoStep(3, "Candidate Workspace", "Review top candidate", "Evidence, skills and risks are visible."),
                DemoStep(4, "Comparison Workspace", "Compare shortlist", "Differences are clear."),
                DemoStep(5, "Decision Board", "Show collaborative decision", "AI, recruiter and manager signals are aligned."),
                DemoStep(6, "Executive Reporting", "Prepare stakeholder output", "A report can be exported."),
            ],
            presenter_notes=[
                "Start by loading the demo from this page or from the Command Center.",
                "Use the same top candidate across Candidate Workspace, Comparison and Decision Board.",
                "Emphasize that AI assists and humans decide.",
                "Finish with Executive Reporting to show business value.",
            ],
        )

    def _checks(self, session):
        checks = []
        if session is None:
            return [
                DemoCheck("Active session", "FAIL", "No demo session loaded."),
                DemoCheck("Candidates", "FAIL", "No candidates available."),
                DemoCheck("Ranked analyses", "FAIL", "No AI ranking available."),
                DemoCheck("Decision data", "FAIL", "No decision data available."),
            ]

        candidate_count = getattr(session, "candidate_count", 0)
        ranked = getattr(session, "ranked_analyses", []) or []

        checks.append(DemoCheck("Active session", "OK", getattr(session, "role_title", "Recruitment")))
        checks.append(DemoCheck("Candidates", "OK" if candidate_count > 0 else "FAIL", f"{candidate_count} candidate(s)"))
        checks.append(DemoCheck("Ranked analyses", "OK" if ranked else "FAIL", f"{len(ranked)} ranked profile(s)"))

        has_decision = any(getattr(item, "decision_report", None) for item in ranked)
        checks.append(DemoCheck("Decision data", "OK" if has_decision else "FAIL", "Decision reports available" if has_decision else "Missing decision reports"))

        return checks
