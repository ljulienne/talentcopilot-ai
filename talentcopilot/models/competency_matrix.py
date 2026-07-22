from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional


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

    def effective_level(self) -> float:
        if self.consolidated_level is not None:
            return float(self.consolidated_level)
        if self.interviewer_level is not None:
            return float(self.interviewer_level)
        return float(self.ai_estimated_level)


@dataclass
class CompetencyAuditEntry:
    competency_id: str
    field_name: str
    previous_value: object
    new_value: object
    evaluator: str
    rationale: str
    changed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class CandidateCompetencyMatrix:
    candidate_id: str
    candidate_name: str
    job_id: str
    role_title: str
    matrix_version: int = 1
    status: str = "pre_interview"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    competencies: list[CompetencyAssessment] = field(default_factory=list)
    audit_history: list[CompetencyAuditEntry] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)
