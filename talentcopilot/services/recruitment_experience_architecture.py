from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class ExperienceSpace:
    key: str
    label: str
    purpose: str
    owns: tuple[str, ...]
    previews: tuple[str, ...] = ()
    primary_action: str = ""


@dataclass(frozen=True)
class WorkflowStep:
    key: str
    label: str
    target_page: str
    completion_signal: str


TARGET_SPACES: tuple[ExperienceSpace, ...] = (
    ExperienceSpace(
        key="recruitment",
        label="Recruitment Workspace",
        purpose="Pilot the active recruitment and move the workflow forward.",
        owns=("workflow progress", "shortlist status", "operational alerts", "next action"),
        previews=("candidate recommendation", "interview readiness", "decision status"),
        primary_action="Review shortlisted candidates",
    ),
    ExperienceSpace(
        key="candidate",
        label="Candidate Intelligence",
        purpose="Understand one candidate's recommendation, competencies, evidence and risks.",
        owns=("candidate summary", "competency matrix", "evidence", "risks"),
        previews=("interview priorities",),
        primary_action="Prepare interview",
    ),
    ExperienceSpace(
        key="interview",
        label="Interview Intelligence",
        purpose="Prepare, conduct and record evidence from the interview.",
        owns=("interview playbook", "live notes", "competency validation", "interview assessment"),
        previews=("candidate summary", "material risks"),
        primary_action="Save assessment and compare",
    ),
    ExperienceSpace(
        key="decision",
        label="Comparison & Decision",
        purpose="Compare finalists and document the final hiring decision.",
        owns=("finalist comparison", "decision rationale", "final recommendation", "decision record"),
        previews=("candidate strengths", "unresolved risks"),
        primary_action="Finalize recommendation",
    ),
)


WORKFLOW: tuple[WorkflowStep, ...] = (
    WorkflowStep("setup", "Create recruitment", "Recruitment Workspace", "active recruitment exists"),
    WorkflowStep("role", "Add job description", "Recruitment Workspace", "role profile is available"),
    WorkflowStep("candidates", "Add candidates", "Recruitment Workspace", "at least one candidate exists"),
    WorkflowStep("analysis", "Review analysis", "Recruitment Workspace", "candidate analyses are complete"),
    WorkflowStep("candidate", "Deep-dive candidates", "Candidate Intelligence", "shortlist review recorded"),
    WorkflowStep("prepare", "Prepare interviews", "Interview Intelligence", "playbook generated"),
    WorkflowStep("assess", "Record interview findings", "Interview Intelligence", "assessment saved"),
    WorkflowStep("compare", "Compare finalists", "Comparison", "finalists compared"),
    WorkflowStep("decide", "Make decision", "Decision Board", "decision recorded"),
)


DUPLICATE_CONTENT_CONTRACT: dict[str, str] = {
    "workflow progress": "Recruitment Workspace",
    "candidate recommendation": "Candidate Intelligence",
    "competency matrix": "Candidate Intelligence",
    "candidate evidence": "Candidate Intelligence",
    "candidate risks": "Candidate Intelligence",
    "interview questions": "Interview Intelligence",
    "interview notes": "Interview Intelligence",
    "finalist comparison": "Comparison",
    "final decision": "Decision Board",
}


LEGACY_ROUTE_ALIASES: dict[str, str] = {
    "Candidate Workspace": "Candidate Intelligence",
    "Interview Workspace": "Interview Intelligence",
    "Recruitment Intelligence": "Recruitment Workspace",
}


def validate_architecture(
    spaces: Iterable[ExperienceSpace] = TARGET_SPACES,
    workflow: Iterable[WorkflowStep] = WORKFLOW,
) -> list[str]:
    errors: list[str] = []
    spaces = tuple(spaces)
    workflow = tuple(workflow)

    labels = [space.label for space in spaces]
    if len(labels) != len(set(labels)):
        errors.append("Target space labels must be unique.")

    owned_items: dict[str, str] = {}
    for space in spaces:
        if not space.primary_action:
            errors.append(f"{space.label} has no primary action.")
        for item in space.owns:
            previous = owned_items.get(item)
            if previous and previous != space.label:
                errors.append(f"{item!r} is owned by both {previous} and {space.label}.")
            owned_items[item] = space.label

    step_keys = [step.key for step in workflow]
    if len(step_keys) != len(set(step_keys)):
        errors.append("Workflow step keys must be unique.")
    for step in workflow:
        if not step.target_page or not step.completion_signal:
            errors.append(f"Workflow step {step.key!r} is incomplete.")

    for information, owner in DUPLICATE_CONTENT_CONTRACT.items():
        if not information or not owner:
            errors.append("Duplicate-content contract entries must be complete.")

    return errors
