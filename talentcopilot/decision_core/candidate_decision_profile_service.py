from hashlib import md5

from talentcopilot.decision_core.budget_intelligence_engine import BudgetIntelligenceEngine
from talentcopilot.decision_core.budget_intelligence_models import BudgetContext, CandidateCompensation
from talentcopilot.decision_core.confidence_intelligence_engine import ConfidenceIntelligenceEngine
from talentcopilot.decision_core.decision_trace_service import DecisionTraceService
from talentcopilot.decision_core.evidence_graph_builder import EvidenceGraphBuilder
from talentcopilot.decision_core.evidence_intelligence_engine import EvidenceIntelligenceEngine
from talentcopilot.decision_core.fit_intelligence_engine import FitIntelligenceEngine
from talentcopilot.decision_core.fit_intelligence_models import RoleRequirements
from talentcopilot.decision_core.models import CandidateDecisionProfile
from talentcopilot.decision_core.recommendation_intelligence_engine import RecommendationIntelligenceEngine
from talentcopilot.decision_core.risk_intelligence_engine import RiskIntelligenceEngine


class CandidateDecisionProfileService:
    def build_from_candidate_dict(
        self,
        candidate: dict,
        role_title: str = "Recruitment",
        role_requirements: RoleRequirements | None = None,
        budget_context: BudgetContext | None = None,
        compensation: CandidateCompensation | None = None,
    ) -> CandidateDecisionProfile:
        name = candidate.get("name", "Candidate")
        graph = EvidenceGraphBuilder().build_from_candidate_dict(candidate, role_title)
        trace = DecisionTraceService().initialize_trace(name, graph)

        evidence_engine = EvidenceIntelligenceEngine()
        evidence_report = evidence_engine.evaluate(graph)
        evidence_engine.add_trace_step(trace, graph, evidence_report)

        role = role_requirements or RoleRequirements(role_title=role_title)
        fit_engine = FitIntelligenceEngine()
        fit_report = fit_engine.evaluate(graph, role, evidence_report)
        fit_engine.add_trace_step(trace, graph, fit_report)

        risk_engine = RiskIntelligenceEngine()
        risk_report = risk_engine.evaluate(graph, role, evidence_report, fit_report)
        risk_engine.add_trace_step(trace, graph, risk_report)

        budget_report = None
        if budget_context and compensation:
            budget_engine = BudgetIntelligenceEngine()
            budget_report = budget_engine.evaluate(graph, budget_context, compensation, fit_report)
            budget_engine.add_trace_step(trace, graph, budget_report)

        confidence_engine = ConfidenceIntelligenceEngine()
        confidence_report = confidence_engine.evaluate(graph, evidence_report, fit_report, risk_report, trace, budget_report)
        confidence_engine.add_trace_step(trace, graph, confidence_report)

        recommendation_engine = RecommendationIntelligenceEngine()
        recommendation_report = recommendation_engine.evaluate(
            graph,
            evidence_report,
            fit_report,
            risk_report,
            confidence_report,
            budget_report,
        )
        recommendation_engine.add_trace_step(trace, graph, recommendation_report)

        metadata = {
            "profile_version": "dic-v2.0-alpha-g",
            "evidence_status": evidence_report.status,
            "evidence_quality_score": str(evidence_report.evidence_quality_score),
            "evidence_readiness_score": str(evidence_report.evidence_readiness_score),
            "fit_status": fit_report.status,
            "fit_score": str(fit_report.fit_score),
            "fit_summary": fit_report.summary,
            "risk_score": str(risk_report.risk_score),
            "risk_level": risk_report.risk_level,
            "risk_summary": risk_report.summary,
            "confidence_score": str(confidence_report.confidence_score),
            "confidence_level": confidence_report.confidence_level,
            "decision_quality": confidence_report.decision_quality,
            "recommendation": recommendation_report.recommendation,
            "recommendation_category": recommendation_report.category,
            "recommendation_rationale": recommendation_report.rationale,
        }

        if budget_report:
            metadata.update({
                "budget_fit_score": str(budget_report.budget_fit_score),
                "budget_feasibility": budget_report.feasibility,
                "budget_recommendation": budget_report.budget_recommendation,
                "salary_gap": str(budget_report.salary_gap),
            })

        return CandidateDecisionProfile(
            profile_id=self._id("profile", name, role_title),
            candidate_name=name,
            role_title=role_title,
            evidence_graph=graph,
            decision_trace=trace,
            fit_score=fit_report.fit_score,
            confidence_score=confidence_report.confidence_score,
            risk_level=risk_report.risk_level,
            recommendation=recommendation_report.recommendation,
            metadata=metadata,
        )

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
