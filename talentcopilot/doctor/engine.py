from __future__ import annotations

from pathlib import Path

from talentcopilot.doctor.checks import (
    check_critical_imports,
    check_git_state,
    check_navigation,
    check_python_path,
    check_release_artifacts,
    check_repository_layout,
    check_test_inventory,
    check_executive_copilot_readiness,
)
from talentcopilot.doctor.models import DoctorReport


class TalentCopilotDoctor:
    def __init__(self, repo: str | Path):
        self.repo = Path(repo).resolve()

    def run(self, *, include_git: bool = True) -> DoctorReport:
        checks = [
            check_repository_layout(self.repo),
            check_python_path(self.repo),
            check_critical_imports(),
            check_navigation(),
            check_test_inventory(self.repo),
            check_executive_copilot_readiness(self.repo),
        ]
        if include_git:
            checks.extend(
                [
                    check_release_artifacts(self.repo),
                    check_git_state(self.repo),
                ]
            )
        return DoctorReport(tuple(checks))
