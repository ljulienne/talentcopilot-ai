from typing import Any, Dict, Iterable, List, Optional, Tuple
from uuid import uuid4

from talentcopilot.models.recruitment_session import (
    CandidateAnalysisState,
    CandidateAnalysisStatus,
    RecruitmentSession,
    SessionStatus,
)
from talentcopilot.services.candidate_identity import resolve_candidate_id


TRANSFERABLE_SKILL_GROUPS = (
    {"project management", "program management", "project coordination", "delivery management", "pmo"},
    {"stakeholder management", "executive reporting", "business partnering", "client management", "reporting"},
    {"change management", "training", "user adoption", "communications", "organizational change"},
    {"hris", "human resources information systems", "hr systems", "payroll systems", "people systems", "hr analytics", "hr reporting"},
    {"data analysis", "analytics", "business intelligence", "reporting", "excel", "sql"},
)


class EnterprisePipeline:
    """Canonical Release 3 session pipeline and ranking source of truth."""

    def create_session(self, job: Dict[str, Any], candidates: Iterable[Dict[str, Any]], session_id: Optional[str] = None) -> RecruitmentSession:
        normalized_candidates = []
        for source_candidate in candidates or []:
            candidate = dict(source_candidate)
            candidate["candidate_id"] = resolve_candidate_id(candidate)
            normalized_candidates.append(candidate)

        return RecruitmentSession(
            session_id=session_id or f"session-{uuid4().hex[:10]}",
            job=job or {"title": "Role"},
            candidates=normalized_candidates,
            status=SessionStatus.READY,
        )

    def analyze_session(self, session: RecruitmentSession) -> RecruitmentSession:
        session.status = SessionStatus.ANALYZING
        session.analyses = []

        analyses = [self._analyze_candidate(session.job, candidate) for candidate in session.candidates]
        analyses = sorted(
            analyses,
            key=lambda item: (-item.match_score, item.candidate_id or item.candidate_name),
        )
        for index, analysis in enumerate(analyses, start=1):
            analysis.rank = index
            session.add_analysis(analysis)

        session.status = SessionStatus.COMPLETED
        session.mark_updated()
        return session

    def run(self, job: Dict[str, Any], candidates: Iterable[Dict[str, Any]]) -> RecruitmentSession:
        return self.analyze_session(self.create_session(job, candidates))

    def _analyze_candidate(self, job: Dict[str, Any], candidate: Dict[str, Any]) -> CandidateAnalysisState:
        candidate_name = str(candidate.get("name", "Candidate"))
        candidate_id = resolve_candidate_id(candidate)

        try:
            match_score, score_breakdown = self._basic_match_score(job, candidate)
            governance_report = self._try_governance(job, candidate, match_score)
            decision_report = self._try_decision(job, candidate, match_score, governance_report)
            copilot_report = self._try_copilot(job, candidate, decision_report)

            return CandidateAnalysisState(
                candidate_name=candidate_name,
                candidate_id=candidate_id,
                status=CandidateAnalysisStatus.ANALYZED,
                match_score=match_score,
                score_breakdown=score_breakdown,
                governance_report=governance_report,
                decision_report=decision_report,
                recruiter_copilot_report=copilot_report,
                notes=["Enterprise pipeline analysis completed."],
            )
        except Exception as exc:
            return CandidateAnalysisState(
                candidate_name=candidate_name,
                candidate_id=candidate_id,
                status=CandidateAnalysisStatus.ERROR,
                errors=[str(exc)],
            )

    def _basic_match_score(self, job: Dict[str, Any], candidate: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        required = [self._normalize(value) for value in self._as_list(job.get("required_skills") or job.get("skills") or job.get("competencies")) if str(value).strip()]
        candidate_skills = [self._normalize(value) for value in self._as_list(candidate.get("skills")) if str(value).strip()]
        candidate_text = self._normalize(" ".join(str(value) for value in self._flatten_candidate(candidate)))
        job_keywords = [self._normalize(value) for value in self._as_list(job.get("keywords")) if str(value).strip()]

        if not required:
            return 60.0, {
                "required_skills": 0.0,
                "transferable_skills": 0.0,
                "context_relevance": 0.0,
                "experience_readiness": 0.0,
                "default_without_requirements": 60.0,
            }

        exact_hits = sum(1 for requirement in required if requirement in candidate_skills or requirement in candidate_text)
        exact_ratio = exact_hits / len(required)

        transferable_total = 0.0
        for requirement in required:
            if requirement in candidate_skills or requirement in candidate_text:
                continue
            transferable_total += self._transferable_strength(requirement, candidate_skills, candidate_text)
        transferable_ratio = transferable_total / len(required)

        context_terms = [term for term in job_keywords if len(term) >= 3]
        context_hits = sum(1 for term in context_terms if term in candidate_text)
        context_ratio = context_hits / len(context_terms) if context_terms else 0.0

        years = self._safe_float(candidate.get("years_experience"))
        experience_ratio = min(1.0, years / 8.0) if years > 0 else 0.0

        required_component = exact_ratio * 75.0
        transferable_component = transferable_ratio * 15.0
        context_component = context_ratio * 5.0
        experience_component = experience_ratio * 5.0
        overall = round(required_component + transferable_component + context_component + experience_component, 2)

        return overall, {
            "required_skills": round(required_component, 2),
            "transferable_skills": round(transferable_component, 2),
            "context_relevance": round(context_component, 2),
            "experience_readiness": round(experience_component, 2),
        }

    def _transferable_strength(self, requirement: str, candidate_skills: List[str], candidate_text: str) -> float:
        requirement_groups = [group for group in TRANSFERABLE_SKILL_GROUPS if requirement in group]
        if not requirement_groups:
            return 0.0

        best = 0.0
        for group in requirement_groups:
            for skill in candidate_skills:
                if skill in group:
                    best = max(best, 0.45)
            for related in group:
                if related != requirement and related in candidate_text:
                    best = max(best, 0.30)
        return best

    def _try_governance(self, job, candidate, match_score):
        try:
            from talentcopilot.ai.governance_engine import GovernanceEngine
            return GovernanceEngine().assess_candidate(candidate, job, match_score=match_score)
        except Exception:
            return None

    def _try_decision(self, job, candidate, match_score, governance_report):
        try:
            from talentcopilot.ai.decision_engine import DecisionEngine
            return DecisionEngine().make_decision(candidate=candidate, job=job, match_score=match_score, governance_report=governance_report)
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
        if isinstance(value, (tuple, set)):
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

    def _normalize(self, value: Any) -> str:
        return " ".join(str(value).lower().replace("&", " and ").split())

    def _safe_float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
