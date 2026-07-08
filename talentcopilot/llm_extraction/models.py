from pydantic import BaseModel, Field
from typing import List, Optional


class CandidateFacts(BaseModel):
    candidate_name: str = Field(default="Unknown Candidate")
    headline: Optional[str] = None
    current_title: Optional[str] = None
    current_company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    years_experience: int = 0
    skills: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    education: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    industries: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    countries: List[str] = Field(default_factory=list)
    expected_salary: Optional[int] = None


class CandidateInsights(BaseModel):
    seniority: Optional[str] = None
    leadership_signals: List[str] = Field(default_factory=list)
    transformation_signals: List[str] = Field(default_factory=list)
    international_signals: List[str] = Field(default_factory=list)
    risk_notes: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)


class CandidateExtractionResult(BaseModel):
    facts: CandidateFacts
    insights: CandidateInsights = Field(default_factory=CandidateInsights)
    extraction_confidence: float = 0.0
    source_summary: str = ""
    extraction_status: str = "OK"


class RoleFacts(BaseModel):
    title: str = Field(default="Unknown Role")
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    required_languages: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    minimum_experience: int = 0
    responsibilities: List[str] = Field(default_factory=list)
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    location: Optional[str] = None
    remote_policy: Optional[str] = None


class RoleInsights(BaseModel):
    seniority_level: Optional[str] = None
    business_context: Optional[str] = None
    critical_requirements: List[str] = Field(default_factory=list)
    nice_to_have: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)


class RoleExtractionResult(BaseModel):
    facts: RoleFacts
    insights: RoleInsights = Field(default_factory=RoleInsights)
    extraction_confidence: float = 0.0
    source_summary: str = ""
    extraction_status: str = "OK"
