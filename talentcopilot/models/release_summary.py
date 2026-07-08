from dataclasses import dataclass, field
from typing import List


@dataclass
class ReleaseWorkspaceStatus:
    name: str
    status: str
    value: str


@dataclass
class ReleaseSummary:
    release_name: str
    version: str
    summary: str
    workspaces: List[ReleaseWorkspaceStatus] = field(default_factory=list)
    next_release_focus: List[str] = field(default_factory=list)
