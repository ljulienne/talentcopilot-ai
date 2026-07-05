from dataclasses import dataclass, field
from typing import List, Optional

from talentcopilot.domain.application import Application
from talentcopilot.domain.evidence import Evidence
from talentcopilot.domain.hiring_strategy import HiringStrategy
from talentcopilot.domain.interview import InterviewPlan


@dataclass
class CandidateDecision:
    application: Application
    match_score: int
    rank: Optional[int] = None
    recommendation: str = ""
    confidence: int = 0
    decision_basis: str = "Official Match Score"
    evidence: List[Evidence] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    interview_plan: InterviewPlan = field(default_factory=InterviewPlan)
    hiring_strategy: Optional[HiringStrategy] = None
    executive_summary: str = ""
    next_action: str = ""
