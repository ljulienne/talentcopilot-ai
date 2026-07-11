from __future__ import annotations

from dataclasses import dataclass, field

from talentcopilot.intelligence_core.models import OrganizationInsight


@dataclass(frozen=True)
class SkillProfile:
    canonical_name: str
    category: str
    aliases: tuple[str, ...]
    holders: tuple[str, ...]
    departments: tuple[str, ...]
    holder_count: int
    department_count: int
    rarity_score: int
    coverage_level: str
    strategic: bool
    gap_status: str
    recommendations: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class DepartmentSkillCoverage:
    department: str
    employee_count: int
    unique_skill_count: int
    strategic_skill_count: int
    missing_strategic_skills: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class SkillsIntelligenceReport:
    employee_count: int
    unique_skill_count: int
    strategic_skill_count: int
    missing_strategic_count: int
    critical_skill_count: int
    portfolio_health_score: int
    executive_summary: str
    skills: tuple[SkillProfile, ...]
    departments: tuple[DepartmentSkillCoverage, ...]
    missing_strategic_skills: tuple[str, ...]
    insights: tuple[OrganizationInsight, ...] = field(default_factory=tuple)
