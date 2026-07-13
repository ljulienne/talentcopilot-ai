from talentcopilot.services.official_score_service import get_official_candidate_score

from talentcopilot.models.hiring_budget import (
    CandidateBudgetAssessment,
    CandidateCostInput,
    HiringBudgetInput,
    HiringBudgetReport,
)


class HiringBudgetService:
    def default_budget(self) -> HiringBudgetInput:
        return HiringBudgetInput(
            target_salary=85000,
            maximum_salary=100000,
            relocation_budget=8000,
            agency_fee=0,
            signing_bonus=5000,
        )

    def build(self, session=None, budget: HiringBudgetInput | None = None) -> HiringBudgetReport:
        budget = budget or self.default_budget()

        if session is None or not getattr(session, "ranked_analyses", None):
            return HiringBudgetReport(
                role_title="No active recruitment",
                target_salary=budget.target_salary,
                maximum_salary=budget.maximum_salary,
                assessments=[],
            )

        assessments = []
        for index, analysis in enumerate(session.ranked_analyses):
            fit_score = get_official_candidate_score(analysis)
            expected_salary = self._estimate_salary(index, fit_score, budget)
            candidate_cost = CandidateCostInput(
                candidate_name=getattr(analysis, "candidate_name", "Candidate"),
                expected_salary=expected_salary,
                relocation_required=index == 0 and fit_score >= 85,
                notice_period_weeks=8 if index == 0 else 4,
                visa_sponsorship_required=False,
            )
            assessments.append(self.assess_candidate(candidate_cost, budget, fit_score))

        return HiringBudgetReport(
            role_title=getattr(session, "role_title", "Recruitment"),
            target_salary=budget.target_salary,
            maximum_salary=budget.maximum_salary,
            assessments=assessments,
        )

    def _estimate_salary(self, index: int, fit_score: float, budget: HiringBudgetInput) -> float:
        if fit_score >= 90:
            return budget.maximum_salary * 1.12
        if fit_score >= 80:
            return budget.maximum_salary * 0.98
        if fit_score >= 60:
            return budget.target_salary * 0.92
        return budget.target_salary * 0.75

    def assess_candidate(
        self,
        candidate: CandidateCostInput,
        budget: HiringBudgetInput,
        fit_score: float,
    ) -> CandidateBudgetAssessment:
        salary_gap = candidate.expected_salary - budget.maximum_salary

        if candidate.expected_salary <= budget.target_salary:
            budget_fit = 100
        elif candidate.expected_salary <= budget.maximum_salary:
            span = max(1, budget.maximum_salary - budget.target_salary)
            budget_fit = int(100 - ((candidate.expected_salary - budget.target_salary) / span) * 35)
        else:
            over = candidate.expected_salary - budget.maximum_salary
            budget_fit = max(0, int(60 - (over / max(1, budget.maximum_salary)) * 200))

        extra_cost = 0
        if candidate.relocation_required:
            extra_cost += budget.relocation_budget
        if candidate.visa_sponsorship_required:
            extra_cost += 5000
        if candidate.expected_salary > budget.maximum_salary:
            extra_cost += candidate.expected_salary - budget.maximum_salary

        if extra_cost <= 3000:
            cost_impact = "Low"
        elif extra_cost <= 12000:
            cost_impact = "Medium"
        else:
            cost_impact = "High"

        if budget_fit >= 80:
            feasibility = "High"
        elif budget_fit >= 55:
            feasibility = "Medium"
        else:
            feasibility = "Low"

        if fit_score < 30:
            recommendation = "Reject"
            rationale = "Candidate fit is too low; budget is not the main decision factor."
        elif fit_score >= 80 and budget_fit < 60:
            recommendation = "Review Compensation Feasibility"
            rationale = "Candidate is strong but financial feasibility is weak."
        elif fit_score >= 75 and budget_fit >= 70:
            recommendation = "Proceed"
            rationale = "Candidate fit and budget feasibility are aligned."
        elif budget_fit < 45:
            recommendation = "Budget Risk"
            rationale = "Expected cost exceeds acceptable range."
        else:
            recommendation = "Review"
            rationale = "Candidate requires further business review."

        next_actions = []
        if recommendation == "Review Compensation Feasibility":
            next_actions.extend([
                "Validate salary flexibility with candidate.",
                "Check whether additional budget can be approved.",
                "Compare with second candidate's budget feasibility.",
            ])
        elif recommendation == "Proceed":
            next_actions.append("Continue with interview or decision workflow.")
        elif recommendation == "Reject":
            next_actions.append("Do not advance unless role criteria change.")
        else:
            next_actions.append("Review budget and fit trade-offs with stakeholders.")

        return CandidateBudgetAssessment(
            candidate_name=candidate.candidate_name,
            fit_score=fit_score,
            expected_salary=candidate.expected_salary,
            salary_gap=salary_gap,
            budget_fit=max(0, min(100, budget_fit)),
            cost_impact=cost_impact,
            feasibility=feasibility,
            recommendation=recommendation,
            rationale=rationale,
            next_actions=next_actions,
        )
