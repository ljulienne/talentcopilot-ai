from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha1

from talentcopilot.intelligence_core.models import (
    DecisionReadiness,
    Evidence,
    OrganizationInsight,
    Recommendation,
    Severity,
)
from talentcopilot.organization_intelligence.models import EmployeeRecord

from .models import DepartureImpact, SuccessorCandidate, WorkforceScenarioReport


class WorkforceScenarioEngine:
    """Simulates workforce continuity impact using explainable HR metadata."""

    def analyze_departure(
        self,
        employees: list[EmployeeRecord],
        employee_id: str,
    ) -> WorkforceScenarioReport:
        if not employees:
            raise ValueError("At least one employee is required.")

        subject = next((item for item in employees if item.employee_id == employee_id), None)
        if subject is None:
            raise ValueError(f"Unknown employee_id: {employee_id}")

        others = [item for item in employees if item.employee_id != employee_id]
        skill_counts = Counter(skill.strip() for item in employees for skill in item.skills if skill.strip())
        department_by_skill: dict[str, set[str]] = defaultdict(set)
        for item in employees:
            for skill in item.skills:
                if skill.strip():
                    department_by_skill[skill.strip()].add(item.department or "Unknown")

        lost_skills = tuple(dict.fromkeys(skill.strip() for skill in subject.skills if skill.strip()))
        critical = set(skill.strip() for skill in subject.critical_skills if skill.strip())
        critical_lost = tuple(skill for skill in lost_skills if skill in critical)
        unique_lost = tuple(skill for skill in lost_skills if skill_counts[skill] <= 1)

        successors = tuple(self._successors(subject, others, lost_skills, critical))
        affected_departments = tuple(
            sorted(
                {
                    department
                    for skill in lost_skills
                    for department in department_by_skill.get(skill, set())
                },
                key=str.casefold,
            )
        )

        risk_score = self._risk_score(
            lost_skill_count=len(lost_skills),
            critical_count=len(critical_lost),
            unique_count=len(unique_lost),
            retirement_risk=subject.retirement_risk,
            successor_score=successors[0].readiness_score if successors else 0,
            documentation_level=subject.documentation_level,
        )
        risk_level = self._risk_level(risk_score)
        recommendations = tuple(
            self._recommendations(subject, critical_lost, unique_lost, successors)
        )
        summary = self._summary(subject, risk_score, risk_level, critical_lost, unique_lost, successors)
        insights = tuple(
            self._insights(subject, risk_score, risk_level, critical_lost, unique_lost, successors, recommendations)
        )

        impact = DepartureImpact(
            employee_id=subject.employee_id,
            employee_name=subject.name,
            department=subject.department,
            role=subject.role,
            lost_skills=lost_skills,
            critical_lost_skills=critical_lost,
            unique_skills_lost=unique_lost,
            affected_departments=affected_departments,
            successor_candidates=successors,
            risk_score=risk_score,
            risk_level=risk_level,
            executive_summary=summary,
            recommendations=recommendations,
            insights=insights,
        )
        return WorkforceScenarioReport(
            employee_count=len(employees),
            scenario_type="Departure",
            subject_employee_id=subject.employee_id,
            subject_employee_name=subject.name,
            impact=impact,
        )

    def _successors(
        self,
        subject: EmployeeRecord,
        others: list[EmployeeRecord],
        lost_skills: tuple[str, ...],
        critical: set[str],
    ) -> list[SuccessorCandidate]:
        required = set(lost_skills)
        if not required:
            return []

        ranked: list[SuccessorCandidate] = []
        for candidate in others:
            candidate_skills = {skill.strip() for skill in candidate.skills if skill.strip()}
            matched = required & candidate_skills
            if not matched:
                continue
            missing = required - candidate_skills
            overlap = len(matched) / len(required)
            same_department_bonus = 12 if candidate.department == subject.department else 0
            critical_bonus = 12 if critical and critical.issubset(candidate_skills) else 0
            backup_bonus = 10 if any(skill in candidate.backup_for for skill in required) else 0
            readiness = min(100, round(overlap * 66 + same_department_bonus + critical_bonus + backup_bonus))
            rationale = [f"Matches {len(matched)} of {len(required)} relevant skill(s)."]
            if candidate.department == subject.department:
                rationale.append("Already works in the same department.")
            if critical and critical.issubset(candidate_skills):
                rationale.append("Covers all identified critical skills.")
            if backup_bonus:
                rationale.append("Already identified as a backup for a relevant capability.")
            ranked.append(
                SuccessorCandidate(
                    employee_id=candidate.employee_id,
                    name=candidate.name,
                    department=candidate.department,
                    role=candidate.role,
                    readiness_score=readiness,
                    matched_skills=tuple(sorted(matched, key=str.casefold)),
                    missing_skills=tuple(sorted(missing, key=str.casefold)),
                    rationale=tuple(rationale),
                )
            )
        ranked.sort(key=lambda item: (-item.readiness_score, item.name.casefold()))
        return ranked[:5]

    @staticmethod
    def _risk_score(
        *,
        lost_skill_count: int,
        critical_count: int,
        unique_count: int,
        retirement_risk: bool,
        successor_score: int,
        documentation_level: str,
    ) -> int:
        score = min(25, lost_skill_count * 4)
        score += min(30, critical_count * 15)
        score += min(30, unique_count * 18)
        if retirement_risk:
            score += 8
        if successor_score < 50:
            score += 18
        elif successor_score < 70:
            score += 10
        if documentation_level in {"low", "unknown", ""}:
            score += 10
        elif documentation_level == "medium":
            score += 4
        return min(100, score)

    @staticmethod
    def _risk_level(score: int) -> str:
        if score >= 80:
            return "Critical"
        if score >= 60:
            return "High"
        if score >= 35:
            return "Medium"
        return "Low"

    @staticmethod
    def _recommendations(
        subject: EmployeeRecord,
        critical_lost: tuple[str, ...],
        unique_lost: tuple[str, ...],
        successors: tuple[SuccessorCandidate, ...],
    ) -> list[str]:
        actions: list[str] = []
        if unique_lost:
            actions.append("Document and transfer unique knowledge before the departure occurs.")
        if critical_lost:
            actions.append("Create a formal continuity plan for the critical skills at risk.")
        if successors:
            actions.append(
                f"Assess {successors[0].name} as the first internal successor candidate and close identified skill gaps."
            )
        else:
            actions.append("Launch an internal mobility, training or external recruitment plan because no credible successor was identified.")
        if subject.documentation_level in {"low", "unknown", ""}:
            actions.append("Raise documentation quality to at least medium before transition.")
        return list(dict.fromkeys(actions))

    @staticmethod
    def _summary(
        subject: EmployeeRecord,
        risk_score: int,
        risk_level: str,
        critical_lost: tuple[str, ...],
        unique_lost: tuple[str, ...],
        successors: tuple[SuccessorCandidate, ...],
    ) -> str:
        successor_text = (
            f"The strongest internal successor is {successors[0].name} ({successors[0].readiness_score}% readiness)."
            if successors
            else "No credible internal successor was identified."
        )
        return (
            f"The departure of {subject.name} creates a {risk_level.lower()} workforce continuity risk "
            f"({risk_score}/100). {len(critical_lost)} critical skill(s) and {len(unique_lost)} unique skill(s) "
            f"would be exposed. {successor_text}"
        )

    def _insights(
        self,
        subject: EmployeeRecord,
        risk_score: int,
        risk_level: str,
        critical_lost: tuple[str, ...],
        unique_lost: tuple[str, ...],
        successors: tuple[SuccessorCandidate, ...],
        recommendations: tuple[str, ...],
    ) -> list[OrganizationInsight]:
        severity = (
            Severity.CRITICAL if risk_score >= 80 else
            Severity.HIGH if risk_score >= 60 else
            Severity.MEDIUM if risk_score >= 35 else
            Severity.LOW
        )
        identifier = sha1(subject.employee_id.encode("utf-8")).hexdigest()[:10]
        evidence = [
            Evidence("Critical skills exposed", ", ".join(critical_lost) or "None", strength=0.95),
            Evidence("Unique skills exposed", ", ".join(unique_lost) or "None", strength=0.95),
            Evidence(
                "Successor readiness",
                f"{successors[0].name}: {successors[0].readiness_score}%" if successors else "No candidate identified",
                strength=0.85,
            ),
        ]
        insight = OrganizationInsight(
            insight_id=f"workforce-departure-{identifier}",
            title=f"Departure impact: {subject.name}",
            category="Workforce",
            severity=severity,
            confidence=0.92,
            current_situation=(
                f"A departure scenario for {subject.name} ({subject.role or 'role unspecified'}) produces a "
                f"{risk_level.lower()} continuity risk score of {risk_score}/100."
            ),
            business_impact=(
                "Business continuity, delivery capacity and critical knowledge retention may be affected if the transition is not managed."
            ),
            evidence=tuple(evidence),
            recommendations=tuple(
                Recommendation(action, "High", "90 days", "Reduce workforce continuity exposure")
                for action in recommendations[:3]
            ),
            decision_readiness=DecisionReadiness.READY,
        )
        return [insight]
