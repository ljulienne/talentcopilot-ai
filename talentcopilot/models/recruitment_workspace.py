from dataclasses import dataclass, field
from typing import List


@dataclass
class PipelineStage:
    name: str
    count: int
    status: str = "pending"


@dataclass
class WorkspaceCandidate:
    rank: int
    name: str
    stage: str
    match_score: float
    recommendation: str


@dataclass
class TimelineEvent:
    label: str
    status: str
    description: str = ""


@dataclass
class RecruitmentWorkspaceReport:
    role_title: str
    session_id: str
    status: str
    candidates_count: int
    analyzed_count: int
    pipeline: List[PipelineStage] = field(default_factory=list)
    candidates: List[WorkspaceCandidate] = field(default_factory=list)
    timeline: List[TimelineEvent] = field(default_factory=list)
    next_actions: List[str] = field(default_factory=list)
