from dataclasses import dataclass, field
from typing import List


@dataclass
class CopilotAction:
    title: str
    rationale: str
    priority: str = "Medium"
    owner: str = "Recruiter"


@dataclass
class CopilotQuestion:
    question: str
    purpose: str
    expected_signal: str = ""


@dataclass
class CopilotAlert:
    title: str
    detail: str
    severity: str = "Medium"


@dataclass
class CandidateCopilotSummary:
    candidate_name: str
    rank: int
    match_score: float
    headline: str
    recruiter_summary: str
    actions: List[CopilotAction] = field(default_factory=list)
    questions: List[CopilotQuestion] = field(default_factory=list)
    alerts: List[CopilotAlert] = field(default_factory=list)
    stakeholder_summary: str = ""


@dataclass
class RecruiterCopilotWorkspaceReport:
    role_title: str
    session_id: str
    candidates: List[CandidateCopilotSummary] = field(default_factory=list)
    global_actions: List[CopilotAction] = field(default_factory=list)
