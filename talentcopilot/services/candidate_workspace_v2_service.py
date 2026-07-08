from dataclasses import dataclass
from typing import List

from talentcopilot.decision_core.workspace_bridge import DecisionCoreWorkspaceBridge
from talentcopilot.decision_core.orchestrator_models import DecisionCoreOutput


@dataclass
class CandidateWorkspaceV2Report:
    role_title: str
    outputs: List[DecisionCoreOutput]
    status: str


class CandidateWorkspaceV2Service:
    def build_from_session(self, session=None) -> CandidateWorkspaceV2Report:
        bridge_report = DecisionCoreWorkspaceBridge().build_from_session(session)
        return CandidateWorkspaceV2Report(
            role_title=bridge_report.role_title,
            outputs=bridge_report.outputs,
            status=bridge_report.status,
        )

    def build_demo(self) -> CandidateWorkspaceV2Report:
        bridge_report = DecisionCoreWorkspaceBridge().build_demo()
        return CandidateWorkspaceV2Report(
            role_title=bridge_report.role_title,
            outputs=bridge_report.outputs,
            status=bridge_report.status,
        )
