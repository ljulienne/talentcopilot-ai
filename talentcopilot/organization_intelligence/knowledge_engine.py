from __future__ import annotations

from collections import defaultdict

from .models import EmployeeRecord, KnowledgeDiagnostic, SkillRisk


class KnowledgeConcentrationEngine:
    """Explainable rules-based foundation for knowledge concentration diagnostics."""

    def analyze(self, employees: list[EmployeeRecord]) -> KnowledgeDiagnostic:
        if not employees:
            raise ValueError("At least one employee is required.")

        holders: dict[str, list[EmployeeRecord]] = defaultdict(list)
        backups: dict[str, list[str]] = defaultdict(list)
        critical: set[str] = set()

        for employee in employees:
            for skill in employee.skills:
                normalized = skill.strip()
                if normalized:
                    holders[normalized.casefold()].append(employee)
            for skill in employee.critical_skills:
                critical.add(skill.strip().casefold())
            for skill in employee.backup_for:
                backups[skill.strip().casefold()].append(employee.name)

        risks: list[SkillRisk] = []
        for key, skill_holders in holders.items():
            display = self._display_skill(skill_holders, key)
            is_critical = key in critical
            skill_backups = sorted(set(backups.get(key, [])))
            reasons: list[str] = []
            score = 0

            count = len(skill_holders)
            if count == 1:
                score += 55
                reasons.append("Only one identified holder")
            elif count == 2:
                score += 35
                reasons.append("Only two identified holders")
            elif count <= 4:
                score += 15
                reasons.append("Limited holder coverage")

            if is_critical:
                score += 20
                reasons.append("Marked as business-critical")

            if not skill_backups:
                score += 12
                reasons.append("No explicit backup identified")

            if any(e.retirement_risk for e in skill_holders):
                score += 10
                reasons.append("At least one holder has a near-term retirement risk")

            if all(e.documentation_level in {"", "unknown", "low", "none"} for e in skill_holders):
                score += 8
                reasons.append("Documentation coverage is low or unknown")

            departments = sorted({e.department for e in skill_holders})
            if len(departments) == 1 and count <= 3:
                score += 5
                reasons.append("Knowledge is concentrated in one department")

            score = min(100, score)
            level = "High" if score >= 70 else "Medium" if score >= 40 else "Low"
            risks.append(
                SkillRisk(
                    skill=display,
                    holders=sorted(e.name for e in skill_holders),
                    departments=departments,
                    backups=skill_backups,
                    critical=is_critical,
                    risk_score=score,
                    risk_level=level,
                    reasons=reasons or ["Coverage appears sufficiently distributed"],
                    recommendations=self._recommendations(display, score, skill_backups, count),
                )
            )

        risks.sort(key=lambda x: (-x.risk_score, x.skill.casefold()))
        high = sum(r.risk_level == "High" for r in risks)
        medium = sum(r.risk_level == "Medium" for r in risks)
        low = sum(r.risk_level == "Low" for r in risks)
        overall = round(sum(r.risk_score for r in risks) / len(risks)) if risks else 0
        summary = self._summary(len(employees), len(risks), high, risks)
        return KnowledgeDiagnostic(len(employees), len(risks), high, medium, low, overall, summary, risks)

    @staticmethod
    def _display_skill(skill_holders: list[EmployeeRecord], key: str) -> str:
        for employee in skill_holders:
            for skill in employee.skills:
                if skill.casefold() == key:
                    return skill
        return key.title()

    @staticmethod
    def _recommendations(skill: str, score: int, backups: list[str], holder_count: int) -> list[str]:
        actions: list[str] = []
        if holder_count <= 2:
            actions.append(f"Create a structured knowledge-transfer plan for {skill}.")
        if not backups:
            actions.append(f"Nominate and train at least one backup for {skill}.")
        if score >= 70:
            actions.append("Document critical procedures and validate continuity within 90 days.")
        if score < 40:
            actions.append("Maintain current coverage and review it during the next workforce cycle.")
        return actions

    @staticmethod
    def _summary(employee_count: int, skill_count: int, high: int, risks: list[SkillRisk]) -> str:
        if not risks:
            return f"{employee_count} employees were analyzed, but no skills were available for diagnosis."
        top = risks[0]
        return (
            f"{employee_count} employees and {skill_count} skills were analyzed. "
            f"{high} skill(s) present a high knowledge-concentration risk. "
            f"The highest-priority exposure is {top.skill} with a risk score of {top.risk_score}/100."
        )
