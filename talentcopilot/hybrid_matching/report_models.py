from dataclasses import dataclass, field
from typing import List


@dataclass
class HybridRecruiterReport:
    candidate_name: str
    role_title: str
    readiness_level: str
    executive_summary: str
    top_strengths: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)
    interview_focus: List[str] = field(default_factory=list)
    action_recommendation: str = "Review"
