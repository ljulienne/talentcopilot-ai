from __future__ import annotations

from dataclasses import dataclass

from talentcopilot.intelligence_core.engine import InsightEngine
from talentcopilot.intelligence_core.models import OrganizationInsight

from .graph import OrganizationGraph


@dataclass(frozen=True)
class PersonNetworkMetric:
    employee_id: str
    name: str
    department: str
    degree: int
    weighted_degree: float
    cross_department_links: int


@dataclass(frozen=True)
class DepartmentNetworkMetric:
    department: str
    employee_count: int
    internal_links: int
    external_links: int
    connectivity_score: int


@dataclass(frozen=True)
class OrganizationGraphDiagnostic:
    employee_count: int
    edge_count: int
    department_count: int
    connector_count: int
    isolated_department_count: int
    people: tuple[PersonNetworkMetric, ...]
    departments: tuple[DepartmentNetworkMetric, ...]
    insights: tuple[OrganizationInsight, ...]


class OrganizationGraphEngine:
    def analyze(self, graph: OrganizationGraph) -> OrganizationGraphDiagnostic:
        people = self._people_metrics(graph)
        departments = self._department_metrics(graph)
        insights = self._insights(graph, people, departments)
        connector_threshold = max(2, round((len(graph.employees) - 1) * 0.4))
        return OrganizationGraphDiagnostic(
            employee_count=len(graph.employees),
            edge_count=len(graph.edges),
            department_count=len(departments),
            connector_count=sum(item.degree >= connector_threshold for item in people),
            isolated_department_count=sum(item.external_links == 0 for item in departments),
            people=tuple(people),
            departments=tuple(departments),
            insights=tuple(insights),
        )

    def _people_metrics(self, graph: OrganizationGraph) -> list[PersonNetworkMetric]:
        result = []
        for employee_id, employee in graph.employees.items():
            cross = 0
            for neighbor_id in graph.neighbors(employee_id):
                if graph.employees[neighbor_id].department != employee.department:
                    cross += 1
            result.append(PersonNetworkMetric(
                employee_id=employee_id,
                name=employee.name,
                department=employee.department,
                degree=graph.degree(employee_id),
                weighted_degree=graph.weighted_degree(employee_id),
                cross_department_links=cross,
            ))
        return sorted(result, key=lambda item: (-item.degree, -item.cross_department_links, item.name.casefold()))

    def _department_metrics(self, graph: OrganizationGraph) -> list[DepartmentNetworkMetric]:
        departments = sorted({employee.department for employee in graph.employees.values()})
        metrics = []
        for department in departments:
            member_ids = {employee.employee_id for employee in graph.employees.values() if employee.department == department}
            internal = 0
            external = 0
            for edge in graph.edges:
                left_in = edge.source in member_ids
                right_in = edge.target in member_ids
                if left_in and right_in:
                    internal += 1
                elif left_in or right_in:
                    external += 1
            possible_external = max(1, len(member_ids) * (len(graph.employees) - len(member_ids)))
            score = min(100, round((external / possible_external) * 100 * 3))
            metrics.append(DepartmentNetworkMetric(
                department=department,
                employee_count=len(member_ids),
                internal_links=internal,
                external_links=external,
                connectivity_score=score,
            ))
        return sorted(metrics, key=lambda item: (item.connectivity_score, item.department.casefold()))

    def _insights(self, graph, people, departments) -> list[OrganizationInsight]:
        builder = InsightEngine()
        insights: list[OrganizationInsight] = []

        isolated = [item for item in departments if item.external_links == 0]
        for item in isolated:
            insights.append(builder.build(
                insight_id=f"department-isolation-{item.department.casefold().replace(' ', '-')}",
                title=f"{item.department} appears organizationally isolated",
                category="Collaboration",
                severity="High",
                confidence=0.86,
                current_situation=f"No cross-department relationship was inferred for {item.department} from the uploaded data.",
                business_impact="Isolation can slow decisions, reduce knowledge exchange and create avoidable delivery dependencies.",
                evidence=[
                    {"label":"External links", "detail":"0 inferred cross-department links", "strength":0.95},
                    {"label":"Team size", "detail":f"{item.employee_count} employee(s) analyzed", "strength":0.75},
                ],
                recommendations=[
                    {"action":f"Create a cross-functional working rhythm involving {item.department}.", "priority":"High", "timeframe":"30 days", "business_value":"Increase collaboration and reduce silo risk."},
                ],
            ))

        if people:
            top = people[0]
            average = sum(item.degree for item in people) / len(people)
            if top.degree >= max(3, average * 1.7):
                insights.append(builder.build(
                    insight_id=f"connector-dependency-{top.employee_id}",
                    title=f"The organization depends heavily on {top.name} as a connector",
                    category="Network dependency",
                    severity="High",
                    confidence=0.9,
                    current_situation=f"{top.name} has {top.degree} inferred relationships, including {top.cross_department_links} across departments.",
                    business_impact="A single connector can become a bottleneck and a continuity risk if knowledge and relationships are not distributed.",
                    evidence=[
                        {"label":"Network degree", "detail":str(top.degree), "strength":0.9},
                        {"label":"Cross-department links", "detail":str(top.cross_department_links), "strength":0.9},
                    ],
                    recommendations=[
                        {"action":f"Create at least one secondary connector for the relationships currently concentrated on {top.name}.", "priority":"High", "timeframe":"60 days", "business_value":"Improve network resilience."},
                        {"action":"Document critical stakeholder relationships and recurring collaboration paths.", "priority":"Medium", "timeframe":"90 days", "business_value":"Reduce dependency on informal knowledge."},
                    ],
                ))

        department_links = graph.department_links()
        if department_links:
            weakest_pair, count = min(department_links.items(), key=lambda item: item[1])
            insights.append(builder.build(
                insight_id="weak-cross-department-link",
                title=f"Weak collaboration signal between {weakest_pair[0]} and {weakest_pair[1]}",
                category="Collaboration",
                severity="Medium",
                confidence=0.72,
                current_situation=f"Only {count} inferred relationship(s) connect these departments.",
                business_impact="Low connectivity may delay cross-functional work when the departments share processes or transformation goals.",
                evidence=[{"label":"Inferred links", "detail":str(count), "strength":0.75}],
                recommendations=[{"action":f"Validate whether {weakest_pair[0]} and {weakest_pair[1]} share critical processes, then establish a named liaison if needed.", "priority":"Medium", "timeframe":"60 days", "business_value":"Reduce cross-functional friction."}],
            ))

        return insights
