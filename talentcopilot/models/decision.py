
from dataclasses import dataclass, field
from enum import Enum
from typing import List


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
class DecisionConcern:
    title: str
    severity: str
    explanation: str
    mitigation: str = ""


@dataclass
class DecisionReport:
    candidate_name: str
    role_title: str
    recommendation: HiringRecommendation
    decision_score: float
    confidence: DecisionConfidence
    human_validation: HumanValidationLevel
    executive_summary: str
    concerns: List[DecisionConcern] = field(default_factory=list)
    interview_focus: List[str] = field(default_factory=list)
    missing_information: List[str] = field(default_factory=list)
