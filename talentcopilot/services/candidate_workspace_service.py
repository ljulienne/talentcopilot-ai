from talentcopilot.models.candidate_workspace import (
    CandidateEvidence,
    CandidateRisk,
    CandidateSkill,
    CandidateWorkspaceReport,
)


class CandidateWorkspaceService:
    def build_all(self, session=None):
        if session is None or not getattr(session, "ranked_analyses", None):
            return []

        reports = []
        candidates_by_name = {}
        for candidate in getattr(session, "candidates", []) or []:
            name = candidate.get("name")
            if name:
                candidates_by_name[name] = candidate

        for analysis in session.ranked_analyses:
            candidate = candidates_by_name.get(analysis.candidate_name, {})
            reports.append(self._build_one(analysis, candidate))
        return reports

    def _build_one(self, analysis, candidate):
        decision_report = getattr(analysis, "decision_report", None)

        recommendation = "-"
        executive_summary = "No decision summary available yet."
        risks = []

        if decision_report:
            recommendation = getattr(
                decision_report.recommendation,
                "value",
                decision_report.recommendation,
            )
            executive_summary = getattr(decision_report, "executive_summary", executive_summary)

            for concern in getattr(decision_report, "concerns", []) or []:
                risks.append(
                    CandidateRisk(
                        title=getattr(concern, "title", "Concern"),
                        detail=getattr(concern, "explanation", ""),
                        severity=getattr(concern, "severity", "Medium"),
                    )
                )

        skills = []
        for skill in candidate.get("skills", [])[:8]:
            level = 85 if str(skill).lower() in executive_summary.lower() else 72
            skills.append(CandidateSkill(name=str(skill), level=level, evidence="Detected from candidate profile."))

        evidence = []
        for achievement in candidate.get("achievements", [])[:6]:
            evidence.append(
                CandidateEvidence(
                    title="Candidate evidence",
                    detail=str(achievement),
                    strength="High",
                )
            )

        if not evidence:
            evidence.append(CandidateEvidence("Evidence not available", "No detailed achievements provided.", "Low"))

        interview_focus = []
        if decision_report and getattr(decision_report, "interview_focus", None):
            interview_focus = list(decision_report.interview_focus)
        elif skills:
            interview_focus = [f"Validate depth of {skills[0].name}.", "Confirm stakeholder management examples."]

        return CandidateWorkspaceReport(
            candidate_name=getattr(analysis, "candidate_name", "Candidate"),
            rank=int(getattr(analysis, "rank", 0) or 0),
            match_score=float(getattr(analysis, "match_score", 0) or 0),
            recommendation=str(recommendation),
            executive_summary=str(executive_summary),
            skills=skills,
            evidence=evidence,
            risks=risks,
            interview_focus=interview_focus,
        )
