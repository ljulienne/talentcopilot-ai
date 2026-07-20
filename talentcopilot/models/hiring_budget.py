from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class HiringBudgetInput:
    target_salary: float
    maximum_salary: float
    relocation_budget: float = 0.0
    agency_fee: float = 0.0
    signing_bonus: float = 0.0


@dataclass
class CandidateCostInput:
    candidate_name: str
    expected_salary: float
    relocation_required: bool = False
    notice_period_weeks: int = 0
    visa_sponsorship_required: bool = False


@dataclass
class CandidateBudgetAssessment:
    candidate_name: str
    fit_score: float
    expected_salary: Optional[float]
    salary_gap: Optional[float]
    budget_fit: Optional[int]
    cost_impact: str
    feasibility: str
    recommendation: str
    rationale: str
    next_actions: List[str] = field(default_factory=list)
    talent_recommendation: str = "Review"
    compensation_data_status: str = "Available"
    budget_recommendation: str = "Review"


@dataclass
class HiringBudgetReport:
    role_title: str
    target_salary: float
    maximum_salary: float
    assessments: List[CandidateBudgetAssessment] = field(default_factory=list)
