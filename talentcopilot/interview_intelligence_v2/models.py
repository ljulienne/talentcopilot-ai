from dataclasses import dataclass, field
from typing import List


@dataclass
class EvidenceGapItem:
    area: str
    severity: str
    detail: str
    reason: str


@dataclass
class InterviewQuestion:
    area: str
    question: str
    purpose: str
    expected_strong_answer: str
    positive_signals: List[str] = field(default_factory=list)
    red_flags: List[str] = field(default_factory=list)
    follow_ups: List[str] = field(default_factory=list)
    evaluation_criteria: List[str] = field(default_factory=list)


@dataclass
class InterviewQuestionSet:
    candidate_name: str
    role_title: str
    recommendation: str
    evidence_gaps: List[EvidenceGapItem] = field(default_factory=list)
    questions: List[InterviewQuestion] = field(default_factory=list)
    summary: str = ""
