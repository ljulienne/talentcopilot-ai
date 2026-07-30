"""Recruitment project portfolio and lifecycle management.

Release 8.5.0 builds on restart-safe project persistence. It adds a compact,
queryable portfolio model without changing candidate scores, ranks or the
canonical recruitment source of truth.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping, Sequence

from talentcopilot.models.recruitment_workflow import RecruitmentWorkflowContext
from talentcopilot.services.recruitment_project_persistence import (
    load_project,
    save_project,
    session_from_project_payload,
    workflow_context_from_payload,
)
from talentcopilot.storage.recruitment_store import load_recruitment, save_recruitment


PROJECT_MANAGEMENT_KEY = "project_management"
PROJECT_PORTFOLIO_VERSION = "talentcopilot-project-portfolio-v1"

LIFECYCLE_DRAFT = "draft"
LIFECYCLE_ANALYZING = "analyzing"
LIFECYCLE_REVIEW = "review"
LIFECYCLE_INTERVIEW = "interview"
LIFECYCLE_DECISION_READY = "decision_ready"
LIFECYCLE_DECIDED = "decided"
LIFECYCLE_ARCHIVED = "archived"

LIFECYCLE_LABELS = {
    LIFECYCLE_DRAFT: "Draft",
    LIFECYCLE_ANALYZING: "Analyzing",
    LIFECYCLE_REVIEW: "Review",
    LIFECYCLE_INTERVIEW: "Interview",
    LIFECYCLE_DECISION_READY: "Decision ready",
    LIFECYCLE_DECIDED: "Decided",
    LIFECYCLE_ARCHIVED: "Archived",
}

PRIORITY_VALUES = ("Normal", "High", "Critical")


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_text(value: Any, fallback: str = "") -> str:
    text = str(value or "").strip()
    return text or fallback


def _management_from_mapping(data: Mapping[str, Any] | None) -> dict[str, Any]:
    payload = dict(data or {})
    metadata = payload.get("metadata") if isinstance(payload.get("metadata"), Mapping) else {}
    management = metadata.get(PROJECT_MANAGEMENT_KEY) if isinstance(metadata, Mapping) else {}
    return dict(management or {}) if isinstance(management, Mapping) else {}


def management_from_session(session: Any | None) -> dict[str, Any]:
    metadata = getattr(session, "metadata", {}) or {}
    management = metadata.get(PROJECT_MANAGEMENT_KEY) if isinstance(metadata, Mapping) else {}
    return dict(management or {}) if isinstance(management, Mapping) else {}


def derive_lifecycle(
    *,
    candidate_count: int,
    analyzed_count: int,
    workflow_context: RecruitmentWorkflowContext | Mapping[str, Any] | None = None,
    management: Mapping[str, Any] | None = None,
) -> str:
    management_data = dict(management or {})
    if bool(management_data.get("archived")):
        return LIFECYCLE_ARCHIVED

    if isinstance(workflow_context, RecruitmentWorkflowContext):
        workflow = workflow_context
    else:
        workflow = workflow_context_from_payload(
            workflow_context if isinstance(workflow_context, Mapping) else None
        )

    if bool(getattr(workflow, "decision_recorded", False)):
        return LIFECYCLE_DECIDED
    if bool(getattr(workflow, "finalists_compared", False)):
        return LIFECYCLE_DECISION_READY
    if list(getattr(workflow, "interview_assessed_candidate_ids", []) or []) or list(
        getattr(workflow, "interview_prepared_candidate_ids", []) or []
    ):
        return LIFECYCLE_INTERVIEW
    if candidate_count <= 0:
        return LIFECYCLE_DRAFT
    if analyzed_count < candidate_count:
        return LIFECYCLE_ANALYZING
    return LIFECYCLE_REVIEW


@dataclass(frozen=True)
class ProjectPortfolioSummary:
    project_id: str
    title: str
    role_title: str
    project_type: str
    lifecycle: str
    priority: str
    owner: str
    location: str
    candidate_count: int
    analyzed_count: int
    interview_count: int
    finalist_count: int
    decision_recorded: bool
    updated_at: str
    source: str
    is_active: bool = False

    @property
    def progress_percent(self) -> int:
        if self.candidate_count <= 0:
            return 0
        return max(0, min(100, round(self.analyzed_count / self.candidate_count * 100)))

    @property
    def status(self) -> str:
        return LIFECYCLE_LABELS.get(self.lifecycle, "In progress")

    @property
    def archived(self) -> bool:
        return self.lifecycle == LIFECYCLE_ARCHIVED

    @property
    def next_action(self) -> str:
        if self.lifecycle == LIFECYCLE_ARCHIVED:
            return "Reopen project"
        if self.lifecycle == LIFECYCLE_DECIDED:
            return "Review decision record"
        if self.lifecycle == LIFECYCLE_DECISION_READY:
            return "Record final decision"
        if self.lifecycle == LIFECYCLE_INTERVIEW:
            return "Continue interviews"
        if self.lifecycle == LIFECYCLE_REVIEW:
            return "Review candidate evidence"
        if self.lifecycle == LIFECYCLE_ANALYZING:
            return "Continue analysis"
        return "Add candidates"

    @property
    def searchable_text(self) -> str:
        return " ".join(
            [
                self.title,
                self.role_title,
                self.location,
                self.owner,
                self.status,
                self.priority,
            ]
        ).casefold()


def summary_from_session(session: Any | None) -> ProjectPortfolioSummary | None:
    if session is None:
        return None
    management = management_from_session(session)
    workflow = management.get("workflow_context") if isinstance(management.get("workflow_context"), Mapping) else None
    candidate_count = _safe_int(getattr(session, "candidate_count", 0))
    analyzed_count = _safe_int(getattr(session, "analyzed_count", 0))
    role_title = _safe_text(getattr(session, "role_title", ""), "Active recruitment")
    job = getattr(session, "job", {}) or {}
    lifecycle = derive_lifecycle(
        candidate_count=candidate_count,
        analyzed_count=analyzed_count,
        workflow_context=workflow,
        management=management,
    )
    return ProjectPortfolioSummary(
        project_id=_safe_text(getattr(session, "session_id", ""), "active-recruitment"),
        title=_safe_text(management.get("display_name"), role_title),
        role_title=role_title,
        project_type="Recruitment",
        lifecycle=lifecycle,
        priority=_safe_text(management.get("priority"), "Normal"),
        owner=_safe_text(management.get("owner"), "Unassigned"),
        location=_safe_text(job.get("location") if isinstance(job, Mapping) else "", "Location not set"),
        candidate_count=candidate_count,
        analyzed_count=analyzed_count,
        interview_count=_safe_int(management.get("interview_count")),
        finalist_count=_safe_int(management.get("finalist_count")),
        decision_recorded=lifecycle == LIFECYCLE_DECIDED,
        updated_at=_safe_text(getattr(session, "updated_at", "")),
        source="session",
        is_active=True,
    )


def summary_from_stored(item: Mapping[str, Any]) -> ProjectPortfolioSummary:
    management = _management_from_mapping(item)
    workflow = item.get("workflow_context") if isinstance(item.get("workflow_context"), Mapping) else {}
    candidate_count = _safe_int(item.get("candidate_count"))
    analyzed_count = _safe_int(item.get("analyzed_count"), candidate_count)
    role_title = _safe_text(item.get("title"), "Untitled recruitment")
    job = item.get("job") if isinstance(item.get("job"), Mapping) else {}
    lifecycle = derive_lifecycle(
        candidate_count=candidate_count,
        analyzed_count=analyzed_count,
        workflow_context=workflow,
        management=management,
    )
    interview_ids = list(workflow.get("interview_assessed_candidate_ids") or []) if isinstance(workflow, Mapping) else []
    finalist_ids = list(workflow.get("finalist_candidate_ids") or []) if isinstance(workflow, Mapping) else []
    return ProjectPortfolioSummary(
        project_id=_safe_text(item.get("id"), "saved-recruitment"),
        title=_safe_text(management.get("display_name"), role_title),
        role_title=role_title,
        project_type="Recruitment",
        lifecycle=lifecycle,
        priority=_safe_text(management.get("priority"), "Normal"),
        owner=_safe_text(management.get("owner"), "Unassigned"),
        location=_safe_text(item.get("location") or job.get("location"), "Location not set"),
        candidate_count=candidate_count,
        analyzed_count=analyzed_count,
        interview_count=len(interview_ids),
        finalist_count=len(finalist_ids),
        decision_recorded=bool(workflow.get("decision_recorded")) if isinstance(workflow, Mapping) else False,
        updated_at=_safe_text(item.get("updated_at") or item.get("created_at")),
        source="storage",
        is_active=False,
    )


def build_project_summaries(
    active_session: Any | None,
    stored_recruitments: Sequence[Mapping[str, Any]] | None,
) -> tuple[ProjectPortfolioSummary, ...]:
    projects: list[ProjectPortfolioSummary] = []
    active = summary_from_session(active_session)
    if active is not None:
        projects.append(active)

    active_id = active.project_id if active else None
    for item in stored_recruitments or ():
        saved = summary_from_stored(item)
        if active_id and saved.project_id == active_id:
            continue
        projects.append(saved)

    return tuple(
        sorted(
            projects,
            key=lambda project: (
                project.archived,
                not project.is_active,
                -_timestamp(project.updated_at),
            ),
            reverse=False,
        )
    )


def _timestamp(value: str) -> float:
    text = _safe_text(value)
    if not text:
        return 0.0
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return 0.0


def filter_project_summaries(
    projects: Iterable[ProjectPortfolioSummary],
    *,
    query: str = "",
    lifecycle: str = "all",
    include_archived: bool = False,
    sort_by: str = "recent",
) -> tuple[ProjectPortfolioSummary, ...]:
    query_key = _safe_text(query).casefold()
    lifecycle_key = _safe_text(lifecycle, "all").casefold()
    selected = []
    for project in projects:
        if not include_archived and project.archived:
            continue
        if lifecycle_key not in {"", "all"} and project.lifecycle != lifecycle_key:
            continue
        if query_key and query_key not in project.searchable_text:
            continue
        selected.append(project)

    if sort_by == "oldest":
        selected.sort(key=lambda item: (_timestamp(item.updated_at), item.title.casefold()))
    elif sort_by == "name":
        selected.sort(key=lambda item: (item.title.casefold(), -_timestamp(item.updated_at)))
    elif sort_by == "progress":
        selected.sort(key=lambda item: (-item.progress_percent, -_timestamp(item.updated_at)))
    elif sort_by == "priority":
        priority_order = {"Critical": 0, "High": 1, "Normal": 2}
        selected.sort(key=lambda item: (priority_order.get(item.priority, 3), -_timestamp(item.updated_at)))
    else:
        selected.sort(key=lambda item: (-_timestamp(item.updated_at), item.title.casefold()))
    return tuple(selected)


def portfolio_metrics(projects: Iterable[ProjectPortfolioSummary]) -> dict[str, int]:
    items = tuple(projects)
    visible = tuple(item for item in items if not item.archived)
    return {
        "projects": len(visible),
        "candidates": sum(item.candidate_count for item in visible),
        "decision_ready": sum(
            item.lifecycle in {LIFECYCLE_DECISION_READY, LIFECYCLE_DECIDED}
            for item in visible
        ),
        "archived": sum(item.archived for item in items),
    }


def _normalise_priority(value: Any) -> str:
    text = _safe_text(value, "Normal").title()
    return text if text in PRIORITY_VALUES else "Normal"


def _write_management(
    project_id: str,
    *,
    display_name: str | None = None,
    owner: str | None = None,
    priority: str | None = None,
    archived: bool | None = None,
) -> dict[str, Any]:
    data = load_recruitment(project_id)
    # Validate the persisted canonical state before and after portfolio-only edits.
    session_from_project_payload(data)
    metadata = dict(data.get("metadata") or {})
    management = dict(metadata.get(PROJECT_MANAGEMENT_KEY) or {})
    management.setdefault("version", PROJECT_PORTFOLIO_VERSION)
    if display_name is not None:
        management["display_name"] = _safe_text(display_name, _safe_text(data.get("title"), "Untitled recruitment"))
    if owner is not None:
        management["owner"] = _safe_text(owner, "Unassigned")
    if priority is not None:
        management["priority"] = _normalise_priority(priority)
    if archived is not None:
        management["archived"] = bool(archived)
        management["archived_at"] = (
            datetime.now(timezone.utc).replace(microsecond=0).isoformat()
            if archived
            else ""
        )
    metadata[PROJECT_MANAGEMENT_KEY] = management
    data["metadata"] = metadata
    saved = save_recruitment(data)
    session_from_project_payload(saved)
    return saved


def update_project_details(
    project_id: str,
    *,
    display_name: str | None = None,
    owner: str | None = None,
    priority: str | None = None,
) -> dict[str, Any]:
    return _write_management(
        project_id,
        display_name=display_name,
        owner=owner,
        priority=priority,
    )


def archive_project(project_id: str) -> dict[str, Any]:
    return _write_management(project_id, archived=True)


def reopen_project(project_id: str) -> dict[str, Any]:
    return _write_management(project_id, archived=False)


def update_active_project_details(
    session: Any,
    workflow_context: RecruitmentWorkflowContext | None,
    *,
    display_name: str | None = None,
    owner: str | None = None,
    priority: str | None = None,
    archived: bool | None = None,
    analysis_batch: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if session is None:
        raise ValueError("An active recruitment session is required.")
    metadata = dict(getattr(session, "metadata", {}) or {})
    management = dict(metadata.get(PROJECT_MANAGEMENT_KEY) or {})
    management.setdefault("version", PROJECT_PORTFOLIO_VERSION)
    if display_name is not None:
        management["display_name"] = _safe_text(display_name, getattr(session, "role_title", "Recruitment"))
    if owner is not None:
        management["owner"] = _safe_text(owner, "Unassigned")
    if priority is not None:
        management["priority"] = _normalise_priority(priority)
    if archived is not None:
        management["archived"] = bool(archived)
        management["archived_at"] = (
            datetime.now(timezone.utc).replace(microsecond=0).isoformat()
            if archived
            else ""
        )
    if workflow_context is not None:
        management["workflow_context"] = {
            "decision_recorded": bool(workflow_context.decision_recorded),
            "finalists_compared": bool(workflow_context.finalists_compared),
            "interview_assessed_candidate_ids": list(workflow_context.interview_assessed_candidate_ids),
            "interview_prepared_candidate_ids": list(workflow_context.interview_prepared_candidate_ids),
        }
        management["interview_count"] = len(workflow_context.interview_assessed_candidate_ids)
        management["finalist_count"] = len(workflow_context.finalist_candidate_ids)
    metadata[PROJECT_MANAGEMENT_KEY] = management
    session.metadata = metadata
    return save_project(session, workflow_context, analysis_batch=analysis_batch)


def load_portfolio_project(project_id: str):
    """Public convenience wrapper used by the Project Hub and tests."""

    return load_project(project_id)
