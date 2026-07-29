from __future__ import annotations

from typing import Any, Mapping, Optional

from talentcopilot.models.hiring_budget import (
    CandidateBudgetAssessment,
    CandidateCostInput,
    HiringBudgetInput,
    HiringBudgetReport,
)
from talentcopilot.services.candidate_decision_signal_service import (
    CandidateDecisionSignalService,
)


class HiringBudgetService:
    """Keep talent suitability separate from compensation feasibility.

    The service never fabricates a salary expectation. When compensation data is
    absent, it preserves the official recruitment recommendation and reports the
    budget decision as pending.
    """

    def __init__(self, signal_service=None):
        self.signal_service = signal_service or CandidateDecisionSignalService()

    def default_budget(self) -> HiringBudgetInput:
        return HiringBudgetInput(
            target_salary=85000,
            maximum_salary=100000,
            minimum_salary=70000,
            currency="EUR",
            target_bonus_percent=10,
            benefits_budget=6000,
            relocation_budget=8000,
            agency_fee=0,
            signing_bonus=5000,
            onboarding_cost=4000,
            first_year_cost_limit=120000,
        )

    def build(self, session=None, budget: HiringBudgetInput | None = None) -> HiringBudgetReport:
        budget = budget or self.default_budget()

        if session is None or not getattr(session, "ranked_analyses", None):
            return HiringBudgetReport(
                role_title="No active recruitment",
                target_salary=budget.target_salary,
                maximum_salary=budget.maximum_salary,
                assessments=[],
                minimum_salary=budget.minimum_salary,
                currency=budget.currency,
                first_year_cost_limit=budget.first_year_cost_limit,
            )

        assessments = []
        for analysis in session.ranked_analyses:
            fit_score = float(getattr(analysis, "match_score", 0) or 0)
            talent_recommendation = self.signal_service.build(
                analysis, session
            ).recommendation
            candidate = self._candidate_record(analysis, session)
            expected_salary = self._expected_salary(candidate, analysis)

            if expected_salary is None:
                assessments.append(
                    self._assessment_without_compensation(
                        analysis=analysis,
                        fit_score=fit_score,
                        talent_recommendation=talent_recommendation,
                        currency=budget.currency,
                    )
                )
                continue

            candidate_cost = CandidateCostInput(
                candidate_name=getattr(analysis, "candidate_name", "Candidate"),
                expected_salary=expected_salary,
                relocation_required=bool(candidate.get("relocation_required", False)),
                notice_period_weeks=int(candidate.get("notice_period_weeks", 0) or 0),
                visa_sponsorship_required=bool(
                    candidate.get("visa_sponsorship_required", False)
                ),
                variable_compensation=self._number(candidate.get("variable_compensation")),
                benefits_value=self._number(candidate.get("benefits_value")),
                signing_bonus_requested=self._number(candidate.get("signing_bonus_requested")),
                relocation_support_requested=self._number(
                    candidate.get("relocation_support_requested")
                ),
                benefits_requested=str(candidate.get("benefits_requested", "") or ""),
                availability_date=str(candidate.get("availability_date", "") or ""),
                flexibility=str(candidate.get("flexibility", "Unknown") or "Unknown"),
                notes=str(candidate.get("notes", "") or ""),
                currency=str(candidate.get("currency", budget.currency) or budget.currency),
            )
            assessment = self.assess_candidate(candidate_cost, budget, fit_score)
            assessment.talent_recommendation = talent_recommendation
            assessments.append(assessment)

        return HiringBudgetReport(
            role_title=getattr(session, "role_title", "Recruitment"),
            target_salary=budget.target_salary,
            maximum_salary=budget.maximum_salary,
            assessments=assessments,
            minimum_salary=budget.minimum_salary,
            currency=budget.currency,
            first_year_cost_limit=budget.first_year_cost_limit,
        )

    def _assessment_without_compensation(
        self,
        *,
        analysis: Any,
        fit_score: float,
        talent_recommendation: str,
        currency: str = "EUR",
    ) -> CandidateBudgetAssessment:
        candidate_name = str(
            getattr(analysis, "candidate_name", "Candidate") or "Candidate"
        )
        return CandidateBudgetAssessment(
            candidate_name=candidate_name,
            fit_score=fit_score,
            expected_salary=None,
            salary_gap=None,
            budget_fit=None,
            cost_impact="Not assessed",
            feasibility="Insufficient data",
            recommendation=talent_recommendation,
            talent_recommendation=talent_recommendation,
            compensation_data_status="Missing salary expectation",
            budget_recommendation="Pending compensation data",
            rationale=(
                f"{candidate_name}'s talent recommendation remains "
                f"'{talent_recommendation}'. A budget conclusion cannot be issued "
                "because no candidate salary expectation is available."
            ),
            next_actions=[
                "Collect the candidate's salary expectation and currency.",
                "Confirm the approved salary range and total compensation assumptions.",
                "Re-run the budget assessment without changing the official talent recommendation.",
            ],
            currency=currency,
        )

    def _candidate_record(self, analysis: Any, session: Any) -> Mapping[str, Any]:
        candidate_id = str(getattr(analysis, "candidate_id", "") or "")
        candidate_name_raw = str(getattr(analysis, "candidate_name", "") or "")
        candidate_name = candidate_name_raw.casefold()
        record: dict[str, Any] = {}
        for item in list(getattr(session, "candidates", []) or []):
            source = dict(item) if isinstance(item, Mapping) else {}
            record_id = str(source.get("candidate_id", "") or "")
            record_name = str(
                source.get("name", source.get("candidate_name", "")) or ""
            ).casefold()
            if candidate_id and record_id == candidate_id:
                record = source
                break
            if candidate_name and record_name == candidate_name:
                record = source
                break

        metadata = getattr(session, "metadata", {}) or {}
        store = metadata.get("candidate_compensation", {}) if isinstance(metadata, Mapping) else {}
        if isinstance(store, Mapping):
            expectation = store.get(candidate_id) or store.get(candidate_name_raw) or {}
            if isinstance(expectation, Mapping):
                record = {**record, **dict(expectation)}
        return record

    def _expected_salary(
        self, candidate: Mapping[str, Any], analysis: Any
    ) -> Optional[float]:
        sources = [
            candidate.get("expected_salary"),
            candidate.get("salary_expectation"),
            candidate.get("desired_salary"),
        ]
        compensation = candidate.get("compensation")
        if isinstance(compensation, Mapping):
            sources.extend(
                [
                    compensation.get("expected_salary"),
                    compensation.get("salary_expectation"),
                ]
            )
        breakdown = getattr(analysis, "score_breakdown", {}) or {}
        if isinstance(breakdown, Mapping):
            sources.extend(
                [
                    breakdown.get("expected_salary"),
                    breakdown.get("salary_expectation"),
                ]
            )

        for value in sources:
            try:
                parsed = float(value)
            except (TypeError, ValueError):
                continue
            if parsed > 0:
                return parsed
        return None

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
            budget_fit = int(
                100
                - ((candidate.expected_salary - budget.target_salary) / span) * 35
            )
        else:
            over = candidate.expected_salary - budget.maximum_salary
            budget_fit = max(
                0,
                int(60 - (over / max(1, budget.maximum_salary)) * 200),
            )

        extra_cost = 0.0
        if candidate.relocation_required:
            extra_cost += budget.relocation_budget
        if candidate.visa_sponsorship_required:
            extra_cost += 5000
        if candidate.expected_salary > budget.maximum_salary:
            extra_cost += candidate.expected_salary - budget.maximum_salary

        requested_package = float(
            candidate.expected_salary
            + candidate.variable_compensation
            + candidate.benefits_value
            + candidate.signing_bonus_requested
            + candidate.relocation_support_requested
        )
        total_first_year_cost = float(
            requested_package + budget.agency_fee + budget.onboarding_cost
        )
        first_year_limit = float(budget.first_year_cost_limit or 0.0)
        if first_year_limit <= 0:
            first_year_limit = float(
                budget.maximum_salary
                + budget.benefits_budget
                + budget.signing_bonus
                + budget.relocation_budget
                + budget.agency_fee
                + budget.onboarding_cost
            )
        package_gap = total_first_year_cost - first_year_limit
        if package_gap > 0:
            extra_cost += package_gap

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
            next_actions.extend(
                [
                    "Validate salary flexibility with candidate.",
                    "Check whether additional budget can be approved.",
                    "Compare with another high-fit candidate's budget feasibility.",
                ]
            )
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
            talent_recommendation=recommendation,
            compensation_data_status="Available",
            budget_recommendation=recommendation,
            rationale=rationale,
            next_actions=next_actions,
            requested_package=requested_package,
            total_first_year_cost=total_first_year_cost,
            package_gap=package_gap,
            benefits_requested=candidate.benefits_requested,
            availability_date=candidate.availability_date,
            flexibility=candidate.flexibility,
            currency=candidate.currency or budget.currency,
        )

    @staticmethod
    def _number(value: Any) -> float:
        try:
            return max(0.0, float(value or 0.0))
        except (TypeError, ValueError):
            return 0.0
