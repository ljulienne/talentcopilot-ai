from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple


class MissionHealth(str, Enum):
    STRONG = "Strong"
    NEEDS_ATTENTION = "Needs attention"
    AT_RISK = "At risk"


@dataclass(frozen=True)
class NextBestAction:
    title: str
    reason: str
    readiness_gain: int = 0
    target_page: str | None = None


@dataclass(frozen=True)
class MissionJournalEntry:
    label: str
    detail: str
    status: str = "complete"


@dataclass(frozen=True)
class MissionWorkspaceSnapshot:
    mission_title: str
    domain_label: str
    stage: str
    readiness: int
    decision_confidence: int
    health: MissionHealth
    health_reasons: Tuple[str, ...] = field(default_factory=tuple)
    missing_evidence: Tuple[str, ...] = field(default_factory=tuple)
    next_actions: Tuple[NextBestAction, ...] = field(default_factory=tuple)
    journal: Tuple[MissionJournalEntry, ...] = field(default_factory=tuple)
    reasoning: str = ""
