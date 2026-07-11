from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from talentcopilot.executive_reasoning import ExecutiveAnswer


class QuestionDomain(str, Enum):
    OVERVIEW = "Executive overview"
    RISK = "Risk"
    SKILLS = "Skills"
    WORKFORCE = "Workforce"
    SUCCESSION = "Succession"
    COLLABORATION = "Collaboration"
    RECRUITMENT = "Recruitment"


@dataclass(frozen=True)
class ExecutiveQuestion:
    question_id: str
    title: str
    domain: QuestionDomain
    description: str
    required_engines: tuple[str, ...] = field(default_factory=tuple)
    keywords: tuple[str, ...] = field(default_factory=tuple)
    follow_up_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.question_id.strip():
            raise ValueError("question_id is required.")
        if not self.title.strip():
            raise ValueError("Question title is required.")


@dataclass(frozen=True)
class RoutedQuestion:
    question: ExecutiveQuestion
    matched_text: str
    match_score: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.match_score <= 1.0:
            raise ValueError("match_score must be between 0 and 1.")


@dataclass(frozen=True)
class CopilotResponse:
    question: ExecutiveQuestion
    answer: ExecutiveAnswer
    executive_health_score: int
    data_readiness: str
    suggested_questions: tuple[ExecutiveQuestion, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not 0 <= self.executive_health_score <= 100:
            raise ValueError("executive_health_score must be between 0 and 100.")
