from dataclasses import dataclass, field
from typing import List


@dataclass
class InterviewRating:
    competency: str
    score: int
    evidence_confirmed: bool
    notes: str = ""


@dataclass
class InterviewEvaluationSummary:
    candidate_name: str
    overall_score: float
    decision_impact: str
    recommendation_after_interview: str
    strengths_confirmed: List[str] = field(default_factory=list)
    risks_remaining: List[str] = field(default_factory=list)
    ratings: List[InterviewRating] = field(default_factory=list)
