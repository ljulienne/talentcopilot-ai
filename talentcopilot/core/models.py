from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class Evidence:
    text: str
    source: str = "CV"
    linked_competency: Optional[str] = None
    confidence: int = 70


@dataclass
class Competency:
    name: str
    category: str = "General"
    level: str = "Unknown"
    confidence: int = 70
    evidence: List[Evidence] = field(default_factory=list)


@dataclass
class JobRequirement:
    name: str
    category: str = "General"
    importance: str = "Medium"
    expected_level: str = "Intermediate"
    weight: float = 10.0


@dataclass
class CandidateCapability:
    name: str
    category: str = "General"
    detected_level: str = "Unknown"
    confidence: int = 70
    evidence: List[Evidence] = field(default_factory=list)


@dataclass
class InterviewQuestion:
    question: str
    purpose: str
    linked_competency: Optional[str] = None
    priority: str = "Medium"


@dataclass
class Gap:
    competency: str
    severity: str
    explanation: str
    recommendation: str


@dataclass
class Candidate:
    name: str
    current_role: str = ""
    experiences: List[str] = field(default_factory=list)
    education: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    capabilities: List[CandidateCapability] = field(default_factory=list)


@dataclass
class Job:
    title: str
    description: str
    requirements: List[JobRequirement] = field(default_factory=list)


@dataclass
class MatchDetail:
    requirement: JobRequirement
    capability: Optional[CandidateCapability]
    score: int
    confidence: int
    explanation: str


@dataclass
class MatchResult:
    candidate: Candidate
    job: Job
    overall_score: int
    confidence_score: int
    recommendation: str
    match_details: List[MatchDetail] = field(default_factory=list)
    gaps: List[Gap] = field(default_factory=list)
    interview_questions: List[InterviewQuestion] = field(default_factory=list)
    executive_summary: str = ""