"""Legacy recruitment compatibility models.

This module preserves the historical session_adapter/session_manager API.
It is a compatibility boundary only.

The official Release 3.0 source of truth remains:
    talentcopilot.models.recruitment_session.RecruitmentSession
    CandidateAnalysisState.match_score
    CandidateAnalysisState.rank
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class CandidateProfile:
    name: str
    role: str = ""
    summary: str = ""
    skills: List[str] = field(default_factory=list)
    score: float = 0.0
    decision_confidence: float = 0.0
    recommendation: str = "Review required"
    risks: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class JobProfile:
    title: str
    company: str = ""
    department: str = ""
    location: str = ""
    language: str = "English"


@dataclass
class AnalysisResult:
    candidate: CandidateProfile
    rank: int

    @property
    def match_score(self) -> float:
        return float(self.candidate.score)

    @property
    def official_match_score(self) -> float:
        return float(self.candidate.score)

    @property
    def official_rank(self) -> int:
        return self.rank


@dataclass
class RecruitmentSession:
    job: JobProfile
    results: List[AnalysisResult] = field(default_factory=list)

    @property
    def ranked_analyses(self) -> List[AnalysisResult]:
        """Expose the legacy results using the official ranking vocabulary."""
        return sorted(
            self.results,
            key=lambda item: (
                item.rank,
                -float(item.candidate.score),
                item.candidate.name,
            ),
        )
