from __future__ import annotations

import hashlib
from dataclasses import dataclass
from html import escape
from typing import Any

from talentcopilot.services.recruitment_workflow_service import RecruitmentWorkflowService
from talentcopilot.services.recruitment_workflow_state import get_workflow_context
from talentcopilot.ui.navigation_actions import request_page


@dataclass(frozen=True)
class WorkflowGroup:
    key: str
    label: str
    completed: bool
    current: bool
    available: bool
    reason: str = ""


_GROUP_DEFINITIONS = (
    ("analyze", "Analyze", ("setup", "role", "candidates", "analysis")),
    ("review", "Review candidates", ("candidate",)),
    ("compensation", "Compensation", ()),
    ("interview", "Interview", ("prepare", "assess")),
    ("decide", "Compare & decide", ("compare", "decide")),
)

_PAGE_GROUP = {
    "Recruitment Workspace": "analyze",
    "Recruitment Overview": "analyze",
    "Dashboard Perspective": "review",
    "Candidate Intelligence": "review",
    "Hiring Budget": "compensation",
    "Compensation & Budget": "compensation",
    "Interview Intelligence": "interview",
    "Comparison": "decide",
    "Decision Board": "decide",
}

_PREVIOUS_PAGE = {
    "Dashboard Perspective": "Recruitment Overview",
    "Candidate Intelligence": "Dashboard Perspective",
    "Hiring Budget": "Dashboard Perspective",
    "Compensation & Budget": "Dashboard Perspective",
    "Interview Intelligence": "Compensation & Budget",
    "Comparison": "Interview Intelligence",
    "Decision Board": "Comparison",
}


def _key(prefix: str, current_page: str, session) -> str:
    identity = f"{getattr(session, 'session_id', 'session')}|{current_page}|{prefix}"
    digest = hashlib.sha1(identity.encode("utf-8")).hexdigest()[:14]
    return f"workflow_{prefix}_{digest}"


def _compensation_state(session: Any) -> tuple[bool, bool, str]:
    if session is None:
        return False, False, "Create or open a recruitment first."
    analyses = list(getattr(session, "ranked_analyses", []) or [])
    if not analyses:
        return False, False, "Complete candidate analysis before compensation review."
    metadata = getattr(session, "metadata", {}) or {}
    budget_ready = bool(metadata.get("compensation_budget")) if isinstance(metadata, dict) else False
    candidate_store = metadata.get("candidate_compensation", {}) if isinstance(metadata, dict) else {}
    candidate_ready = bool(candidate_store) if isinstance(candidate_store, dict) else False
    completed = budget_ready and candidate_ready
    reason = "" if completed else "Define the position budget and document candidate expectations when available."
    return completed, True, reason


def aggregate_workflow_steps(
    states,
    *,
    current_page: str,
    session: Any = None,
) -> tuple[WorkflowGroup, ...]:
    """Collapse technical states into five recruiter-facing stages.

    Compensation is transversal: it becomes available after analysis and can be
    revisited before or after interview without changing talent scores.
    """

    by_key = {item.key: item for item in states}
    requested_group = _PAGE_GROUP.get(current_page, "")
    groups = []
    for key, label, member_keys in _GROUP_DEFINITIONS:
        if key == "compensation":
            completed, available, reason = _compensation_state(session)
            current = key == requested_group
        else:
            members = [by_key[item] for item in member_keys if item in by_key]
            completed = bool(members) and all(item.completed for item in members)
            current = key == requested_group or (
                not requested_group and any(item.current for item in members)
            )
            available = any(item.available for item in members)
            reason = next((item.reason for item in members if item.reason), "")
        groups.append(
            WorkflowGroup(
                key=key,
                label=label,
                completed=completed,
                current=current,
                available=available,
                reason=reason,
            )
        )
    return tuple(groups)


def _analysis_complete(states) -> bool:
    return bool(next((item.completed for item in states if item.key == "analysis"), False))


def _primary_route(service, states, context, *, current_page: str):
    if current_page in {"Recruitment Workspace", "Recruitment Overview"}:
        if _analysis_complete(states):
            return "Dashboard Perspective", "Open candidate dashboard"
        return "Recruitment Overview", "Continue analysis"
    if current_page == "Dashboard Perspective":
        return "Candidate Intelligence", "Open candidate detail"
    if current_page == "Candidate Intelligence":
        return "Compensation & Budget", "Record compensation expectations"
    if current_page in {"Hiring Budget", "Compensation & Budget"}:
        return "Interview Intelligence", "Prepare interview"
    if current_page == "Interview Intelligence":
        return "Comparison", "Compare finalists"
    if current_page == "Comparison":
        return "Decision Board", "Review final decision"
    next_step = service.next_step(states)
    if next_step is None:
        return "Decision Board", "Review final decision"
    return next_step.page_label, service.primary_action(context)


