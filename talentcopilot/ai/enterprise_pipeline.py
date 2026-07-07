from typing import Any, Dict, Iterable, List, Optional
from uuid import uuid4

from talentcopilot.models.recruitment_session import (
    CandidateAnalysisState,
    CandidateAnalysisStatus,
    RecruitmentSession,
    SessionStatus,
)


class EnterprisePipeline:
    """
    Central orchestration pipeline for TalentCopilot v0.7.

    The pipeline is dependency-tolerant:
    - if optional engines exist, it uses them;
    - if they are unavailable, it produces a safe deterministic session state.

    This avoids breaking Streamlit while the product moves toward deeper integration.
    """

    def create_session(self, job: Dict[str, Any], candidates: Iterable[Dict[str, Any]], session_id: Optional[str] = None) -> RecruitmentSession:
        session = RecruitmentSession(
            session_id=session_id or f"session-{uuid4().hex[:10]}",
            job=job or {"title": "Role"},
            candidates=list(candidates or []),
            status=SessionStatus.READY,
        )
        return session

    def analyze_session(self, session: RecruitmentSession) -> RecruitmentSession:
        session.status = SessionStatus.ANALYZING
        session.analyses = []

        analyses = []
        for candidate in session.candidates:
            analyses.append(self._analyze_candidate(session.job, candidate))

        analyses = sorted(analyses, key=lambda item: item.match_score, reverse=True)
        for index, analysis in enumerate(analyses, start=1):
            analysis.rank = index
            session.add_analysis(analysis)

        session.status = SessionStatus.COMPLETED
        session.mark_updated()
        return session

    def run(self, job: Dict[str, Any], candidates: Iterable[Dict[str, Any]]) -> RecruitmentSession:
        session = self.create_session(job, candidates)
        return self.analyze_session(session)

    def _analyze_candidate(self, job: Dict[str, Any], candidate: Dict[str, Any]) -> CandidateAnalysisState:
        candidate_name = str(candidate.get("name", "Candidate"))

        try:
            match_score = self._basic_match_score(job, candidate)
            governance_report = self._try_governance(job, candidate, match_score)
            decision_report = self._try_decision(job, candidate, match_score, governance_report)
            copilot_report = self._try_copilot(job, candidate, decision_report)

            return CandidateAnalysisState(
                candidate_name=candidate_name,
                status=CandidateAnalysisStatus.ANALYZED,
                match_score=match_score,
                governance_report=governance_report,
                decision_report=decision_report,
                recruiter_copilot_report=copilot_report,
                notes=["Enterprise pipeline analysis completed."],
            )

        except Exception as exc:
            return CandidateAnalysisState(
                candidate_name=candidate_name,
                status=CandidateAnalysisStatus.ERROR,
                errors=[str(exc)],
            )

    def _basic_match_score(self, job: Dict[str, Any], candidate: Dict[str, Any]) -> float:
        required = self._as_list(job.get("required_skills") or job.get("skills") or job.get("competencies"))
        candidate_skills = self._as_list(candidate.get("skills"))
        text = " ".join(str(value) for value in self._flatten_candidate(candidate)).lower()

        if not required:
            return 60.0

        matched = 0
        for skill in required:
            skill_text = str(skill).lower()
            if skill_text in [str(s).lower() for s in candidate_skills] or skill_text in text:
                matched += 1

        return round((matched / len(required)) * 100, 2)

    def _try_governance(self, job, candidate, match_score):
        try:
            from talentcopilot.ai.governance_engine import GovernanceEngine
            return GovernanceEngine().assess_candidate(candidate, job, match_score=match_score)
        except Exception:
            return None

    def _try_decision(self, job, candidate, match_score, governance_report):
        try:
            from talentcopilot.ai.decision_engine import DecisionEngine
            return DecisionEngine().make_decision(
                candidate=candidate,
                job=job,
                match_score=match_score,
                governance_report=governance_report,
            )
        except Exception:
            return None

    def _try_copilot(self, job, candidate, decision_report):
        if decision_report is None:
            return None
        try:
            from talentcopilot.ai.recruiter_copilot_engine import RecruiterCopilotEngine
            return RecruiterCopilotEngine().advise(candidate, job, decision_report)
        except Exception:
            return None

    def _as_list(self, value: Any) -> List[Any]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        if isinstance(value, set):
            return list(value)
        return [value]

    def _flatten_candidate(self, candidate: Dict[str, Any]) -> List[Any]:
        values = []
        for value in candidate.values():
            if isinstance(value, list):
                values.extend(value)
            elif isinstance(value, dict):
                values.extend(value.values())
            else:
                values.append(value)
        return values
