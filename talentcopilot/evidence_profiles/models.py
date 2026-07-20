from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class EvidenceItem:
    evidence_id: str
    category: str
    label: str
    normalized_value: str
    excerpt: str
    source_kind: str
    confidence: int = 80
    metadata: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class CareerStep:
    title: str
    organization: str = ""
    start_year: int | None = None
    end_year: int | None = None
    evidence_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CandidateEvidenceProfile:
    candidate_name: str
    skills: List[str] = field(default_factory=list)
    technologies: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    responsibilities: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)
    career_steps: List[CareerStep] = field(default_factory=list)
    evidence: List[EvidenceItem] = field(default_factory=list)
    source_text_hash: str = ""
    profile_version: str = "candidate-evidence-profile-v1.0"

    def evidence_for(self, category: str) -> List[EvidenceItem]:
        key = str(category or "").casefold()
        return [item for item in self.evidence if item.category.casefold() == key]

    def to_dict(self) -> dict:
        return {
            "candidate_name": self.candidate_name,
            "skills": list(self.skills),
            "technologies": list(self.technologies),
            "certifications": list(self.certifications),
            "languages": list(self.languages),
            "responsibilities": list(self.responsibilities),
            "achievements": list(self.achievements),
            "career_steps": [item.to_dict() for item in self.career_steps],
            "evidence": [item.to_dict() for item in self.evidence],
            "source_text_hash": self.source_text_hash,
            "profile_version": self.profile_version,
        }


@dataclass
class MissionEvidenceProfile:
    role_title: str
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    technologies: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    responsibilities: List[str] = field(default_factory=list)
    critical_criteria: List[str] = field(default_factory=list)
    minimum_years_experience: int = 0
    seniority: str = "unspecified"
    evidence: List[EvidenceItem] = field(default_factory=list)
    source_text_hash: str = ""
    profile_version: str = "mission-evidence-profile-v1.0"

    def evidence_for(self, category: str) -> List[EvidenceItem]:
        key = str(category or "").casefold()
        return [item for item in self.evidence if item.category.casefold() == key]

    def to_dict(self) -> dict:
        return {
            "role_title": self.role_title,
            "required_skills": list(self.required_skills),
            "preferred_skills": list(self.preferred_skills),
            "technologies": list(self.technologies),
            "languages": list(self.languages),
            "certifications": list(self.certifications),
            "responsibilities": list(self.responsibilities),
            "critical_criteria": list(self.critical_criteria),
            "minimum_years_experience": self.minimum_years_experience,
            "seniority": self.seniority,
            "evidence": [item.to_dict() for item in self.evidence],
            "source_text_hash": self.source_text_hash,
            "profile_version": self.profile_version,
        }
