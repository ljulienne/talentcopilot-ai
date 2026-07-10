from collections import defaultdict
from typing import Iterable

from .models import (
    CollaborationRecord,
    ConnectorInsight,
    DepartmentInsight,
    OrganizationDiagnostic,
)


class OrganizationIntelligenceService:
    """Small, explainable ONA foundation for the first product release.

    It deliberately uses interaction metadata only. It does not inspect message
    contents and does not infer personality, emotions, or protected attributes.
    """

    REQUIRED_COLUMNS = {
        "source_person",
        "source_department",
        "target_person",
        "target_department",
        "interactions",
    }

    def analyze(self, records: Iterable[CollaborationRecord]) -> OrganizationDiagnostic:
        rows = [row for row in records if row.interactions > 0]
        if not rows:
            return OrganizationDiagnostic(
                record_count=0,
                departments=[],
                executive_summary="No collaboration data has been loaded yet.",
                recommendations=["Upload a collaboration export or use the demonstration dataset."],
            )

        departments = sorted(
            {
                department.strip()
                for row in rows
                for department in (row.source_department, row.target_department)
                if department.strip()
            }
        )

        internal_weight = defaultdict(int)
        external_weight = defaultdict(int)
        person_departments = defaultdict(set)
        person_weight = defaultdict(int)
        total_weight = 0
        cross_weight = 0

        for row in rows:
            weight = int(row.interactions)
            total_weight += weight
            source_department = row.source_department.strip()
            target_department = row.target_department.strip()

            person_departments[row.source_person.strip()].add(source_department)
            person_departments[row.source_person.strip()].add(target_department)
            person_departments[row.target_person.strip()].add(source_department)
            person_departments[row.target_person.strip()].add(target_department)
            person_weight[row.source_person.strip()] += weight
            person_weight[row.target_person.strip()] += weight

            if source_department == target_department:
                internal_weight[source_department] += weight
            else:
                cross_weight += weight
                external_weight[source_department] += weight
                external_weight[target_department] += weight

        department_insights = []
        for department in departments:
            internal = internal_weight[department]
            external = external_weight[department]
            denominator = internal + external
            ratio = external / denominator if denominator else 0.0
            department_insights.append(
                DepartmentInsight(
                    department=department,
                    internal_weight=internal,
                    external_weight=external,
                    collaboration_ratio=round(ratio, 3),
                )
            )

        department_insights.sort(key=lambda item: (item.collaboration_ratio, item.external_weight))

        connectors = [
            ConnectorInsight(
                person=person,
                departments_reached=len(departments_reached),
                interaction_weight=person_weight[person],
            )
            for person, departments_reached in person_departments.items()
            if person and len(departments_reached) > 1
        ]
        connectors.sort(key=lambda item: (item.departments_reached, item.interaction_weight), reverse=True)

        cross_ratio = cross_weight / total_weight if total_weight else 0.0
        lowest = department_insights[0] if department_insights else None
        top_connector = connectors[0] if connectors else None

        summary_parts = [
            f"{len(departments)} departments and {len(rows)} collaboration links were analyzed.",
            f"{cross_ratio:.0%} of recorded interaction weight crosses departmental boundaries.",
        ]
        if lowest:
            summary_parts.append(
                f"{lowest.department} currently has the weakest cross-department collaboration signal."
            )
        if top_connector:
            summary_parts.append(
                f"{top_connector.person} appears to be a key connector across {top_connector.departments_reached} departments."
            )

        recommendations = []
        if lowest and lowest.collaboration_ratio < 0.35:
            recommendations.append(
                f"Review workflows involving {lowest.department}; its external collaboration ratio is only {lowest.collaboration_ratio:.0%}."
            )
        if top_connector and top_connector.interaction_weight >= max(5, total_weight * 0.2):
            recommendations.append(
                f"Reduce dependency on {top_connector.person} by creating backup links and documenting cross-team knowledge."
            )
        if cross_ratio < 0.4:
            recommendations.append(
                "Create at least one recurring cross-functional forum around the most interdependent business processes."
            )
        if not recommendations:
            recommendations.append(
                "Collaboration appears broadly distributed; validate the pattern with project outcomes and an employee survey."
            )

        return OrganizationDiagnostic(
            record_count=len(rows),
            departments=departments,
            connectors=connectors[:5],
            department_insights=department_insights,
            cross_department_weight=cross_weight,
            total_weight=total_weight,
            executive_summary=" ".join(summary_parts),
            recommendations=recommendations,
        )

    def demo_records(self) -> list[CollaborationRecord]:
        return [
            CollaborationRecord("Maya", "HR", "Noah", "IT", 12),
            CollaborationRecord("Maya", "HR", "Emma", "Finance", 8),
            CollaborationRecord("Noah", "IT", "Liam", "Operations", 10),
            CollaborationRecord("Emma", "Finance", "Liam", "Operations", 3),
            CollaborationRecord("Ava", "HR", "Maya", "HR", 14),
            CollaborationRecord("Lucas", "IT", "Noah", "IT", 15),
            CollaborationRecord("Chloe", "Finance", "Emma", "Finance", 18),
            CollaborationRecord("Leo", "Operations", "Liam", "Operations", 11),
            CollaborationRecord("Maya", "HR", "Liam", "Operations", 5),
        ]
