from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ComparisonCandidate:
    rank: int
    candidate_name: str
    match_score: float
    recommendation: str
    key_strength: str
    key_risk: str
    # Internal diagnostic retained for backward compatibility.
    decision_score: Optional[float] = None
    # Canonical secondary indicator exposed in recruiter UX.
    ai_confidence: Optional[float] = None
    mission_rank: int = 0
    interview_priority: int = 0
    career_fit_score: Optional[float] = None


@dataclass
class ScoreGap:
    label: str
    value: float
    interpretation: str


@dataclass
class DecisionMatrixLine:
    candidate_name: str
    technical_fit: int
    leadership_fit: int
    evidence_strength: int
    decision_readiness: int


@dataclass
class ComparisonWorkspaceReport:
    role_title: str
    session_id: str
    candidates: List[ComparisonCandidate] = field(default_factory=list)
    score_gaps: List[ScoreGap] = field(default_factory=list)
    matrix: List[DecisionMatrixLine] = field(default_factory=list)
    differentiators: List[str] = field(default_factory=list)
