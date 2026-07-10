from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from typing import Iterable

from .models import EmployeeRecord


@dataclass(frozen=True)
class GraphEdge:
    source: str
    target: str
    relation: str
    weight: float = 1.0
    evidence: str = ""


@dataclass
class OrganizationGraph:
    employees: dict[str, EmployeeRecord]
    edges: list[GraphEdge] = field(default_factory=list)

    def neighbors(self, employee_id: str) -> set[str]:
        result: set[str] = set()
        for edge in self.edges:
            if edge.source == employee_id:
                result.add(edge.target)
            elif edge.target == employee_id:
                result.add(edge.source)
        return result

    def degree(self, employee_id: str) -> int:
        return len(self.neighbors(employee_id))

    def weighted_degree(self, employee_id: str) -> float:
        total = 0.0
        for edge in self.edges:
            if edge.source == employee_id or edge.target == employee_id:
                total += edge.weight
        return round(total, 2)

    def relation_count(self, relation: str) -> int:
        return sum(edge.relation == relation for edge in self.edges)

    def department_links(self) -> dict[tuple[str, str], int]:
        links: dict[tuple[str, str], int] = {}
        for edge in self.edges:
            left = self.employees[edge.source].department
            right = self.employees[edge.target].department
            if left == right:
                continue
            key = tuple(sorted((left, right)))
            links[key] = links.get(key, 0) + 1
        return links


class OrganizationGraphBuilder:
    """Builds an explainable people graph from standard HR exports."""

    def build(self, employees: Iterable[EmployeeRecord]) -> OrganizationGraph:
        items = list(employees)
        by_id = {item.employee_id: item for item in items}
        by_name = {item.name.casefold(): item.employee_id for item in items}
        edges: dict[tuple[str, str, str], GraphEdge] = {}

        def add(source: str, target: str, relation: str, weight: float, evidence: str) -> None:
            if source == target or source not in by_id or target not in by_id:
                return
            left, right = sorted((source, target))
            key = (left, right, relation)
            current = edges.get(key)
            if current is None or weight > current.weight:
                edges[key] = GraphEdge(left, right, relation, weight, evidence)

        for employee in items:
            manager_id = by_name.get(employee.manager.casefold()) if employee.manager else None
            if manager_id:
                add(employee.employee_id, manager_id, "manager", 1.0, f"{employee.name} reports to {employee.manager}")

        for left, right in combinations(items, 2):
            shared = sorted(set(skill.casefold() for skill in left.skills) & set(skill.casefold() for skill in right.skills))
            if shared:
                weight = min(1.0, 0.25 + 0.15 * len(shared))
                add(left.employee_id, right.employee_id, "shared_skill", weight, "Shared skills: " + ", ".join(shared))

            left_backup = set(skill.casefold() for skill in left.backup_for)
            right_skills = set(skill.casefold() for skill in right.skills)
            right_backup = set(skill.casefold() for skill in right.backup_for)
            left_skills = set(skill.casefold() for skill in left.skills)
            if left_backup & right_skills:
                add(left.employee_id, right.employee_id, "backup", 0.9, f"{left.name} provides backup coverage for {right.name}")
            if right_backup & left_skills:
                add(left.employee_id, right.employee_id, "backup", 0.9, f"{right.name} provides backup coverage for {left.name}")

        return OrganizationGraph(employees=by_id, edges=list(edges.values()))
