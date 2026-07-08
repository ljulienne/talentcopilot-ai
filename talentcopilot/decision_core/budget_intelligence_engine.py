from talentcopilot.decision_core.budget_intelligence_models import (
    BudgetContext,
    BudgetIntelligenceReport,
    CandidateCompensation,
)
from talentcopilot.decision_core.fit_intelligence_models import FitIntelligenceReport
from talentcopilot.decision_core.models import DecisionTraceStep, EvidenceGraph


class BudgetIntelligenceEngine:
    def evaluate(
        self,
        graph: EvidenceGraph,
        budget: BudgetContext,
        compensation: CandidateCompensation,
        fit_report: FitIntelligenceReport | None = None,
    ) -> BudgetIntelligenceReport:
        salary_gap = compensation.expected_salary - budget.maximum_salary
        budget_fit = self._budget_fit(budget, compensation.expected_salary)

        extra_cost = 0.0
        if compensation.expected_salary > budget.maximum_salary:
            extra_cost += compensation.expected_salary - budget.maximum_salary
        if compensation.relocation_required:
            extra_cost += budget.relocation_budget
        if compensation.visa_sponsorship_required:
            extra_cost += budget.visa_sponsorship_cost
        if budget.signing_bonus:
            extra_cost += budget.signing_bonus

        cost_impact = self._cost_impact(extra_cost)
        feasibility = self._feasibility(budget_fit)
        fit_score = fit_report.fit_score if fit_report else None

        recommendation, rationale = self._recommendation(fit_score, budget_fit, compensation.expected_salary, budget)

        actions = self._mitigations(recommendation, salary_gap, compensation)

        return BudgetIntelligenceReport(
            candidate_name=graph.candidate_name,
            budget_fit_score=budget_fit,
            salary_gap=salary_gap,
            estimated_extra_cost=extra_cost,
            cost_impact=cost_impact,
            feasibility=feasibility,
            budget_recommendation=recommendation,
            rationale=rationale,
            mitigation_actions=actions,
        )

    def add_trace_step(self, trace, graph: EvidenceGraph, report: BudgetIntelligenceReport):
        trace.add_step(
            DecisionTraceStep(
                step_id=f"budget_intelligence_{graph.graph_id}",
                engine="BudgetIntelligenceEngine",
                action="EVALUATE_BUDGET_FEASIBILITY",
                input_refs=[graph.graph_id],
                output_ref=str(report.budget_fit_score),
                explanation=report.rationale,
            )
        )
        return trace

    def _budget_fit(self, budget: BudgetContext, expected_salary: float) -> int:
        if expected_salary <= budget.target_salary:
            return 100
        if expected_salary <= budget.maximum_salary:
            span = max(1, budget.maximum_salary - budget.target_salary)
            return int(100 - ((expected_salary - budget.target_salary) / span) * 35)
        over = expected_salary - budget.maximum_salary
        return max(0, int(60 - (over / max(1, budget.maximum_salary)) * 200))

    def _cost_impact(self, extra_cost: float) -> str:
        if extra_cost <= 3000:
            return "Low"
        if extra_cost <= 12000:
            return "Medium"
        return "High"

    def _feasibility(self, budget_fit: int) -> str:
        if budget_fit >= 80:
            return "High"
        if budget_fit >= 55:
            return "Medium"
        return "Low"

    def _recommendation(self, fit_score, budget_fit: int, expected_salary: float, budget: BudgetContext):
        if fit_score is not None and fit_score < 30:
            return (
                "Budget Not Decisive",
                "Candidate fit is too low; budget should not drive the hiring decision.",
            )
        if fit_score is not None and fit_score >= 80 and budget_fit < 60:
            return (
                "Review Compensation Feasibility",
                "Candidate fit is strong but budget feasibility is weak.",
            )
        if budget_fit >= 75:
            return (
                "Budget Feasible",
                "Candidate expected compensation is compatible with budget assumptions.",
            )
        if expected_salary > budget.maximum_salary:
            return (
                "Budget Risk",
                "Expected salary exceeds the maximum budget.",
            )
        return (
            "Budget Review",
            "Financial feasibility requires stakeholder review.",
        )

    def _mitigations(self, recommendation: str, salary_gap: float, compensation: CandidateCompensation):
        actions = []
        if recommendation == "Review Compensation Feasibility":
            actions.extend([
                "Confirm compensation flexibility with the candidate.",
                "Validate whether the hiring budget can be increased.",
                "Compare with other high-fit candidates with stronger budget fit.",
            ])
        elif recommendation == "Budget Risk":
            actions.extend([
                "Review maximum salary approval threshold.",
                "Consider non-salary compensation levers.",
            ])
        elif recommendation == "Budget Feasible":
            actions.append("Proceed with the recruitment workflow.")
        else:
            actions.append("Review budget trade-offs with stakeholders.")

        if salary_gap > 0:
            actions.append(f"Address salary gap of {salary_gap:.0f}.")
        if compensation.relocation_required:
            actions.append("Validate relocation cost and timing.")
        if compensation.visa_sponsorship_required:
            actions.append("Validate visa sponsorship feasibility.")

        return actions
