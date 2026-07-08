from dataclasses import dataclass, field
from typing import List


@dataclass
class RecommendationReason:
    area: str
    detail: str
    impact: str


@dataclass
class RecommendationAction:
    title: str
    owner: str
    priority: str


@dataclass
class RecommendationIntelligenceReport:
    candidate_name: str
    recommendation: str
    category: str
    rationale: str
    confidence_level: str
    reasons: List[RecommendationReason] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    next_actions: List[RecommendationAction] = field(default_factory=list)
