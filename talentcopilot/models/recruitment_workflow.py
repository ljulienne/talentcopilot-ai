from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class WorkflowStepState:
    key: str
    label: str
    page_label: str
    completed: bool = False
    current: bool = False
    available: bool = True
    reason: str = ""


@dataclass
class RecruitmentWorkflowContext:
    session_id: str = ""
    role_title: str = "Recruitment"
    selected_candidate_id: str = ""
    selected_candidate_name: str = ""
    current_step: str = "setup"
    completed_steps: list[str] = field(default_factory=list)
    last_page: str = "Recruitment Workspace"
    next_page: str = "Recruitment Workspace"
    shortlisted_candidate_ids: list[str] = field(default_factory=list)
    interview_prepared_candidate_ids: list[str] = field(default_factory=list)
    interview_assessed_candidate_ids: list[str] = field(default_factory=list)
    finalists_compared: bool = False
    decision_recorded: bool = False
    interview_evaluations: dict[str, dict] = field(default_factory=dict)
    finalist_candidate_ids: list[str] = field(default_factory=list)
    final_decision_candidate_id: str = ""
    final_decision_rationale: str = ""
    final_decision_recommendation: str = ""

    def select_candidate(self, candidate_id: str, candidate_name: str = "") -> None:
        self.selected_candidate_id = str(candidate_id or "")
        self.selected_candidate_name = str(candidate_name or "")

    def mark_completed(self, step_key: str) -> None:
        if step_key and step_key not in self.completed_steps:
            self.completed_steps.append(step_key)
