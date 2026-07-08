from dataclasses import dataclass, field
from typing import List

from talentcopilot.decision_core.orchestrator_models import DecisionCoreOutput


@dataclass
class WorkspaceBridgeReport:
    role_title: str
    total_candidates: int
    profiles_created: int
    outputs: List[DecisionCoreOutput] = field(default_factory=list)
    status: str = "Ready"
