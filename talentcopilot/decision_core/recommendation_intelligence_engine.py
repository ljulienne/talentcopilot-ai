from talentcopilot.decision_core.budget_intelligence_models import BudgetIntelligenceReport
from talentcopilot.decision_core.confidence_intelligence_models import ConfidenceIntelligenceReport
from talentcopilot.decision_core.evidence_intelligence_models import EvidenceIntelligenceReport
from talentcopilot.decision_core.fit_intelligence_models import FitIntelligenceReport
from talentcopilot.decision_core.models import DecisionTraceStep, EvidenceGraph
from talentcopilot.decision_core.recommendation_intelligence_models import (
    RecommendationAction,
    RecommendationIntelligenceReport,
    RecommendationReason,
)
from talentcopilot.decision_core.risk_intelligence_models import RiskIntelligenceReport


class RecommendationIntelligenceEngine:
    def evaluate(
        self,
        graph: EvidenceGraph,
        evidence_report: EvidenceIntelligenceReport,
        fit_report: FitIntelligenceReport,
        risk_report: RiskIntelligenceReport,
        confidence_report: ConfidenceIntelligenceReport,
        budget_report: BudgetIntelligenceReport | None = None,
    ) -> RecommendationIntelligenceReport:
        fit = fit_report.fit_score
        risk = risk_report.risk_level
        confidence = confidence_report.confidence_score
        budget_fit = budget_report.budget_fit_score if budget_report else None

        reasons = []
        blockers = []

        reasons.append(RecommendationReason("Fit", f"Fit score is {fit}%.", "Primary"))
        reasons.append(RecommendationReason("Risk", f"Risk level is {risk}.", "Constraint"))
        reasons.append(RecommendationReason("Confidence", f"Confidence score is {confidence}%.", "Reliability"))

        if budget_report:
            reasons.append(
                RecommendationReason("Budget", f"Budget fit is {budget_fit}%.", "Feasibility")
            )

        if fit < 30:
            recommendation = "Reject"
            category = "No Fit"
            rationale = "Candidate fit is too low for the current role. Budget or affordability cannot override no-fit."
            blockers.append("Fit score below minimum threshold.")
            actions = [RecommendationAction("Do not advance candidate", "Recruiter", "High")]
        elif fit < 50:
            recommendation = "Reject"
            category = "Weak Fit"
            rationale = "Candidate fit is weak and critical gaps remain."
            blockers.append("Candidate fit below interview threshold.")
            actions = [RecommendationAction("Prioritize stronger candidates", "Recruiter", "High")]
        elif confidence < 45:
            recommendation = "More Evidence Required"
            category = "Insufficient Confidence"
            rationale = "Candidate fit may be usable, but the analysis confidence is too low for a reliable decision."
            blockers.append("Confidence below decision threshold.")
            actions = [RecommendationAction("Collect additional evidence", "Recruiter", "High")]
        elif budget_report and fit >= 80 and budget_fit is not None and budget_fit < 60:
            recommendation = "Review Compensation Feasibility"
            category = "Budget Trade-off"
            rationale = "Candidate fit is strong, but financial feasibility is weak."
            blockers.append("Budget fit below feasibility threshold.")
            actions = [
                RecommendationAction("Validate compensation flexibility", "Recruiter", "High"),
                RecommendationAction("Request budget approval if needed", "HR Director", "Medium"),
            ]
        elif risk in {"Critical", "High"} and fit >= 70:
            recommendation = "Interview"
            category = "Risk Validation"
            rationale = "Candidate fit is promising, but risk factors must be validated before decision."
            blockers.extend([factor.detail for factor in risk_report.risk_factors[:3]])
            actions = [RecommendationAction("Run structured risk-focused interview", "Hiring Manager", "High")]
        elif fit >= 88 and confidence >= 80 and risk == "Low":
            recommendation = "Strong Hire"
            category = "Strong Positive"
            rationale = "Candidate has strong fit, low risk and high confidence."
            actions = [RecommendationAction("Proceed to Decision Board", "Recruiter", "High")]
        elif fit >= 78 and confidence >= 65 and risk in {"Low", "Medium"}:
            recommendation = "Hire"
            category = "Positive"
            rationale = "Candidate has strong enough fit and acceptable decision confidence."
            actions = [RecommendationAction("Proceed with hiring workflow", "Recruiter", "High")]
        elif fit >= 60:
            recommendation = "Interview"
            category = "Validate"
            rationale = "Candidate may fit the role but requires interview validation."
            actions = [RecommendationAction("Prepare targeted interview", "Recruiter", "Medium")]
        else:
            recommendation = "Review"
            category = "Manual Review"
            rationale = "Signals are mixed and require recruiter review."
            actions = [RecommendationAction("Review candidate manually", "Recruiter", "Medium")]

        return RecommendationIntelligenceReport(
            candidate_name=graph.candidate_name,
            recommendation=recommendation,
            category=category,
            rationale=rationale,
            confidence_level=confidence_report.confidence_level,
            reasons=reasons,
            blockers=blockers,
            next_actions=actions,
        )

    def add_trace_step(self, trace, graph: EvidenceGraph, report: RecommendationIntelligenceReport):
        trace.add_step(
            DecisionTraceStep(
                step_id=f"recommendation_intelligence_{graph.graph_id}",
                engine="RecommendationIntelligenceEngine",
                action="GENERATE_FINAL_RECOMMENDATION",
                input_refs=[graph.graph_id],
                output_ref=report.recommendation,
                explanation=report.rationale,
            )
        )
        return trace
