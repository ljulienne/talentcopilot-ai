"""Operational action-center models for persisted recruitment projects.

The action center is deliberately separate from candidate scoring. It turns
portfolio workflow signals into one transparent action per open project and
stores only execution status metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


ACTION_STATUS_OPEN = "Open"
ACTION_STATUS_IN_PROGRESS = "In progress"
ACTION_STATUS_DONE = "Done"
ACTION_STATUS_VALUES = (
    ACTION_STATUS_OPEN,
    ACTION_STATUS_IN_PROGRESS,
    ACTION_STATUS_DONE,
)


@dataclass(frozen=True)
class RecruitmentAction:
    action_id: str
    project_id: str
    project_title: str
    role_title: str
    lifecycle: str
    severity: str
    category: str
    summary: str
    recommended_action: str
    owner: str
    priority: str
    activity_age_days: int | None
    status: str
    source: str
    is_active: bool = False
    status_updated_at: str = ""
    status_actor: str = ""


@dataclass(frozen=True)
class RecruitmentActionCenterReport:
    generated_at: str
    total_actions: int
    open_actions: int
    in_progress_actions: int
    done_actions: int
    critical_or_high_open_actions: int
    unassigned_open_actions: int
    actions: Tuple[RecruitmentAction, ...] = field(default_factory=tuple)
    limitation: str = (
        "Action status records operational follow-up only. Completing an action "
        "does not suppress the underlying portfolio signal, alter project evidence, "
        "or change candidate scores and ranks."
    )
