from dataclasses import dataclass, field


@dataclass(frozen=True)
class CollaborationRecord:
    source_person: str
    source_department: str
    target_person: str
    target_department: str
    interactions: int = 1


@dataclass(frozen=True)
class ConnectorInsight:
    person: str
    departments_reached: int
    interaction_weight: int


@dataclass(frozen=True)
class DepartmentInsight:
    department: str
    internal_weight: int
    external_weight: int
    collaboration_ratio: float


@dataclass(frozen=True)
class OrganizationDiagnostic:
    record_count: int
    departments: list[str]
    connectors: list[ConnectorInsight] = field(default_factory=list)
    department_insights: list[DepartmentInsight] = field(default_factory=list)
    cross_department_weight: int = 0
    total_weight: int = 0
    executive_summary: str = ""
    recommendations: list[str] = field(default_factory=list)
