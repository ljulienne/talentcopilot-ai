from dataclasses import dataclass, field
from typing import List


@dataclass
class DemoStep:
    order: int
    workspace: str
    objective: str
    expected_value: str


@dataclass
class DemoCheck:
    name: str
    status: str
    detail: str = ""


@dataclass
class DemoExperienceReport:
    scenario_name: str
    role_title: str
    session_id: str
    readiness_score: int
    steps: List[DemoStep] = field(default_factory=list)
    checks: List[DemoCheck] = field(default_factory=list)
    presenter_notes: List[str] = field(default_factory=list)