def render_recruitment_workflow_shell(session, *, current_page: str) -> None:
    import streamlit as st

    service = RecruitmentWorkflowService()
    context = get_workflow_context(session, current_page=current_page)
    states = service.resolve_steps(session, context, current_page=current_page)
    groups = aggregate_workflow_steps(states, current_page=current_page, session=session)

    completed_groups = sum(1 for item in groups if item.completed)
    progress = completed_groups / max(1, len(groups))
    selected = context.selected_candidate_name or "No candidate selected"
    current = next((item for item in groups if item.current), groups[0])
    # The page body owns the single "Next recommended action". The shared
    # workflow shell now communicates progress only, avoiding duplicate CTAs.

    st.markdown(
        """
        <style>
        .tc-workflow-anchor{position:sticky;top:5.35rem;z-index:980;margin:-.25rem 0 .65rem;padding-top:.1rem}
        .tc-workflow-shell{border:1px solid #D9E5F5;border-radius:14px;padding:9px 12px 8px;background:rgba(255,255,255,.975);box-shadow:0 8px 24px rgba(15,23,42,.07);backdrop-filter:blur(16px)}
        .tc-workflow-top{display:grid;grid-template-columns:minmax(210px,1.25fr) minmax(420px,3fr) auto;gap:12px;align-items:center}
        .tc-workflow-context{min-width:0}
        .tc-workflow-role{font-size:.82rem;font-weight:850;color:#0F172A;letter-spacing:-.012em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
        .tc-workflow-meta{font-size:.64rem;color:#64748B;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:1px}
        .tc-workflow-track{display:flex;align-items:center;gap:4px;min-width:0}
        .tc-workflow-step{position:relative;display:flex;align-items:center;justify-content:center;flex:1;min-width:0;height:31px;padding:0 7px;border-radius:9px;border:1px solid #E2E8F0;color:#64748B;background:#F8FAFC;font-size:.66rem;font-weight:780;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
        .tc-workflow-step.current{color:#1E3A8A;background:#EFF6FF;border-color:#93C5FD;box-shadow:inset 3px 0 0 #0EA5E9}
        .tc-workflow-step.done{color:#166534;background:#F0FDF4;border-color:#BBF7D0}
        .tc-workflow-step.locked{color:#8A99AD;background:#F8FAFC;border-style:dashed}
        .tc-workflow-state{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap}
        .tc-workflow-kicker{display:inline-flex;align-items:center;justify-content:center;min-height:1.65rem;border-radius:999px;padding:.16rem .55rem;font-size:.63rem;font-weight:850;color:#1E3A8A;background:#EFF6FF;border:1px solid #BFDBFE;white-space:nowrap}
        .tc-workflow-bar{height:3px;background:#E7EEF8;border-radius:999px;overflow:hidden;margin-top:7px}
        .tc-workflow-bar>span{display:block;height:100%;background:linear-gradient(90deg,#1D4ED8 0%,#0EA5E9 58%,#06B6D4 100%);border-radius:999px;box-shadow:0 0 14px rgba(14,165,233,.35)}
        .tc-workflow-action-note{display:flex;align-items:center;min-height:2.35rem;padding:.35rem .55rem;color:#52647D;font-size:.72rem}
        @media(max-width:1000px){.tc-workflow-top{grid-template-columns:1fr auto}.tc-workflow-track{grid-column:1 / -1;order:3}.tc-workflow-context{order:1}.tc-workflow-kicker{order:2}}
        @media(max-width:980px){.tc-workflow-anchor{position:relative;top:auto}.tc-workflow-track{display:grid;grid-template-columns:repeat(2,minmax(120px,1fr))}.tc-workflow-step{justify-content:flex-start}.tc-workflow-meta{white-space:normal}.tc-workflow-top{grid-template-columns:1fr}}
        </style>
        """,
        unsafe_allow_html=True,
    )

    steps_html = []
    for item in groups:
        css = "current" if item.current else "done" if item.completed else "locked" if not item.available else ""
        accessible_state = "Complete" if item.completed else "Current" if item.current else "Blocked" if not item.available else "Available"
        steps_html.append(
            f'<div class="tc-workflow-step {css}" title="{escape(item.reason or accessible_state)}">'
            f'<span class="tc-workflow-state">{accessible_state}</span>'
            f'{escape(item.label)}</div>'
        )

    st.markdown(
        f'<div class="tc-workflow-anchor"><div class="tc-workflow-shell">'
        f'<div class="tc-workflow-top">'
        f'<div class="tc-workflow-context"><div class="tc-workflow-role">{escape(context.role_title)}</div>'
        f'<div class="tc-workflow-meta">{escape(selected)} · {escape(current.label)}</div></div>'
        f'<div class="tc-workflow-track">{"".join(steps_html)}</div>'
        f'<div class="tc-workflow-kicker">{int(progress * 100)}% complete</div></div>'
        f'<div class="tc-workflow-bar" aria-label="Workflow progress"><span style="width:{int(progress * 100)}%"></span></div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    st.caption("Use the highlighted stage to understand progress; the page below contains the single contextual action.")


__all__ = ["WorkflowGroup", "aggregate_workflow_steps", "render_recruitment_workflow_shell"]
