from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple


class MissionDomain(str, Enum):
    RECRUITMENT = "recruitment"
    ORGANIZATION = "organization"
    SUCCESSION = "succession"
    SKILLS = "skills"
    WORKFORCE = "workforce"
    COLLABORATION = "collaboration"
    KNOWLEDGE = "knowledge"
    INTERNAL_MOBILITY = "internal_mobility"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class MissionCanvas:
    raw_request: str
    domain: MissionDomain
    mission_title: str
    objective: str
    context: str
    constraints: Tuple[str, ...] = field(default_factory=tuple)
    success_criteria: Tuple[str, ...] = field(default_factory=tuple)
    required_inputs: Tuple[str, ...] = field(default_factory=tuple)
    recommended_workflow: Tuple[str, ...] = field(default_factory=tuple)
    target_page: str | None = None
    confidence: str = "Limited"
    limitation: str = "Additional context is required before a reliable analysis can begin."
