from talentcopilot.recruitment_source_of_truth import RecruitmentSourceOfTruthService
from talentcopilot.models.candidate_workspace import (
    CandidateEvidence,
    CandidateRisk,
    CandidateSkill,
    CandidateWorkspaceReport,
)
from talentcopilot.services.candidate_identity import resolve_candidate_id


class CandidateWorkspaceService:
    def build_all(self, session=None):
        if session is None or not getattr(session, "ranked_analyses", None):
            return []

        candidates_by_id = {}
        candidates_by_name = {}
        for candidate in getattr(session, "candidates", []) or []:
            candidate_id = resolve_candidate_id(candidate)
            candidates_by_id[candidate_id] = candidate
            name = candidate.get("name")
            if name:
                candidates_by_name.setdefault(name, candidate)

        reports = []
        for analysis in RecruitmentSourceOfTruthService().ordered_analyses(session):
            candidate = candidates_by_id.get(getattr(analysis, "candidate_id", ""))
            if candidate is None:
                candidate = candidates_by_name.get(analysis.candidate_name, {})
            reports.append(self._build_one(analysis, candidate))
        return reports

    def _build_one(self, analysis, candidate):
        decision_report = getattr(analysis, "decision_report", None)
        recommendation = "-"
        executive_summary = "No decision summary available yet."
        risks = []

        if decision_report:
            recommendation = getattr(decision_report.recommendation, "value", decision_report.recommendation)
            executive_summary = getattr(decision_report, "executive_summary", executive_summary)
            for concern in getattr(decision_report, "concerns", []) or []:
                risks.append(CandidateRisk(
                    title=getattr(concern, "title", "Concern"),
                    detail=getattr(concern, "explanation", ""),
                    severity=getattr(concern, "severity", "Medium"),
                ))

        skills = [
            CandidateSkill(name=str(skill), level=72, evidence="Detected from candidate profile.")
            for skill in candidate.get("skills", [])[:8]
        ]
        evidence = [
            CandidateEvidence(title="Candidate evidence", detail=str(achievement), strength="High")
            for achievement in candidate.get("achievements", [])[:6]
        ]
        if not evidence:
            evidence.append(CandidateEvidence("Evidence not available", "No detailed achievements provided.", "Low"))

        interview_focus = []
        if decision_report and getattr(decision_report, "interview_focus", None):
            interview_focus = list(decision_report.interview_focus)
        elif skills:
            interview_focus = [f"Validate depth of {skills[0].name}.", "Confirm stakeholder management examples."]

        return CandidateWorkspaceReport(
            candidate_name=getattr(analysis, "candidate_name", "Candidate"),
            candidate_id=getattr(analysis, "candidate_id", "") or resolve_candidate_id(candidate),
            # Candidate Intelligence displays the canonical Mission Fit score.
            # Its "Official Rank" must therefore use the corresponding
            # Mission Fit rank, not the separate Decision Priority rank.
            rank=int(
                (getattr(analysis, "score_breakdown", {}) or {}).get(
                    "mission_fit_rank"
                )
                or getattr(analysis, "rank", None)
                or getattr(analysis, "official_rank", 0)
                or 0
            ),
            match_score=float(getattr(analysis, "official_match_score", getattr(analysis, "match_score", 0.0))),
            score_breakdown=dict(getattr(analysis, "score_breakdown", {}) or {}),
            recommendation=str(recommendation),
            executive_summary=str(executive_summary),
            skills=skills,
            evidence=evidence,
            risks=risks,
            interview_focus=interview_focus,
        )
