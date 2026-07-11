from __future__ import annotations

from itertools import combinations

from talentcopilot.intelligence_core.engine import InsightEngine
from talentcopilot.intelligence_core.models import OrganizationInsight

from .collaboration_models import (
    CollaborationBroker,
    CollaborationDiagnostic,
    DepartmentCollaborationMetric,
    DepartmentPairMetric,
)
from .graph import OrganizationGraph
from .graph_engine import OrganizationGraphEngine


class CollaborationIntelligenceEngine:
    """Turns an inferred organization graph into explainable collaboration diagnostics."""

    def analyze(self, graph: OrganizationGraph) -> CollaborationDiagnostic:
        graph_diagnostic = OrganizationGraphEngine().analyze(graph)
        departments = self._department_metrics(graph, graph_diagnostic.departments)
        pairs = self._department_pairs(graph)
        brokers = self._brokers(graph, graph_diagnostic.people)
        overall_score = self._overall_score(departments, pairs)
        insights = self._insights(departments, pairs, brokers, overall_score)
        recommendations = self._recommendations(departments, pairs, brokers)

        return CollaborationDiagnostic(
            employee_count=len(graph.employees),
            department_count=len(departments),
            overall_collaboration_score=overall_score,
            overall_health=self._health(overall_score),
            silo_count=sum(item.risk_level == "High" for item in departments),
            broker_count=len(brokers),
            weak_pair_count=sum(item.risk_level == "High" for item in pairs),
            departments=tuple(departments),
            department_pairs=tuple(pairs),
            brokers=tuple(brokers),
            insights=tuple(insights),
            recommendations=tuple(recommendations),
        )

    def _department_metrics(self, graph, source_metrics) -> list[DepartmentCollaborationMetric]:
        department_names = sorted({item.department for item in source_metrics})
        partner_map = {name: set() for name in department_names}
        for (left, right), count in graph.department_links().items():
            if count > 0:
                partner_map[left].add(right)
                partner_map[right].add(left)

        maximum_partners = max(1, len(department_names) - 1)
        result = []
        for item in source_metrics:
            partner_score = len(partner_map[item.department]) / maximum_partners
            external_score = min(1.0, item.external_links / max(1, item.employee_count * 2))
            score = round((partner_score * 0.6 + external_score * 0.4) * 100)
            result.append(DepartmentCollaborationMetric(
                department=item.department,
                employee_count=item.employee_count,
                internal_links=item.internal_links,
                external_links=item.external_links,
                partner_departments=len(partner_map[item.department]),
                collaboration_score=score,
                risk_level=self._risk(score),
            ))
        return sorted(result, key=lambda value: (value.collaboration_score, value.department.casefold()))

    def _department_pairs(self, graph: OrganizationGraph) -> list[DepartmentPairMetric]:
        departments = sorted({employee.department for employee in graph.employees.values()})
        links = graph.department_links()
        result = []
        for left, right in combinations(departments, 2):
            count = links.get(tuple(sorted((left, right))), 0)
            left_size = sum(item.department == left for item in graph.employees.values())
            right_size = sum(item.department == right for item in graph.employees.values())
            possible = max(1, left_size * right_size)
            score = min(100, round((count / possible) * 100 * 2.5))
            result.append(DepartmentPairMetric(
                department_a=left,
                department_b=right,
                inferred_links=count,
                collaboration_score=score,
                risk_level=self._risk(score),
            ))
        return sorted(result, key=lambda value: (value.collaboration_score, value.department_a, value.department_b))

    def _brokers(self, graph, people_metrics) -> list[CollaborationBroker]:
        departments_reached = {}
        for item in people_metrics:
            employee = graph.employees[item.employee_id]
            reached = {
                graph.employees[neighbor].department
                for neighbor in graph.neighbors(item.employee_id)
                if graph.employees[neighbor].department != employee.department
            }
            departments_reached[item.employee_id] = reached

        candidates = []
        for item in people_metrics:
            reached = departments_reached[item.employee_id]
            if item.cross_department_links < 2 and len(reached) < 2:
                continue
            dependency = "High" if item.cross_department_links >= 3 or len(reached) >= 3 else "Medium"
            candidates.append(CollaborationBroker(
                employee_id=item.employee_id,
                name=item.name,
                department=item.department,
                total_relationships=item.degree,
                cross_department_links=item.cross_department_links,
                departments_reached=len(reached),
                dependency_level=dependency,
            ))
        return sorted(candidates, key=lambda value: (-value.cross_department_links, -value.departments_reached, value.name.casefold()))

    def _overall_score(self, departments, pairs) -> int:
        if not departments:
            return 0
        department_average = sum(item.collaboration_score for item in departments) / len(departments)
        connected_pairs = [item for item in pairs if item.inferred_links > 0]
        pair_coverage = (len(connected_pairs) / len(pairs) * 100) if pairs else 100
        return max(0, min(100, round(department_average * 0.65 + pair_coverage * 0.35)))

    def _insights(self, departments, pairs, brokers, overall_score) -> list[OrganizationInsight]:
        builder = InsightEngine()
        insights: list[OrganizationInsight] = []

        high_risk_departments = [item for item in departments if item.risk_level == "High"]
        for item in high_risk_departments[:3]:
            insights.append(builder.build(
                insight_id=f"collaboration-silo-{item.department.casefold().replace(' ', '-')}",
                title=f"{item.department} shows a strong silo signal",
                category="Collaboration",
                severity="High",
                confidence=0.88,
                current_situation=(
                    f"{item.department} connects with {item.partner_departments} other department(s) "
                    f"through {item.external_links} inferred cross-department relationship(s)."
                ),
                business_impact="A persistent silo can slow cross-functional delivery, reduce knowledge transfer and increase rework.",
                evidence=[
                    {"label": "Collaboration score", "detail": f"{item.collaboration_score}/100", "strength": 0.9},
                    {"label": "Partner departments", "detail": str(item.partner_departments), "strength": 0.85},
                    {"label": "External links", "detail": str(item.external_links), "strength": 0.8},
                ],
                recommendations=[
                    {"action": f"Create a named cross-functional liaison for {item.department}.", "priority": "High", "timeframe": "30 days", "business_value": "Improve coordination and reduce silo risk."},
                    {"action": f"Launch one recurring cross-department working session involving {item.department}.", "priority": "Medium", "timeframe": "60 days", "business_value": "Create repeatable collaboration paths."},
                ],
            ))

        weak_pairs = [item for item in pairs if item.risk_level == "High"]
        if weak_pairs:
            pair = weak_pairs[0]
            insights.append(builder.build(
                insight_id=f"collaboration-pair-{pair.department_a.casefold()}-{pair.department_b.casefold()}",
                title=f"Collaboration between {pair.department_a} and {pair.department_b} needs validation",
                category="Collaboration",
                severity="Medium" if pair.inferred_links else "High",
                confidence=0.78,
                current_situation=f"Only {pair.inferred_links} inferred relationship(s) connect these departments.",
                business_impact="If the departments share processes or transformation goals, weak connectivity may create delays and unclear ownership.",
                evidence=[
                    {"label": "Inferred links", "detail": str(pair.inferred_links), "strength": 0.85},
                    {"label": "Pair collaboration score", "detail": f"{pair.collaboration_score}/100", "strength": 0.8},
                ],
                recommendations=[
                    {"action": f"Validate shared processes between {pair.department_a} and {pair.department_b}, then appoint a liaison where needed.", "priority": "High", "timeframe": "45 days", "business_value": "Reduce cross-functional friction."},
                ],
            ))

        if brokers:
            broker = brokers[0]
            insights.append(builder.build(
                insight_id=f"collaboration-broker-{broker.employee_id}",
                title=f"{broker.name} is a critical collaboration bridge",
                category="Network dependency",
                severity="High" if broker.dependency_level == "High" else "Medium",
                confidence=0.9,
                current_situation=(
                    f"{broker.name} connects {broker.departments_reached} department(s) through "
                    f"{broker.cross_department_links} cross-department relationship(s)."
                ),
                business_impact="Heavy reliance on one informal bridge creates bottlenecks and continuity risk.",
                evidence=[
                    {"label": "Cross-department links", "detail": str(broker.cross_department_links), "strength": 0.92},
                    {"label": "Departments reached", "detail": str(broker.departments_reached), "strength": 0.9},
                    {"label": "Total relationships", "detail": str(broker.total_relationships), "strength": 0.82},
                ],
                recommendations=[
                    {"action": f"Create a secondary collaboration bridge for the relationships concentrated on {broker.name}.", "priority": "High", "timeframe": "60 days", "business_value": "Improve organizational resilience."},
                    {"action": "Document recurring cross-functional collaboration paths and ownership.", "priority": "Medium", "timeframe": "90 days", "business_value": "Reduce dependency on informal networks."},
                ],
            ))

        if not insights:
            insights.append(builder.build(
                insight_id="collaboration-health-positive",
                title="Collaboration signals are broadly distributed",
                category="Collaboration",
                severity="Low",
                confidence=0.72,
                current_situation=f"The inferred collaboration health score is {overall_score}/100 with no high-risk silo detected.",
                business_impact="Distributed collaboration supports resilience and faster cross-functional execution.",
                evidence=[{"label": "Overall collaboration score", "detail": f"{overall_score}/100", "strength": 0.75}],
                recommendations=[{"action": "Continue monitoring collaboration patterns as new data becomes available.", "priority": "Low", "timeframe": "Quarterly", "business_value": "Preserve collaboration health."}],
            ))

        return insights

    def _recommendations(self, departments, pairs, brokers) -> list[str]:
        actions = []
        for item in departments:
            if item.risk_level == "High":
                actions.append(f"Create a cross-functional liaison for {item.department}.")
        for item in pairs:
            if item.risk_level == "High" and item.inferred_links == 0:
                actions.append(f"Validate collaboration needs between {item.department_a} and {item.department_b}.")
        for broker in brokers[:2]:
            if broker.dependency_level == "High":
                actions.append(f"Create backup collaboration coverage for {broker.name}.")
        return list(dict.fromkeys(actions))[:8]

    @staticmethod
    def _risk(score: int) -> str:
        if score < 30:
            return "High"
        if score < 60:
            return "Medium"
        return "Low"

    @staticmethod
    def _health(score: int) -> str:
        if score >= 70:
            return "Healthy"
        if score >= 45:
            return "Watch"
        return "At risk"
