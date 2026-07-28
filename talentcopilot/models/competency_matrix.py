from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Optional


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class CompetencyAssessment:
    competency_id: str
    competency_name: str
    category: str
    importance: str
    required_level: float
    ai_estimated_level: float
    confidence: str
    evidence_status: str
    evidence: str
    interviewer_level: Optional[float] = None
    consolidated_level: Optional[float] = None
    validation_status: str = "To validate"
    comment: str = ""
    interview_evidence: str = ""
    origin: str = "job_requirement"
    is_active: bool = True
    removed_reason: str = ""
    added_by: str = ""
    added_at: str = ""
    requirement_family: str = ""
    requirement_kind: str = ""
    source_excerpt: str = ""
    related_evidence: list[str] = field(default_factory=list)
    interview_priority: str = "Validate"

    def effective_level(self) -> float:
        if self.interviewer_level is not None:
            return float(self.interviewer_level)
        if self.consolidated_level is not None:
            return float(self.consolidated_level)
        return float(self.ai_estimated_level)

    @property
    def is_job_requirement(self) -> bool:
        return self.origin == "job_requirement"


@dataclass
class CompetencyAuditEntry:
    competency_id: str
    field_name: str
    previous_value: object
    new_value: object
    evaluator: str
    rationale: str
    changed_at: str = field(default_factory=_utc_now)


@dataclass
class CandidateCompetencyMatrix:
    candidate_id: str
    candidate_name: str
    job_id: str
    role_title: str
    matrix_version: int = 1
    status: str = "pre_interview"
    created_at: str = field(default_factory=_utc_now)
    updated_at: str = field(default_factory=_utc_now)
    finalized_at: str = ""
    finalized_by: str = ""
    competencies: list[CompetencyAssessment] = field(default_factory=list)
    audit_history: list[CompetencyAuditEntry] = field(default_factory=list)

    def active_competencies(self) -> list[CompetencyAssessment]:
        return [item for item in self.competencies if item.is_active]

    def to_dict(self) -> dict:
        return asdict(self)
