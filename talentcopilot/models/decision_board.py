from dataclasses import dataclass, field
from typing import List


@dataclass
class StakeholderDecision:
    stakeholder: str
    recommendation: str
    confidence: int
    comment: str = ""


@dataclass
class DecisionReason:
    title: str
    detail: str
    strength: str = "High"


@dataclass
class DecisionRisk:
    title: str
    detail: str
    severity: str = "Medium"


@dataclass
class CandidateDecisionSummary:
    candidate_name: str
    rank: int
    match_score: float
    ai_recommendation: str
    consensus_score: int
    stakeholder_decisions: List[StakeholderDecision] = field(default_factory=list)
    reasons: List[DecisionReason] = field(default_factory=list)
    risks: List[DecisionRisk] = field(default_factory=list)


@dataclass
class DecisionBoardReport:
    role_title: str
    session_id: str
    decision_status: str
    candidates: List[CandidateDecisionSummary] = field(default_factory=list)
    next_actions: List[str] = field(default_factory=list)
