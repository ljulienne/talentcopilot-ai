from dataclasses import dataclass, field
from typing import List


@dataclass
class BudgetContext:
    target_salary: float
    maximum_salary: float
    relocation_budget: float = 0.0
    signing_bonus: float = 0.0
    visa_sponsorship_cost: float = 0.0


@dataclass
class CandidateCompensation:
    expected_salary: float
    relocation_required: bool = False
    visa_sponsorship_required: bool = False
    notice_period_weeks: int = 0


@dataclass
class BudgetIntelligenceReport:
    candidate_name: str
    budget_fit_score: int
    salary_gap: float
    estimated_extra_cost: float
    cost_impact: str
    feasibility: str
    budget_recommendation: str
    rationale: str
    mitigation_actions: List[str] = field(default_factory=list)
