from talentcopilot.decision_core.budget_intelligence_models import BudgetIntelligenceReport
from talentcopilot.decision_core.confidence_intelligence_models import ConfidenceIntelligenceReport
from talentcopilot.decision_core.evidence_intelligence_models import EvidenceIntelligenceReport
from talentcopilot.decision_core.executive_intelligence_models import (
    ExecutiveIntelligenceReport,
    StakeholderSummary,
)
from talentcopilot.decision_core.fit_intelligence_models import FitIntelligenceReport
from talentcopilot.decision_core.models import DecisionTraceStep, EvidenceGraph
from talentcopilot.decision_core.recommendation_intelligence_models import RecommendationIntelligenceReport
from talentcopilot.decision_core.risk_intelligence_models import RiskIntelligenceReport


class ExecutiveIntelligenceEngine:
    def evaluate(
        self,
        graph: EvidenceGraph,
        role_title: str,
        evidence_report: EvidenceIntelligenceReport,
        fit_report: FitIntelligenceReport,
        risk_report: RiskIntelligenceReport,
        confidence_report: ConfidenceIntelligenceReport,
        recommendation_report: RecommendationIntelligenceReport,
        budget_report: BudgetIntelligenceReport | None = None,
    ) -> ExecutiveIntelligenceReport:
        candidate = graph.candidate_name
        budget_text = (
            f"Budget feasibility is {budget_report.feasibility} with a budget fit of {budget_report.budget_fit_score}%."
            if budget_report
            else "Budget feasibility has not been assessed yet."
        )

        recruiter_summary = StakeholderSummary(
            audience="Recruiter",
            headline=f"{candidate}: {recommendation_report.recommendation}",
            summary=(
                f"Fit is {fit_report.fit_score}%, confidence is {confidence_report.confidence_score}%, "
                f"risk is {risk_report.risk_level}. {recommendation_report.rationale}"
            ),
            focus_points=[
                "Review candidate evidence and gaps.",
                "Use recommended next actions.",
                "Validate unresolved risks before final decision.",
            ],
        )

        hiring_manager_summary = StakeholderSummary(
            audience="Hiring Manager",
            headline=f"Operational assessment for {candidate}",
            summary=(
                f"The candidate's role fit is {fit_report.status}. "
                f"Risk level is {risk_report.risk_level}. "
                f"Focus the interview or review on the highest-impact fit gaps and risk factors."
            ),
            focus_points=[
                driver.detail for driver in fit_report.drivers[:3]
            ] or ["Validate operational fit through structured discussion."],
        )

        hr_director_summary = StakeholderSummary(
            audience="HR Director",
            headline=f"Decision governance summary for {candidate}",
            summary=(
                f"Recommendation is {recommendation_report.recommendation}. "
                f"Decision quality is {confidence_report.decision_quality}. "
                f"{budget_text}"
            ),
            focus_points=[
                "Check decision quality before final approval.",
                "Confirm budget and policy alignment.",
                "Review traceability for defensibility.",
            ],
        )

        executive_summary = StakeholderSummary(
            audience="Executive",
            headline=f"{candidate} — {recommendation_report.recommendation}",
            summary=(
                f"TalentCopilot recommends: {recommendation_report.recommendation}. "
                f"Fit {fit_report.fit_score}%, risk {risk_report.risk_level}, "
                f"confidence {confidence_report.confidence_score}%. "
                f"{recommendation_report.rationale}"
            ),
            focus_points=[
                "Decision is evidence-based.",
                "Human review remains required.",
                "Main trade-offs are fit, risk, confidence and budget feasibility.",
            ],
        )

        markdown = self.to_markdown(
            candidate,
            role_title,
            recommendation_report,
            fit_report,
            risk_report,
            confidence_report,
            evidence_report,
            budget_report,
        )

        return ExecutiveIntelligenceReport(
            candidate_name=candidate,
            role_title=role_title,
            recommendation=recommendation_report.recommendation,
            decision_quality=confidence_report.decision_quality,
            recruiter_summary=recruiter_summary,
            hiring_manager_summary=hiring_manager_summary,
            hr_director_summary=hr_director_summary,
            executive_summary=executive_summary,
            markdown_summary=markdown,
        )

    def add_trace_step(self, trace, graph: EvidenceGraph, report: ExecutiveIntelligenceReport):
        trace.add_step(
            DecisionTraceStep(
                step_id=f"executive_intelligence_{graph.graph_id}",
                engine="ExecutiveIntelligenceEngine",
                action="GENERATE_EXECUTIVE_SUMMARY",
                input_refs=[graph.graph_id],
                output_ref=report.recommendation,
                explanation=report.executive_summary.summary,
            )
        )
        return trace

    def to_markdown(
        self,
        candidate,
        role_title,
        recommendation_report,
        fit_report,
        risk_report,
        confidence_report,
        evidence_report,
        budget_report=None,
    ) -> str:
        lines = [
            f"# Decision Summary — {candidate}",
            "",
            f"Role: {role_title}",
            f"Recommendation: {recommendation_report.recommendation}",
            f"Decision quality: {confidence_report.decision_quality}",
            "",
            "## Core signals",
            f"- Fit Score: {fit_report.fit_score}%",
            f"- Fit Status: {fit_report.status}",
            f"- Risk Level: {risk_report.risk_level}",
            f"- Confidence: {confidence_report.confidence_score}%",
            f"- Evidence Readiness: {evidence_report.evidence_readiness_score}%",
        ]

        if budget_report:
            lines.extend([
                f"- Budget Fit: {budget_report.budget_fit_score}%",
                f"- Budget Feasibility: {budget_report.feasibility}",
            ])

        lines.extend([
            "",
            "## Rationale",
            recommendation_report.rationale,
            "",
            "## Next actions",
        ])

        for action in recommendation_report.next_actions:
            lines.append(f"- {action.title} ({action.owner}, {action.priority})")

        return "\n".join(lines)
