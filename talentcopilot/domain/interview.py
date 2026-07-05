from dataclasses import dataclass, field
from typing import List


@dataclass
class InterviewPlan:
    focus_areas: List[str] = field(default_factory=list)
    questions: List[str] = field(default_factory=list)
    risk_validation_points: List[str] = field(default_factory=list)
