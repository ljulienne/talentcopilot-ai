from dataclasses import dataclass, field
from enum import Enum
from typing import List


class WorkflowStageStatus(str, Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    READY = "Ready"
    COMPLETED = "Completed"
    BLOCKED = "Blocked"


class WorkflowStageName(str, Enum):
    INTAKE = "Intake"
    CANDIDATE_ANALYSIS = "Candidate Analysis"
    SHORTLIST = "Shortlist"
    DECISION_REVIEW = "Decision Review"
    INTERVIEW_PLANNING = "Interview Planning"
    REPORTING = "Reporting"


@dataclass
class WorkflowStage:
    name: WorkflowStageName
    status: WorkflowStageStatus
    explanation: str
    next_action: str = ""


@dataclass
class RecruiterWorkflowReport:
    role_title: str
    session_id: str
    overall_status: WorkflowStageStatus
    stages: List[WorkflowStage] = field(default_factory=list)
    recommended_next_action: str = ""
    shortlist_candidate_names: List[str] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)

    @property
    def completed_count(self) -> int:
        return len([stage for stage in self.stages if stage.status == WorkflowStageStatus.COMPLETED])

    @property
    def blocked_count(self) -> int:
        return len([stage for stage in self.stages if stage.status == WorkflowStageStatus.BLOCKED])
