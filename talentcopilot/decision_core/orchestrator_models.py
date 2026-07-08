from dataclasses import dataclass, field
from typing import Dict, List, Optional

from talentcopilot.decision_core.models import CandidateDecisionProfile


@dataclass
class DecisionCoreInput:
    candidate: dict
    role_title: str
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    minimum_years_experience: int = 0
    target_salary: Optional[float] = None
    maximum_salary: Optional[float] = None
    expected_salary: Optional[float] = None
    relocation_required: bool = False
    visa_sponsorship_required: bool = False


@dataclass
class DecisionCoreOutput:
    profile: CandidateDecisionProfile
    pipeline_version: str
    engine_status: Dict[str, str] = field(default_factory=dict)

    @property
    def recommendation(self) -> str:
        return self.profile.recommendation or "No recommendation"
