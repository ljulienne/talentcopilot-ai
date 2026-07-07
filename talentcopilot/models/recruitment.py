from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class JobProfile:
    title: str = "Untitled role"
    company: str = ""
    department: str = ""
    location: str = ""
    language: str = "English"


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
class AnalysisResult:
    candidate: CandidateProfile
    rank: Optional[int] = None
    status: str = "analysed"


@dataclass
class RecruitmentSession:
    job: JobProfile
    results: List[AnalysisResult] = field(default_factory=list)
    source: str = "session_state"

    @property
    def total_candidates(self) -> int:
        return len(self.results)

    @property
    def ranked_results(self) -> List[AnalysisResult]:
        return sorted(
            self.results,
            key=lambda r: r.candidate.decision_confidence or r.candidate.score,
            reverse=True,
        )

    @property
    def best_candidate(self) -> Optional[CandidateProfile]:
        ranked = self.ranked_results
        return ranked[0].candidate if ranked else None

    @property
    def average_confidence(self) -> float:
        if not self.results:
            return 0.0
        return round(
            sum(r.candidate.decision_confidence for r in self.results) / len(self.results),
            2,
        )
