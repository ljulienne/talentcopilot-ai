from dataclasses import dataclass, field
from typing import List, Optional

from talentcopilot.document_intelligence.models import DocumentSection


@dataclass
class RoleProfile:
    role_title: str
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    responsibilities: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    minimum_years_experience: int = 0
    target_salary: Optional[float] = None
    maximum_salary: Optional[float] = None
    raw_excerpt: str = ""
    language: str = "unknown"
    extraction_status: str = "OK"


@dataclass
class JobAnalysis:
    filename: str
    language: str
    cleaned_text: str
    sections: List[DocumentSection] = field(default_factory=list)
    role_profile: RoleProfile | None = None
