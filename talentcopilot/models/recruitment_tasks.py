from dataclasses import dataclass, field
from typing import List


@dataclass
class RecruitmentTask:
    title: str
    owner: str
    priority: str
    status: str
    detail: str


@dataclass
class RecruitmentTaskReport:
    role_title: str
    session_id: str
    total_tasks: int
    open_tasks: int
    blockers: List[str] = field(default_factory=list)
    tasks: List[RecruitmentTask] = field(default_factory=list)
