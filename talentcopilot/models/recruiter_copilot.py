from dataclasses import dataclass, field
from enum import Enum
from typing import List


class CopilotPriority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class CopilotActionType(str, Enum):
    MOVE_FORWARD = "Move Forward"
    VALIDATE = "Validate"
    HOLD = "Hold"
    REJECT = "Reject"
    COMPARE = "Compare"


@dataclass
class CopilotAction:
    action_type: CopilotActionType
    priority: CopilotPriority
    title: str
    rationale: str
    suggested_owner: str = "Recruiter"


@dataclass
class CopilotQuestion:
    competency: str
    question: str
    purpose: str
    positive_signal: str
    red_flag: str


@dataclass
class CopilotAlert:
    severity: CopilotPriority
    title: str
    message: str
    mitigation: str = ""


@dataclass
class RecruiterCopilotReport:
    candidate_name: str
    role_title: str
    headline: str
    recruiter_summary: str
    actions: List[CopilotAction] = field(default_factory=list)
    interview_questions: List[CopilotQuestion] = field(default_factory=list)
    alerts: List[CopilotAlert] = field(default_factory=list)
    stakeholder_summary: str = ""
    closing_recommendation: str = ""

    @property
    def has_high_priority_alerts(self) -> bool:
        return any(alert.severity == CopilotPriority.HIGH for alert in self.alerts)

    @property
    def action_count(self) -> int:
        return len(self.actions)
