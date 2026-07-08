from dataclasses import dataclass, field
from typing import List


@dataclass
class CommandCenterMetric:
    label: str
    value: str
    delta: str = ""


@dataclass
class CommandCenterPriority:
    title: str
    description: str
    badge: str = "AI Priority"
    impact: str = "High"


@dataclass
class CommandCenterActivity:
    time: str
    title: str
    detail: str


@dataclass
class RecruitmentHealth:
    overall_score: int
    evidence_coverage: int
    interview_readiness: int
    decision_confidence: int
    bias_risk: str
    data_completeness: int


@dataclass
class CommandCenterReport:
    role_title: str
    session_id: str
    metrics: List[CommandCenterMetric] = field(default_factory=list)
    priorities: List[CommandCenterPriority] = field(default_factory=list)
    activities: List[CommandCenterActivity] = field(default_factory=list)
    health: RecruitmentHealth = None
    next_action_title: str = "Load Enterprise Demo"
    next_action_body: str = "Start with a realistic recruitment scenario."
