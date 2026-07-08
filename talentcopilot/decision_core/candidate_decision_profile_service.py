from hashlib import md5

from talentcopilot.decision_core.decision_trace_service import DecisionTraceService
from talentcopilot.decision_core.evidence_graph_builder import EvidenceGraphBuilder
from talentcopilot.decision_core.evidence_intelligence_engine import EvidenceIntelligenceEngine
from talentcopilot.decision_core.fit_intelligence_engine import FitIntelligenceEngine
from talentcopilot.decision_core.fit_intelligence_models import RoleRequirements
from talentcopilot.decision_core.models import CandidateDecisionProfile


class CandidateDecisionProfileService:
    def build_from_candidate_dict(
        self,
        candidate: dict,
        role_title: str = "Recruitment",
        role_requirements: RoleRequirements | None = None,
    ) -> CandidateDecisionProfile:
        name = candidate.get("name", "Candidate")
        graph = EvidenceGraphBuilder().build_from_candidate_dict(candidate, role_title)
        trace = DecisionTraceService().initialize_trace(name, graph)

        evidence_engine = EvidenceIntelligenceEngine()
        evidence_report = evidence_engine.evaluate(graph)
        evidence_engine.add_trace_step(trace, graph, evidence_report)

        role = role_requirements or RoleRequirements(
            role_title=role_title,
            required_skills=[],
            preferred_skills=[],
            minimum_years_experience=0,
        )

        fit_engine = FitIntelligenceEngine()
        fit_report = fit_engine.evaluate(graph, role, evidence_report)
        fit_engine.add_trace_step(trace, graph, fit_report)

        profile = CandidateDecisionProfile(
            profile_id=self._id("profile", name, role_title),
            candidate_name=name,
            role_title=role_title,
            evidence_graph=graph,
            decision_trace=trace,
            fit_score=fit_report.fit_score,
            confidence_score=evidence_report.evidence_readiness_score,
            risk_level=None,
            recommendation=None,
            metadata={
                "profile_version": "dic-v2.0-alpha-c",
                "evidence_status": evidence_report.status,
                "evidence_quality_score": str(evidence_report.evidence_quality_score),
                "evidence_readiness_score": str(evidence_report.evidence_readiness_score),
                "fit_status": fit_report.status,
                "fit_score": str(fit_report.fit_score),
                "fit_summary": fit_report.summary,
            },
        )

        return profile

    def build_many(
        self,
        candidates: list[dict],
        role_title: str = "Recruitment",
        role_requirements: RoleRequirements | None = None,
    ) -> list[CandidateDecisionProfile]:
        return [
            self.build_from_candidate_dict(candidate, role_title, role_requirements)
            for candidate in candidates
        ]

    def _id(self, *parts: str) -> str:
        raw = "::".join(parts)
        return md5(raw.encode("utf-8")).hexdigest()[:16]
