from __future__ import annotations

import hashlib
from dataclasses import dataclass
from html import escape

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
    ("interview", "Interview", ("prepare", "assess")),
    ("decide", "Compare & decide", ("compare", "decide")),
)

_PAGE_GROUP = {
    "Recruitment Workspace": "analyze",
    "Recruitment Overview": "analyze",
    "Candidate Intelligence": "review",
    "Interview Intelligence": "interview",
    "Comparison": "decide",
    "Decision Board": "decide",
}

_PREVIOUS_PAGE = {
    "Recruitment Overview": "Recruitment Workspace",
    "Candidate Intelligence": "Recruitment Overview",
    "Interview Intelligence": "Candidate Intelligence",
    "Comparison": "Interview Intelligence",
    "Decision Board": "Comparison",
}


def _status_symbol(completed: bool, current: bool, available: bool) -> str:
    if completed:
        return "✓"
    if current:
        return "●"
    if not available:
        return "—"
    return "○"


def _key(prefix: str, current_page: str, session) -> str:
    identity = f"{getattr(session, 'session_id', 'session')}|{current_page}|{prefix}"
    digest = hashlib.sha1(identity.encode("utf-8")).hexdigest()[:14]
    return f"workflow_{prefix}_{digest}"


def aggregate_workflow_steps(states, *, current_page: str) -> tuple[WorkflowGroup, ...]:
    """Collapse nine technical workflow states into four recruiter-facing stages."""
    by_key = {item.key: item for item in states}
    requested_group = _PAGE_GROUP.get(current_page, "")
    groups = []
    for key, label, member_keys in _GROUP_DEFINITIONS:
        members = [by_key[item] for item in member_keys if item in by_key]
        completed = bool(members) and all(item.completed for item in members)
        current = key == requested_group or (not requested_group and any(item.current for item in members))
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
    if current_page == "Recruitment Workspace" and _analysis_complete(states):
        return "Recruitment Overview", "Open visual overview"
    if current_page == "Recruitment Overview":
        return "Candidate Intelligence", "Review candidates"
    next_step = service.next_step(states)
    if next_step is None:
        return "Decision Board", "Review final decision"
    return next_step.page_label, service.primary_action(context)


def render_recruitment_workflow_shell(session, *, current_page: str) -> None:
    import streamlit as st

    service = RecruitmentWorkflowService()
    context = get_workflow_context(session, current_page=current_page)
    states = service.resolve_steps(session, context, current_page=current_page)
    groups = aggregate_workflow_steps(states, current_page=current_page)

    completed_groups = sum(1 for item in groups if item.completed)
    progress = completed_groups / max(1, len(groups))
    selected = context.selected_candidate_name or "No candidate selected"
    current = next((item for item in groups if item.current), groups[0])
    next_page, action_label = _primary_route(service, states, context, current_page=current_page)
    previous_page = _PREVIOUS_PAGE.get(current_page)

    st.markdown(
        """
        <style>
        .tc-workflow-shell{border:1px solid #E2E8F0;border-radius:18px;padding:14px 16px;margin:4px 0 18px;background:rgba(255,255,255,.96);box-shadow:0 8px 24px rgba(15,23,42,.045)}
        .tc-workflow-head{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;margin-bottom:9px}
        .tc-workflow-role{font-size:1rem;font-weight:820;color:#111827;letter-spacing:-.015em}
        .tc-workflow-meta{font-size:.78rem;color:#64748B;line-height:1.4}
        .tc-workflow-kicker{display:inline-flex;align-items:center;gap:.35rem;border-radius:999px;padding:.26rem .6rem;font-size:.72rem;font-weight:780;color:#3730A3;background:#EEF2FF;border:1px solid #C7D2FE}
        .tc-workflow-bar{height:5px;background:#EEF2F7;border-radius:999px;overflow:hidden;margin:9px 0 11px}
        .tc-workflow-bar>span{display:block;height:100%;background:linear-gradient(90deg,#4F46E5,#0EA5E9);border-radius:999px}
        .tc-workflow-steps{display:grid;grid-template-columns:repeat(4,minmax(120px,1fr));gap:7px}
        .tc-workflow-step{position:relative;padding:10px 9px;border-radius:12px;text-align:left;font-size:.72rem;line-height:1.25;border:1px solid #E2E8F0;color:#64748B;background:#F8FAFC;min-height:58px}
        .tc-workflow-step strong{display:block;font-size:.82rem;color:inherit}
        .tc-workflow-state{display:block;font-size:.6rem;text-transform:uppercase;letter-spacing:.08em;font-weight:800;margin-bottom:4px;color:#94A3B8}
        .tc-workflow-step.current{color:#3730A3;background:#EEF2FF;border-color:#A5B4FC;font-weight:780;box-shadow:0 0 0 1px rgba(79,70,229,.06) inset}
        .tc-workflow-step.done{color:#166534;background:#F0FDF4;border-color:#BBF7D0}
        .tc-workflow-step.locked{color:#94A3B8;background:#F8FAFC;border-style:dashed}
        @media(max-width:760px){.tc-workflow-steps{grid-template-columns:repeat(2,minmax(120px,1fr))}.tc-workflow-head{display:block}.tc-workflow-kicker{margin-top:8px}}
        </style>
        """,
        unsafe_allow_html=True,
    )

    steps_html = []
    for item in groups:
        css = "current" if item.current else "done" if item.completed else "locked" if not item.available else ""
        accessible_state = "Complete" if item.completed else "Current" if item.current else "Blocked" if not item.available else "Next"
        steps_html.append(
            f'<div class="tc-workflow-step {css}" title="{escape(item.reason or accessible_state)}">'
            f'<span class="tc-workflow-state">{accessible_state}</span>'
            f'<strong>{escape(item.label)}</strong></div>'
        )

    st.markdown(
        f'<div class="tc-workflow-shell"><div class="tc-workflow-head">'
        f'<div><div class="tc-workflow-role">{escape(context.role_title)}</div>'
        f'<div class="tc-workflow-meta">{escape(selected)} · Current stage: {escape(current.label)}</div></div>'
        f'<div class="tc-workflow-kicker">{int(progress * 100)}% complete</div></div>'
        f'<div class="tc-workflow-bar" aria-label="Workflow progress"><span style="width:{int(progress * 100)}%"></span></div>'
        f'<div class="tc-workflow-steps">{"".join(steps_html)}</div></div>',
        unsafe_allow_html=True,
    )

    left, middle, right = st.columns([1.1, 2.6, 1.55])
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
