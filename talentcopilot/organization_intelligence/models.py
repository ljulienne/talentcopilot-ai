from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class EmployeeRecord:
    employee_id: str
    name: str
    department: str
    role: str = ""
    manager: str = ""
    skills: List[str] = field(default_factory=list)
    critical_skills: List[str] = field(default_factory=list)
    backup_for: List[str] = field(default_factory=list)
    retirement_risk: bool = False
    documentation_level: str = "unknown"


@dataclass(frozen=True)
class SkillRisk:
    skill: str
    holders: List[str]
    departments: List[str]
    backups: List[str]
    critical: bool
    risk_score: int
    risk_level: str
    reasons: List[str]
    recommendations: List[str]


@dataclass(frozen=True)
class KnowledgeDiagnostic:
    employee_count: int
    skill_count: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    overall_risk_score: int
    summary: str
    skill_risks: List[SkillRisk]
