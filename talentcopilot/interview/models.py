from dataclasses import dataclass, field
from typing import List


@dataclass
class InterviewCompetency:
    name: str
    evidence_level: str
    confidence: int
    validate_in_interview: bool
    rationale: str = ""


@dataclass
class InterviewQuestion:
    competency: str
    question: str
    objective: str
    expected_evidence: List[str] = field(default_factory=list)
    positive_signals: List[str] = field(default_factory=list)
    warning_signals: List[str] = field(default_factory=list)
    follow_ups: List[str] = field(default_factory=list)


@dataclass
class InterviewSection:
    title: str
    duration_minutes: int
    objective: str


@dataclass
class InterviewPlan:
    total_minutes: int
    sections: List[InterviewSection] = field(default_factory=list)


@dataclass
class InterviewReadiness:
    score: int
    status: str
    drivers: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)


@dataclass
class InterviewScorecardItem:
    competency: str
    suggested_score: int
    evaluation_guidance: str


@dataclass
class InterviewWorkspaceReport:
    candidate_name: str
    role_title: str
    fit_score: float
    confidence_score: int
    risk_level: str
    recommendation: str
    readiness: InterviewReadiness
    competencies: List[InterviewCompetency] = field(default_factory=list)
    plan: InterviewPlan = None
    questions: List[InterviewQuestion] = field(default_factory=list)
    scorecard: List[InterviewScorecardItem] = field(default_factory=list)
    decision_readiness: int = 0
