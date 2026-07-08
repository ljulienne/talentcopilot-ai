from dataclasses import dataclass, field
from typing import List


@dataclass
class HybridDecisionCandidate:
    rank: int
    candidate_name: str
    role_title: str
    decision_fit_score: int
    semantic_score: int
    career_score: int
    hybrid_score: int
    final_score: int
    readiness_level: str
    action_recommendation: str
    top_strengths: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)
    interview_focus: List[str] = field(default_factory=list)


@dataclass
class HybridDecisionBoard:
    role_title: str
    candidates: List[HybridDecisionCandidate] = field(default_factory=list)

    @property
    def top_candidate(self) -> HybridDecisionCandidate | None:
        return self.candidates[0] if self.candidates else None

    @property
    def total_candidates(self) -> int:
        return len(self.candidates)
