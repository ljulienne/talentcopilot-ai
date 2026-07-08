from dataclasses import dataclass, field
from typing import List


@dataclass
class ExecutiveCandidateLine:
    rank: int
    candidate_name: str
    match_score: float
    recommendation: str
    decision_readiness: int


@dataclass
class ExecutiveRiskLine:
    title: str
    detail: str
    severity: str = "Medium"


@dataclass
class ExecutiveReport:
    role_title: str
    session_id: str
    executive_summary: str
    shortlist: List[ExecutiveCandidateLine] = field(default_factory=list)
    risks: List[ExecutiveRiskLine] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
