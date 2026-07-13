from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class SessionStatus(str, Enum):
    DRAFT = "Draft"
    READY = "Ready"
    ANALYZING = "Analyzing"
    COMPLETED = "Completed"
    ERROR = "Error"


class CandidateAnalysisStatus(str, Enum):
    PENDING = "Pending"
    ANALYZED = "Analyzed"
    ERROR = "Error"


@dataclass
class CandidateAnalysisState:
    candidate_name: str
    candidate_id: str = ""
    status: CandidateAnalysisStatus = CandidateAnalysisStatus.PENDING
    match_score: float = 0.0
    ranking_score: Optional[float] = None
    rank: Optional[int] = None
    score_breakdown: Dict[str, float] = field(default_factory=dict)
    governance_report: Optional[Any] = None
    decision_report: Optional[Any] = None
    recruiter_copilot_report: Optional[Any] = None
    talent_locator_result: Optional[Any] = None
    errors: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    @property
    def is_analyzed(self) -> bool:
        return self.status == CandidateAnalysisStatus.ANALYZED

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)

    @property
    def official_match_score(self) -> float:
        """Return the consolidated ranking score when available.

        match_score remains the raw fit score for diagnostics and backward
        compatibility. ranking_score is the recruiter-facing consolidated
        score used to order candidates.
        """
        if self.ranking_score is not None:
            return float(self.ranking_score)
        return float(self.match_score)

    @property
    def official_rank(self) -> Optional[int]:
        return self.rank


@dataclass
class RecruitmentSession:
    session_id: str
    job: Dict[str, Any]
    candidates: List[Dict[str, Any]] = field(default_factory=list)
    status: SessionStatus = SessionStatus.DRAFT
    analyses: List[CandidateAnalysisState] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def role_title(self) -> str:
        return str(self.job.get("title", "Role"))

    @property
    def candidate_count(self) -> int:
        return len(self.candidates)

    @property
    def analyzed_count(self) -> int:
        return len([analysis for analysis in self.analyses if analysis.is_analyzed])

    @property
    def error_count(self) -> int:
        return len([analysis for analysis in self.analyses if analysis.has_errors])

    @property
    def ranked_analyses(self) -> List[CandidateAnalysisState]:
        return sorted(
            self.analyses,
            key=lambda item: (
                item.rank if item.rank is not None else 9999,
                -float(item.match_score),
                item.candidate_id or item.candidate_name,
            ),
        )

    def mark_updated(self) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def add_analysis(self, analysis: CandidateAnalysisState) -> None:
        self.analyses.append(analysis)
        self.mark_updated()

    def get_analysis(self, candidate_key: str) -> Optional[CandidateAnalysisState]:
        for analysis in self.analyses:
            if analysis.candidate_id == candidate_key or analysis.candidate_name == candidate_key:
                return analysis
        return None
