from dataclasses import dataclass, field
from typing import List


@dataclass
class RecruitmentPipelineAction:
    title: str
    owner: str
    priority: str
    rationale: str


@dataclass
class RecruitmentPipelineStage:
    name: str
    status: str
    count: int
    readiness: int
    action: RecruitmentPipelineAction


@dataclass
class RecruitmentPipelineReport:
    role_title: str
    session_id: str
    overall_readiness: int
    stages: List[RecruitmentPipelineStage] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    next_actions: List[RecruitmentPipelineAction] = field(default_factory=list)
