"""Persistent, domain-agnostic recruitment action center.

Release 8.7.0 converts portfolio workflow signals into one stable operational
action per non-archived project. It persists only execution status metadata and
never reads or mutates candidate score, rank, evidence, interview or compensation
fields.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping, Sequence

from talentcopilot.models.recruitment_action_center import (
    ACTION_STATUS_DONE,
    ACTION_STATUS_IN_PROGRESS,
    ACTION_STATUS_OPEN,
    ACTION_STATUS_VALUES,
    RecruitmentAction,
    RecruitmentActionCenterReport,
)
from talentcopilot.services.recruitment_portfolio_intelligence import (
    PRIORITY_ORDER,
    SEVERITY_ORDER,
    RecruitmentPortfolioIntelligenceService,
)
from talentcopilot.services.recruitment_project_persistence import (
    persistence_enabled,
    save_project,
    session_from_project_payload,
)
from talentcopilot.services.recruitment_project_portfolio import (
    LIFECYCLE_ARCHIVED,
    PROJECT_MANAGEMENT_KEY,
    ProjectPortfolioSummary,
)
from talentcopilot.storage.recruitment_store import (
    load_recruitment,
    save_recruitment,
)


ACTION_CENTER_KEY = "action_center"
ACTION_CENTER_VERSION = "talentcopilot-recruitment-action-center-v1"
STATUS_ORDER = {
    ACTION_STATUS_IN_PROGRESS: 0,
    ACTION_STATUS_OPEN: 1,
    ACTION_STATUS_DONE: 2,
}


def _utc_now(now: datetime | None = None) -> datetime:
    value = now or datetime.now(timezone.utc)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _normalise_status(value: Any, *, strict: bool = False) -> str:
    text = str(value or "").strip().casefold()
    aliases = {
        "open": ACTION_STATUS_OPEN,
        "to do": ACTION_STATUS_OPEN,
        "todo": ACTION_STATUS_OPEN,
        "in progress": ACTION_STATUS_IN_PROGRESS,
        "in_progress": ACTION_STATUS_IN_PROGRESS,
        "started": ACTION_STATUS_IN_PROGRESS,
        "done": ACTION_STATUS_DONE,
        "completed": ACTION_STATUS_DONE,
        "complete": ACTION_STATUS_DONE,
    }
    if text in aliases:
        return aliases[text]
    if strict:
        raise ValueError(f"Unsupported action status: {value}")
    return ACTION_STATUS_OPEN


def stable_action_id(project_id: str, category: str, recommended_action: str) -> str:
    """Return a deterministic ID for the current project action signal."""

    signature = "|".join(
        [
            str(project_id or "").strip(),
            str(category or "Workflow").strip().casefold(),
            " ".join(str(recommended_action or "").split()).casefold(),
        ]
    )
    digest = hashlib.sha256(signature.encode("utf-8")).hexdigest()[:18]
    return f"action-{digest}"


def _management(payload: Mapping[str, Any] | None) -> dict[str, Any]:
    data = dict(payload or {})
    metadata = data.get("metadata") if isinstance(data.get("metadata"), Mapping) else {}
    management = metadata.get(PROJECT_MANAGEMENT_KEY) if isinstance(metadata, Mapping) else {}
    return dict(management or {}) if isinstance(management, Mapping) else {}


def action_states_from_payload(payload: Mapping[str, Any] | None) -> dict[str, dict[str, str]]:
    management = _management(payload)
    action_center = management.get(ACTION_CENTER_KEY)
    if not isinstance(action_center, Mapping):
        return {}
    states = action_center.get("states")
    if not isinstance(states, Mapping):
        return {}

    cleaned: dict[str, dict[str, str]] = {}
    for action_id, raw_state in states.items():
        if not isinstance(raw_state, Mapping):
            continue
        cleaned[str(action_id)] = {
            "status": _normalise_status(raw_state.get("status")),
            "updated_at": str(raw_state.get("updated_at") or ""),
            "actor": str(raw_state.get("actor") or ""),
        }
    return cleaned


def action_states_from_session(session: Any | None) -> dict[str, dict[str, str]]:
    if session is None:
        return {}
    return action_states_from_payload({"metadata": getattr(session, "metadata", {}) or {}})


def collect_action_states(
    active_session: Any | None,
    stored_recruitments: Sequence[Mapping[str, Any]] | None,
) -> dict[str, dict[str, dict[str, str]]]:
    """Collect status overrides by project, with the active session taking precedence."""

    states: dict[str, dict[str, dict[str, str]]] = {}
    for item in stored_recruitments or ():
        project_id = str(item.get("id") or "").strip()
        if project_id:
            states[project_id] = action_states_from_payload(item)

    if active_session is not None:
        project_id = str(getattr(active_session, "session_id", "") or "").strip()
        if project_id:
            states[project_id] = action_states_from_session(active_session)
    return states


def _write_state(
    payload: dict[str, Any],
    *,
    action_id: str,
    status: str,
    actor: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    metadata = dict(payload.get("metadata") or {})
    management = dict(metadata.get(PROJECT_MANAGEMENT_KEY) or {})
    action_center = dict(management.get(ACTION_CENTER_KEY) or {})
    states = dict(action_center.get("states") or {})
    timestamp = _utc_now(now).replace(microsecond=0).isoformat()
    states[str(action_id)] = {
        "status": _normalise_status(status),
        "updated_at": timestamp,
        "actor": str(actor or "Recruiter").strip() or "Recruiter",
    }
    action_center["version"] = ACTION_CENTER_VERSION
    action_center["states"] = states
    management[ACTION_CENTER_KEY] = action_center
    metadata[PROJECT_MANAGEMENT_KEY] = management
    payload["metadata"] = metadata
    return payload


def update_saved_action_status(
    project_id: str,
    action_id: str,
    status: str,
    *,
    actor: str = "Recruiter",
    now: datetime | None = None,
) -> dict[str, Any]:
    normalised_status = _normalise_status(status, strict=True)
    data = load_recruitment(project_id)
    # Validate the canonical project before and after metadata-only writes.
    session_from_project_payload(data)
    updated = _write_state(
        dict(data),
        action_id=action_id,
        status=normalised_status,
        actor=actor,
        now=now,
    )
    saved = save_recruitment(updated)
    session_from_project_payload(saved)
    return saved


def update_active_action_status(
    session: Any,
    workflow_context: Any,
    action_id: str,
    status: str,
    *,
    actor: str = "Recruiter",
    analysis_batch: Mapping[str, Any] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    if session is None:
        raise ValueError("An active recruitment session is required.")
    normalised_status = _normalise_status(status, strict=True)
    if not persistence_enabled(session):
        raise ValueError("Save the project before updating action status.")

    payload = {"metadata": dict(getattr(session, "metadata", {}) or {})}
    _write_state(
        payload,
        action_id=action_id,
        status=normalised_status,
        actor=actor,
        now=now,
    )
    session.metadata = dict(payload["metadata"])
    return save_project(
        session,
        workflow_context,
        analysis_batch=analysis_batch,
    )


class RecruitmentActionCenterService:
    """Build one transparent action per non-archived recruitment project."""

    def build(
        self,
        projects: Iterable[ProjectPortfolioSummary],
        *,
        states_by_project: Mapping[str, Mapping[str, Mapping[str, str]]] | None = None,
        now: datetime | None = None,
    ) -> RecruitmentActionCenterReport:
        generated_at = _utc_now(now)
        open_projects = tuple(
            project
            for project in projects
            if project.lifecycle != LIFECYCLE_ARCHIVED
        )
        intelligence = RecruitmentPortfolioIntelligenceService().build(
            open_projects,
            now=generated_at,
        )
        alerts = {alert.project_id: alert for alert in intelligence.alerts}
        overrides = states_by_project or {}

        actions: list[RecruitmentAction] = []
        for project in open_projects:
            alert = alerts.get(project.project_id)
            if alert is not None:
                severity = alert.severity
                category = alert.category
                summary = alert.summary
                recommended_action = alert.recommended_action
                age_days = alert.activity_age_days
                source = "Portfolio alert"
            else:
                severity = "Info"
                category = "Workflow"
                summary = (
                    f"The project is in {project.status.lower()} with no current "
                    "operational alert."
                )
                recommended_action = project.next_action
                age_days = RecruitmentPortfolioIntelligenceService.activity_age_days(
                    project.updated_at,
                    now=generated_at,
                )
                source = "Lifecycle next action"

            action_id = stable_action_id(
                project.project_id,
                category,
                recommended_action,
            )
            state = dict(
                (overrides.get(project.project_id) or {}).get(action_id) or {}
            )
            actions.append(
                RecruitmentAction(
                    action_id=action_id,
                    project_id=project.project_id,
                    project_title=project.title,
                    role_title=project.role_title,
                    lifecycle=project.lifecycle,
                    severity=severity,
                    category=category,
                    summary=summary,
                    recommended_action=recommended_action,
                    owner=project.owner,
                    priority=project.priority,
                    activity_age_days=age_days,
                    status=_normalise_status(state.get("status")),
                    source=source,
                    is_active=project.is_active,
                    status_updated_at=str(state.get("updated_at") or ""),
                    status_actor=str(state.get("actor") or ""),
                )
            )

        actions.sort(
            key=lambda action: (
                STATUS_ORDER.get(action.status, 9),
                SEVERITY_ORDER.get(action.severity, 9),
                PRIORITY_ORDER.get(action.priority, 9),
                -(action.activity_age_days or 0),
                action.project_title.casefold(),
            )
        )
        actions_tuple = tuple(actions)
        open_like = tuple(
            action
            for action in actions_tuple
            if action.status != ACTION_STATUS_DONE
        )
        return RecruitmentActionCenterReport(
            generated_at=generated_at.replace(microsecond=0).isoformat(),
            total_actions=len(actions_tuple),
            open_actions=sum(action.status == ACTION_STATUS_OPEN for action in actions_tuple),
            in_progress_actions=sum(
                action.status == ACTION_STATUS_IN_PROGRESS
                for action in actions_tuple
            ),
            done_actions=sum(action.status == ACTION_STATUS_DONE for action in actions_tuple),
            critical_or_high_open_actions=sum(
                action.severity in {"Critical", "High"}
                for action in open_like
            ),
            unassigned_open_actions=sum(
                str(action.owner or "").strip().casefold()
                in {"", "unassigned", "not assigned", "none"}
                for action in open_like
            ),
            actions=actions_tuple,
        )
