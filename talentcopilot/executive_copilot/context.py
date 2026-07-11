from __future__ import annotations

from dataclasses import dataclass

from talentcopilot.intelligence_core.adapters import KnowledgeInsightAdapter
from talentcopilot.intelligence_core.engine import DecisionEngine
from talentcopilot.intelligence_core.models import DecisionQueue, OrganizationInsight
from talentcopilot.organization_intelligence.collaboration_engine import CollaborationIntelligenceEngine
from talentcopilot.organization_intelligence.graph import OrganizationGraphBuilder
from talentcopilot.organization_intelligence.graph_engine import OrganizationGraphEngine
from talentcopilot.organization_intelligence.knowledge_engine import KnowledgeConcentrationEngine
from talentcopilot.organization_intelligence.models import EmployeeRecord
from talentcopilot.skills_intelligence import SkillsIntelligenceEngine
from talentcopilot.workforce_intelligence import WorkforceScenarioEngine


DEFAULT_STRATEGIC_SKILLS: tuple[str, ...] = (
    "SAP Payroll",
    "HRIS Architecture",
    "API Integration",
    "Data Engineering",
    "Change Management",
)


@dataclass(frozen=True)
class ExecutiveCopilotContext:
    employees: tuple[EmployeeRecord, ...]
    insights: tuple[OrganizationInsight, ...]
    decision_queue: DecisionQueue
    source_counts: dict[str, int]


class ExecutiveCopilotContextBuilder:
    """Builds a deterministic executive context from organization metadata."""

    def build(
        self,
        employees: list[EmployeeRecord],
        *,
        strategic_skills: tuple[str, ...] = DEFAULT_STRATEGIC_SKILLS,
    ) -> ExecutiveCopilotContext:
        if not employees:
            raise ValueError("At least one employee is required.")

        knowledge = KnowledgeConcentrationEngine().analyze(employees)
        knowledge_insights = list(KnowledgeInsightAdapter().from_diagnostic(knowledge))

        graph = OrganizationGraphBuilder().build(employees)
        graph_insights = list(OrganizationGraphEngine().analyze(graph).insights or [])
        collaboration_insights = list(
            CollaborationIntelligenceEngine().analyze(graph).insights or []
        )

        skills_report = SkillsIntelligenceEngine().analyze(
            employees,
            strategic_skills=strategic_skills,
        )
        skills_insights = list(skills_report.insights or [])

        workforce_insights = self._highest_risk_workforce_insights(employees)

        insights = self._deduplicate(
            [
                *knowledge_insights,
                *graph_insights,
                *collaboration_insights,
                *skills_insights,
                *workforce_insights,
            ]
        )
        queue = DecisionEngine().generate(insights)
        source_counts: dict[str, int] = {}
        for item in insights:
            source_counts[item.category] = source_counts.get(item.category, 0) + 1

        return ExecutiveCopilotContext(
            employees=tuple(employees),
            insights=tuple(insights),
            decision_queue=queue,
            source_counts=source_counts,
        )

    @staticmethod
    def _highest_risk_workforce_insights(
        employees: list[EmployeeRecord],
    ) -> list[OrganizationInsight]:
        engine = WorkforceScenarioEngine()
        reports = [
            engine.analyze_departure(employees, employee.employee_id)
            for employee in employees
        ]
        if not reports:
            return []
        highest = max(reports, key=lambda report: report.impact.risk_score)
        return list(highest.impact.insights or [])

    @staticmethod
    def _deduplicate(
        insights: list[OrganizationInsight],
    ) -> list[OrganizationInsight]:
        unique: dict[str, OrganizationInsight] = {}
        for item in insights:
            unique.setdefault(item.insight_id, item)
        return list(unique.values())
