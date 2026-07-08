from dataclasses import dataclass, field
from typing import List


@dataclass
class DemoWorkspaceStep:
    order: int
    workspace: str
    business_question: str
    talking_point: str
    expected_duration_minutes: int
    status: str = "Ready"


@dataclass
class DemoReadinessItem:
    name: str
    status: str
    detail: str


@dataclass
class EnterpriseDemoFinalReport:
    title: str
    positioning: str
    total_duration_minutes: int
    readiness_score: int
    steps: List[DemoWorkspaceStep] = field(default_factory=list)
    readiness_items: List[DemoReadinessItem] = field(default_factory=list)
    closing_message: str = ""
