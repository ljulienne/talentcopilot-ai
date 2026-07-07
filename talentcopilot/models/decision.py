from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class HiringRecommendation(str, Enum):
    STRONG_HIRE = "Strong Hire"
    HIRE = "Hire / Continue Process"
    REVIEW = "Review Carefully"
    HOLD = "Hold"
    NOT_RECOMMENDED = "Not Recommended"


class DecisionConfidence(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class HumanValidationLevel(str, Enum):
    STANDARD_REVIEW = "Standard Review"
    RECOMMENDED = "Recommended"
    STRONGLY_RECOMMENDED = "Strongly Recommended"


@dataclass
class DecisionSignal:
    name: str
    score: float
    weight: float
    explanation: str

    @property
    def weighted_score(self) -> float:
        return round(self.score * self.weight, 2)


@dataclass
class DecisionConcern:
    title: str
    severity: str
    explanation: str
    mitigation: str = ""


@dataclass
class DecisionStrength:
    title: str
    explanation: str


@dataclass
class DecisionReport:
    candidate_name: str
    role_title: str
    recommendation: HiringRecommendation
    decision_score: float
    confidence: DecisionConfidence
    human_validation: HumanValidationLevel
    executive_summary: str
    signals: List[DecisionSignal] = field(default_factory=list)
    strengths: List[DecisionStrength] = field(default_factory=list)
    concerns: List[DecisionConcern] = field(default_factory=list)
    interview_focus: List[str] = field(default_factory=list)
    missing_information: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)

    @property
    def is_positive_recommendation(self) -> bool:
        return self.recommendation in {
            HiringRecommendation.STRONG_HIRE,
            HiringRecommendation.HIRE,
        }

    @property
    def concern_count(self) -> int:
        return len(self.concerns)
