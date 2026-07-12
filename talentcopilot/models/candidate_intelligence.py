"""Presentation models for explainable candidate intelligence.

These objects organise existing candidate workspace signals without replacing or
recalculating TalentCopilot's matching and ranking engines.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class CandidateRiskType(str, Enum):
    EVIDENCED = "Evidenced risk"
    UNKNOWN = "Unknown / validate"


@dataclass(frozen=True)
class CandidateIntelligenceRisk:
    title: str
    detail: str
    severity: str = "Medium"
    risk_type: CandidateRiskType = CandidateRiskType.EVIDENCED


@dataclass(frozen=True)
class CandidateIntelligenceSnapshot:
    candidate_name: str
    mission_fit: float
    evidence_coverage: int
    decision_confidence: int
    potential_signal: int
    recommendation: str
    recommendation_explanation: str
    strengths: tuple[str, ...] = field(default_factory=tuple)
    risks: tuple[CandidateIntelligenceRisk, ...] = field(default_factory=tuple)
    missing_evidence: tuple[str, ...] = field(default_factory=tuple)
    interview_strategy: tuple[str, ...] = field(default_factory=tuple)
    evidence_summary: str = ""
