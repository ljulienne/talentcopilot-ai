from dataclasses import dataclass, field
from typing import List


@dataclass
class StakeholderSummary:
    audience: str
    headline: str
    summary: str
    focus_points: List[str] = field(default_factory=list)


@dataclass
class ExecutiveIntelligenceReport:
    candidate_name: str
    role_title: str
    recommendation: str
    decision_quality: str
    recruiter_summary: StakeholderSummary
    hiring_manager_summary: StakeholderSummary
    hr_director_summary: StakeholderSummary
    executive_summary: StakeholderSummary
    markdown_summary: str
