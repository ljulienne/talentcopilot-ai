from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class StarAssessment:
    situation: bool
    task: bool
    action: bool
    result: bool
    ownership: bool
    metrics: bool
    completeness_score: int
    missing_elements: List[str] = field(default_factory=list)
    evidence_summary: str = ""


@dataclass(frozen=True)
class InterviewEvidenceRating:
    competency: str
    score: int
    evidence_confirmed: bool
    notes: str
    star: StarAssessment


@dataclass(frozen=True)
class HiringRecommendation:
    label: str
    confidence: int
    rationale: List[str] = field(default_factory=list)
    remaining_risks: List[str] = field(default_factory=list)
    next_step: str = ""


@dataclass(frozen=True)
class InterviewOutcome:
    candidate_name: str
    overall_score: float
    evidence_coverage: int
    recommendation: HiringRecommendation
    ratings: List[InterviewEvidenceRating] = field(default_factory=list)
