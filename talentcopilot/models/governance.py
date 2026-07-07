from dataclasses import dataclass, field
from typing import List

from talentcopilot.models.confidence import CandidateConfidenceSummary
from talentcopilot.models.risk import CandidateRiskSummary
from talentcopilot.models.uncertainty import CandidateUncertaintySummary


@dataclass
class EvidenceQualityAssessment:
    competency: str
    quality_score: float
    evidence_count: int
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    explanation: str = ""

    @property
    def quality_level(self) -> str:
        if self.quality_score >= 85:
            return "Excellent"
        if self.quality_score >= 70:
            return "Good"
        if self.quality_score >= 50:
            return "Moderate"
        return "Weak"


@dataclass
class EvidenceQualitySummary:
    overall_quality_score: float
    assessments: List[EvidenceQualityAssessment] = field(default_factory=list)
    explanation: str = ""

    @property
    def quality_level(self) -> str:
        if self.overall_quality_score >= 85:
            return "Excellent"
        if self.overall_quality_score >= 70:
            return "Good"
        if self.overall_quality_score >= 50:
            return "Moderate"
        return "Weak"


@dataclass
class AIDecisionCard:
    candidate_name: str
    role_title: str
    match_score: float
    decision: str
    confidence_score: float
    evidence_quality_score: float
    risk_level: str
    uncertainty_level: str
    human_validation: str
    executive_summary: str
    strengths: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    missing_information: List[str] = field(default_factory=list)
    interview_focus: List[str] = field(default_factory=list)


@dataclass
class GovernanceReport:
    decision_card: AIDecisionCard
    confidence: CandidateConfidenceSummary
    evidence_quality: EvidenceQualitySummary
    risk: CandidateRiskSummary
    uncertainty: CandidateUncertaintySummary
    explainability_notes: List[str] = field(default_factory=list)
