from dataclasses import dataclass, field
from typing import List


@dataclass
class ScoreContribution:
    category: str
    label: str
    points: int
    evidence: List[str] = field(default_factory=list)
    explanation: str = ""


@dataclass
class HybridScoreBreakdown:
    semantic_points: int
    career_points: int
    evidence_points: int
    penalties: int
    final_score: int


@dataclass
class HybridExplanationReport:
    candidate_name: str
    role_title: str
    breakdown: HybridScoreBreakdown
    positive_contributions: List[ScoreContribution] = field(default_factory=list)
    penalties: List[ScoreContribution] = field(default_factory=list)
    recruiter_summary: str = ""
    focus_areas: List[str] = field(default_factory=list)
