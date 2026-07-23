from __future__ import annotations

import hashlib
from html import escape

from talentcopilot.services.recruitment_workflow_service import RecruitmentWorkflowService
from talentcopilot.services.recruitment_workflow_state import get_workflow_context
from talentcopilot.ui.navigation_actions import request_page


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


def render_recruitment_workflow_shell(session, *, current_page: str) -> None:
    import streamlit as st

    service = RecruitmentWorkflowService()
    context = get_workflow_context(session, current_page=current_page)
    states = service.resolve_steps(session, context, current_page=current_page)
    previous = service.previous_step(states)
    next_step = service.next_step(states)

    progress = sum(1 for item in states if item.completed) / max(1, len(states))
    selected = context.selected_candidate_name or "No candidate selected"
    current = next((item for item in states if item.current), states[0])

    st.markdown(
        """
        <style>
        .tc-workflow-shell{border:1px solid #E2E8F0;border-radius:18px;padding:15px 16px;margin:4px 0 20px;background:rgba(255,255,255,.96);box-shadow:0 8px 24px rgba(15,23,42,.055)}
        .tc-workflow-head{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;margin-bottom:11px}
        .tc-workflow-role{font-size:1rem;font-weight:820;color:#111827;letter-spacing:-.015em}
        .tc-workflow-meta{font-size:.78rem;color:#64748B;line-height:1.4}
        .tc-workflow-kicker{display:inline-flex;align-items:center;gap:.35rem;border-radius:999px;padding:.26rem .6rem;font-size:.72rem;font-weight:780;color:#3730A3;background:#EEF2FF;border:1px solid #C7D2FE}
        .tc-workflow-bar{height:5px;background:#EEF2F7;border-radius:999px;overflow:hidden;margin:10px 0 12px}
        .tc-workflow-bar>span{display:block;height:100%;background:linear-gradient(90deg,#4F46E5,#0EA5E9);border-radius:999px}
        .tc-workflow-steps{display:grid;grid-template-columns:repeat(9,minmax(78px,1fr));gap:6px;overflow-x:auto;padding-bottom:2px}
        .tc-workflow-step{padding:8px 7px;border-radius:11px;text-align:center;font-size:.70rem;line-height:1.25;border:1px solid #E2E8F0;color:#64748B;background:#F8FAFC;min-height:52px}
        .tc-workflow-step strong{display:block;font-size:.82rem;margin-bottom:2px}
        .tc-workflow-step.current{color:#3730A3;background:#EEF2FF;border-color:#A5B4FC;font-weight:780;box-shadow:0 0 0 1px rgba(79,70,229,.06) inset}
        .tc-workflow-step.done{color:#166534;background:#F0FDF4;border-color:#BBF7D0}
        .tc-workflow-step.locked{color:#94A3B8;background:#F8FAFC;border-style:dashed}
        @media(max-width:900px){.tc-workflow-steps{grid-template-columns:repeat(9,112px)}}
        </style>
        """,
        unsafe_allow_html=True,
    )

    steps_html = []
    for item in states:
        css = "current" if item.current else "done" if item.completed else "locked" if not item.available else ""
        symbol = _status_symbol(item.completed, item.current, item.available)
        accessible_state = "Complete" if item.completed else "Current" if item.current else "Blocked" if not item.available else "Pending"
        steps_html.append(
            f'<div class="tc-workflow-step {css}" title="{escape(item.reason or accessible_state)}">'
            f'<strong aria-hidden="true">{symbol}</strong><span>{escape(item.label)}</span>'
            f'<span style="position:absolute;left:-9999px">{accessible_state}</span></div>'
        )

    st.markdown(
        f'<div class="tc-workflow-shell"><div class="tc-workflow-head">'
        f'<div><div class="tc-workflow-role">{escape(context.role_title)}</div>'
        f'<div class="tc-workflow-meta">{escape(selected)} · Current stage: {escape(current.label)}</div></div>'
        f'<div class="tc-workflow-kicker">● {int(progress * 100)}% complete</div></div>'
        f'<div class="tc-workflow-bar" aria-label="Workflow progress"><span style="width:{int(progress * 100)}%"></span></div>'
        f'<div class="tc-workflow-steps">{"".join(steps_html)}</div></div>',
        unsafe_allow_html=True,
    )

    left, middle, right = st.columns([1, 3, 1.45])
    with left:
        if previous and st.button(
            "← Previous",
            key=_key("previous", current_page, session),
            use_container_width=True,
        ):
            request_page(previous.page_label, reason=f"Returned to {previous.label}.")
            st.rerun()
    with middle:
        if not current.available and current.reason:
            st.info(current.reason)
        elif next_step:
            st.caption(f"Next recommended step: **{next_step.label}**")
        else:
            st.caption("Workflow complete. Review the final decision record.")
    with right:
        if next_step:
            label = service.primary_action(context)
            if st.button(
                label + " →",
                type="primary",
                key=_key("continue", current_page, session),
                use_container_width=True,
            ):
                request_page(next_step.page_label, reason=f"Continued to {next_step.label}.")
                st.rerun()
