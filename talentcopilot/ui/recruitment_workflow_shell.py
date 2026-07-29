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
    next_page, action_label = _primary_route(service, states, context, current_page=current_page)
    previous_page = _PREVIOUS_PAGE.get(current_page)

    st.markdown(
        """
        <style>
        .tc-workflow-anchor{position:sticky;top:.2rem;z-index:980;margin:-.45rem 0 1rem;padding-top:.15rem}
        .tc-workflow-shell{border:1px solid #D9E5F5;border-radius:16px;padding:12px 15px 11px;background:rgba(255,255,255,.985);box-shadow:0 12px 30px rgba(15,23,42,.08);backdrop-filter:blur(16px)}
        .tc-workflow-head{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;margin-bottom:7px}
        .tc-workflow-role{font-size:.93rem;font-weight:840;color:#0F172A;letter-spacing:-.015em}
        .tc-workflow-meta{font-size:.72rem;color:#52647D;line-height:1.35}
        .tc-workflow-kicker{display:inline-flex;align-items:center;border-radius:999px;padding:.24rem .58rem;font-size:.68rem;font-weight:820;color:#1E3A8A;background:#EFF6FF;border:1px solid #BFDBFE}
        .tc-workflow-bar{height:6px;background:#E7EEF8;border-radius:999px;overflow:hidden;margin:8px 0 10px}
        .tc-workflow-bar>span{display:block;height:100%;background:linear-gradient(90deg,#1D4ED8 0%,#0EA5E9 58%,#06B6D4 100%);border-radius:999px;box-shadow:0 0 14px rgba(14,165,233,.35)}
        .tc-workflow-steps{display:grid;grid-template-columns:repeat(5,minmax(105px,1fr));gap:6px}
        .tc-workflow-step{position:relative;padding:8px 9px;border-radius:10px;text-align:left;font-size:.68rem;line-height:1.22;border:1px solid #E2E8F0;color:#53657D;background:#F8FAFC;min-height:50px}
        .tc-workflow-step strong{display:block;font-size:.76rem;color:inherit}
        .tc-workflow-state{display:block;font-size:.55rem;text-transform:uppercase;letter-spacing:.08em;font-weight:850;margin-bottom:3px;color:#71839B}
        .tc-workflow-step.current{color:#1E3A8A;background:#EFF6FF;border-color:#93C5FD;font-weight:800;box-shadow:inset 3px 0 0 #0EA5E9}
        .tc-workflow-step.done{color:#166534;background:#F0FDF4;border-color:#BBF7D0}
        .tc-workflow-step.locked{color:#8292A8;background:#F8FAFC;border-style:dashed}
        @media(max-width:900px){.tc-workflow-steps{grid-template-columns:repeat(2,minmax(120px,1fr))}.tc-workflow-anchor{position:relative;top:auto}.tc-workflow-head{display:block}.tc-workflow-kicker{margin-top:7px}}
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
            f'<strong>{escape(item.label)}</strong></div>'
        )

    st.markdown(
        f'<div class="tc-workflow-anchor"><div class="tc-workflow-shell"><div class="tc-workflow-head">'
        f'<div><div class="tc-workflow-role">{escape(context.role_title)}</div>'
        f'<div class="tc-workflow-meta">{escape(selected)} · Current stage: {escape(current.label)}</div></div>'
        f'<div class="tc-workflow-kicker">{int(progress * 100)}% complete</div></div>'
        f'<div class="tc-workflow-bar" aria-label="Workflow progress"><span style="width:{int(progress * 100)}%"></span></div>'
        f'<div class="tc-workflow-steps">{"".join(steps_html)}</div></div></div>',
        unsafe_allow_html=True,
    )

    left, middle, right = st.columns([1.05, 2.65, 1.55])
    with left:
        if previous_page and st.button(
            "← Previous",
            key=_key("previous", current_page, session),
            use_container_width=True,
            help=f"Return to {previous_page}.",
        ):
            request_page(previous_page, reason=f"Returned to {previous_page}.")
            st.rerun()
    with middle:
        if not current.available and current.reason:
            st.info(current.reason)
        else:
            st.caption(f"Next recommended action: **{action_label}**")
    with right:
        if st.button(
            action_label + " →",
            type="primary",
            key=_key("continue", current_page, session),
            use_container_width=True,
            help=f"Continue to {next_page}.",
        ):
            request_page(next_page, reason=f"Continued to {next_page}.")
            st.rerun()


__all__ = ["WorkflowGroup", "aggregate_workflow_steps", "render_recruitment_workflow_shell"]
