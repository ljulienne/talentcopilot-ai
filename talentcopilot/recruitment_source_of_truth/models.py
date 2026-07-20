from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class OfficialCandidateRecord:
    candidate_id: str
    candidate_name: str
    mission_fit_score: float
    decision_score: Optional[float]
    mission_rank: int
    decision_rank: int
    interview_priority: int
    confidence: Optional[float] = None
    career_fit_score: Optional[float] = None
    recruiter_fit_score: Optional[float] = None
    score_breakdown: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RecruitmentSourceOfTruth:
    session_id: str
    role_title: str
    version: str
    candidates: List[OfficialCandidateRecord]
    analysis_fingerprint: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "role_title": self.role_title,
            "version": self.version,
            "analysis_fingerprint": self.analysis_fingerprint,
            "candidates": [item.to_dict() for item in self.candidates],
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "RecruitmentSourceOfTruth":
        return cls(
            session_id=str(payload.get("session_id", "")),
            role_title=str(payload.get("role_title", "Recruitment")),
            version=str(payload.get("version", "recruitment-sot-v1.0")),
            analysis_fingerprint=str(payload.get("analysis_fingerprint", "")),
            candidates=[OfficialCandidateRecord(**item) for item in payload.get("candidates", [])],
        )
