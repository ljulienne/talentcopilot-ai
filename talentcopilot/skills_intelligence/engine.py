from __future__ import annotations

from collections import defaultdict
from hashlib import sha1

from talentcopilot.intelligence_core.models import (
    DecisionReadiness,
    Evidence,
    OrganizationInsight,
    Recommendation,
    Severity,
)
from talentcopilot.organization_intelligence.models import EmployeeRecord

from .models import DepartmentSkillCoverage, SkillProfile, SkillsIntelligenceReport
from .taxonomy import SkillsTaxonomy


class SkillsIntelligenceEngine:
    """Explainable skills portfolio, rarity and strategic-gap analysis."""

    def __init__(self, taxonomy: SkillsTaxonomy | None = None):
        self.taxonomy = taxonomy or SkillsTaxonomy()

    def analyze(
        self,
        employees: list[EmployeeRecord],
        strategic_skills: list[str] | tuple[str, ...] | None = None,
    ) -> SkillsIntelligenceReport:
        if not employees:
            raise ValueError("At least one employee is required.")

        strategic = {
            self.taxonomy.canonicalize(item)
            for item in (strategic_skills or [])
            if self.taxonomy.canonicalize(item)
        }
        holder_map: dict[str, set[str]] = defaultdict(set)
        department_map: dict[str, set[str]] = defaultdict(set)
        alias_map: dict[str, set[str]] = defaultdict(set)
        department_employees: dict[str, set[str]] = defaultdict(set)
        department_skills: dict[str, set[str]] = defaultdict(set)

        for employee in employees:
            department = employee.department or "Unknown"
            department_employees[department].add(employee.name)
            for raw_skill in employee.skills:
                canonical = self.taxonomy.canonicalize(raw_skill)
                if not canonical:
                    continue
                holder_map[canonical].add(employee.name)
                department_map[canonical].add(department)
                alias_map[canonical].add(raw_skill.strip())
                department_skills[department].add(canonical)

        all_skills = sorted(set(holder_map) | strategic, key=str.casefold)
        profiles: list[SkillProfile] = []
        missing: list[str] = []

        for skill in all_skills:
            holders = sorted(holder_map.get(skill, set()))
            departments = sorted(department_map.get(skill, set()))
            count = len(holders)
            department_count = len(departments)
            is_strategic = skill in strategic
            rarity_score = self._rarity_score(count, department_count, len(employees), is_strategic)
            coverage = self._coverage_level(count, department_count)
            gap_status = "Missing" if count == 0 else "At risk" if rarity_score >= 70 else "Covered"
            if count == 0:
                missing.append(skill)
            profiles.append(
                SkillProfile(
                    canonical_name=skill,
                    category=self.taxonomy.category_for(skill),
                    aliases=tuple(sorted(alias_map.get(skill, {skill}), key=str.casefold)),
                    holders=tuple(holders),
                    departments=tuple(departments),
                    holder_count=count,
                    department_count=department_count,
                    rarity_score=rarity_score,
                    coverage_level=coverage,
                    strategic=is_strategic,
                    gap_status=gap_status,
                    recommendations=tuple(self._recommendations(skill, count, department_count, is_strategic)),
                )
            )

        profiles.sort(key=lambda item: (-int(item.strategic), -item.rarity_score, item.canonical_name.casefold()))
        department_reports = self._department_reports(
            department_employees,
            department_skills,
            strategic,
        )
        critical_count = sum(item.rarity_score >= 70 for item in profiles)
        health = self._health_score(profiles, strategic)
        summary = self._summary(len(employees), profiles, strategic, missing, health)
        insights = tuple(self._insights(profiles, missing, health))

        return SkillsIntelligenceReport(
            employee_count=len(employees),
            unique_skill_count=len(holder_map),
            strategic_skill_count=len(strategic),
            missing_strategic_count=len(missing),
            critical_skill_count=critical_count,
            portfolio_health_score=health,
            executive_summary=summary,
            skills=tuple(profiles),
            departments=tuple(department_reports),
            missing_strategic_skills=tuple(missing),
            insights=insights,
        )

    @staticmethod
    def _rarity_score(holder_count: int, department_count: int, employee_count: int, strategic: bool) -> int:
        if holder_count == 0:
            score = 100
        elif holder_count == 1:
            score = 88
        elif holder_count == 2:
            score = 70
        elif holder_count <= max(3, round(employee_count * 0.08)):
            score = 48
        else:
            score = 20
        if department_count == 1 and holder_count > 0:
            score += 8
        if strategic:
            score += 8
        return min(100, score)

    @staticmethod
    def _coverage_level(holder_count: int, department_count: int) -> str:
        if holder_count == 0:
            return "Absent"
        if holder_count <= 2 or department_count <= 1:
            return "Fragile"
        if holder_count <= 5 or department_count <= 2:
            return "Developing"
        return "Distributed"

    @staticmethod
    def _recommendations(skill: str, holder_count: int, department_count: int, strategic: bool) -> list[str]:
        if holder_count == 0:
            return [
                f"Acquire or develop {skill} through targeted hiring, training or external partnership.",
                f"Assign an accountable owner for the {skill} capability roadmap.",
            ]
        recommendations: list[str] = []
        if holder_count <= 2:
            recommendations.append(f"Create at least two additional validated holders for {skill}.")
        if department_count <= 1:
            recommendations.append(f"Expand {skill} beyond its current department through mobility or cross-training.")
        if strategic:
            recommendations.append(f"Define proficiency levels and a 12-month development plan for strategic skill {skill}.")
        if not recommendations:
            recommendations.append(f"Maintain {skill} coverage and reassess during the next workforce planning cycle.")
        return recommendations

    @staticmethod
    def _health_score(profiles: list[SkillProfile], strategic: set[str]) -> int:
        considered = [item for item in profiles if item.strategic] or profiles
        if not considered:
            return 0
        exposure = sum(item.rarity_score for item in considered) / len(considered)
        return max(0, min(100, round(100 - exposure)))

    @staticmethod
    def _department_reports(
        department_employees: dict[str, set[str]],
        department_skills: dict[str, set[str]],
        strategic: set[str],
    ) -> list[DepartmentSkillCoverage]:
        reports = []
        for department in sorted(department_employees, key=str.casefold):
            skills = department_skills.get(department, set())
            reports.append(
                DepartmentSkillCoverage(
                    department=department,
                    employee_count=len(department_employees[department]),
                    unique_skill_count=len(skills),
                    strategic_skill_count=len(skills & strategic),
                    missing_strategic_skills=tuple(sorted(strategic - skills, key=str.casefold)),
                )
            )
        return reports

    @staticmethod
    def _summary(
        employee_count: int,
        profiles: list[SkillProfile],
        strategic: set[str],
        missing: list[str],
        health: int,
    ) -> str:
        critical = [item for item in profiles if item.rarity_score >= 70]
        top = critical[0].canonical_name if critical else "none"
        return (
            f"{employee_count} employees and {len(profiles)} normalized skills were analyzed. "
            f"Skills portfolio health is {health}/100. "
            f"{len(critical)} skill(s) have critical or high rarity exposure, and "
            f"{len(missing)} of {len(strategic)} strategic skill(s) are currently missing. "
            f"The highest-priority capability is {top}."
        )

    def _insights(self, profiles: list[SkillProfile], missing: list[str], health: int) -> list[OrganizationInsight]:
        insights: list[OrganizationInsight] = []
        for item in profiles[:8]:
            if item.rarity_score < 70:
                continue
            severity = Severity.CRITICAL if item.rarity_score >= 90 else Severity.HIGH
            current = (
                f"{item.canonical_name} has {item.holder_count} identified holder(s) across "
                f"{item.department_count} department(s)."
            )
            evidence = (
                Evidence("Holder coverage", f"{item.holder_count} identified holder(s)", strength=0.95),
                Evidence("Department coverage", f"{item.department_count} department(s)", strength=0.85),
                Evidence("Strategic status", "Strategic capability" if item.strategic else "Observed capability", strength=0.8),
            )
            recommendations = tuple(
                Recommendation(action, "High", "90 days", "Improved capability resilience")
                for action in item.recommendations[:2]
            )
            identifier = sha1(item.canonical_name.encode("utf-8")).hexdigest()[:10]
            insights.append(
                OrganizationInsight(
                    insight_id=f"skills-{identifier}",
                    title=f"Skills exposure: {item.canonical_name}",
                    category="Skills",
                    severity=severity,
                    confidence=0.9 if item.holder_count <= 2 else 0.82,
                    current_situation=current,
                    business_impact=(
                        "Strategic delivery, internal mobility and business continuity may be constrained by limited capability coverage."
                    ),
                    evidence=evidence,
                    recommendations=recommendations,
                    decision_readiness=DecisionReadiness.READY,
                )
            )

        if missing:
            missing_text = ", ".join(missing[:5])
            insights.insert(
                0,
                OrganizationInsight(
                    insight_id="skills-strategic-gaps",
                    title="Strategic skills are missing",
                    category="Skills",
                    severity=Severity.CRITICAL,
                    confidence=0.98,
                    current_situation=f"The organization has no identified holder for: {missing_text}.",
                    business_impact="Priority initiatives may be delayed or become dependent on external suppliers.",
                    evidence=(Evidence("Strategic gap", missing_text, strength=1.0),),
                    recommendations=(
                        Recommendation("Create a build, buy or borrow plan for each missing strategic skill.", "Critical", "30 days", "Close strategic capability gaps"),
                    ),
                    decision_readiness=DecisionReadiness.READY,
                ),
            )
        return insights
