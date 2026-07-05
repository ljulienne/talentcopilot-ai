from dataclasses import dataclass, field
from typing import List


@dataclass
class CandidateProfile:
    candidate_id: str
    name: str
    current_role: str = ""
    summary: str = ""
    skills: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
