"""Presentation model for the consolidated candidate decision workspace.

The model intentionally separates immutable pre-interview Talent Fit from
interview, compensation and final human-decision signals.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class RequirementDecisionLine:
    requirement: str
    required_level: float
    pre_interview_level: float
    post_interview_level: Optional[float]
    current_status: str
    evidence_status: str
    confidence: str
    interview_priority: str
    validation_status: str
    evidence: str = ""


@dataclass(frozen=True)
class DecisionJourneyStage:
    key: str
    label: str
    status: str
    recommendation: str
    evidence_note: str


@dataclass(frozen=True)
class CandidateDecisionWorkspaceView:
    candidate_id: str
    candidate_name: str
    role_title: str
    official_rank: int
    official_match_score: float
    confidence_score: Optional[float]
    evidence_coverage: Optional[int]
    pre_interview_recommendation: str
    interview_status: str
    interview_recommendation: str
    interview_evidence_coverage: Optional[int]
    compensation_status: str
    compensation_fit: str
    currency: str
    expected_salary: Optional[float]
    availability_date: str
    notice_period_weeks: int
    flexibility: str
    final_decision_status: str
    final_decision_recommendation: str
    final_decision_rationale: str
    final_decision_actor: str
    final_decision_timestamp: str
    requirements: tuple[RequirementDecisionLine, ...] = field(default_factory=tuple)
    strengths: tuple[str, ...] = field(default_factory=tuple)
    risks: tuple[str, ...] = field(default_factory=tuple)
    interview_priorities: tuple[str, ...] = field(default_factory=tuple)
    journey: tuple[DecisionJourneyStage, ...] = field(default_factory=tuple)
    decision_history: tuple[dict, ...] = field(default_factory=tuple)

    @property
    def has_post_interview_evidence(self) -> bool:
        return self.interview_status in {"Completed", "In progress"}

    @property
    def has_final_decision(self) -> bool:
        return self.final_decision_status == "Recorded"
