from __future__ import annotations

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
        return "·"
    return "○"


def render_recruitment_workflow_shell(session, *, current_page: str) -> None:
    import streamlit as st

    service = RecruitmentWorkflowService()
    context = get_workflow_context(session, current_page=current_page)
    states = service.resolve_steps(session, context, current_page=current_page)
    previous = service.previous_step(states)
    next_step = service.next_step(states)

    progress = sum(1 for item in states if item.completed) / max(1, len(states))
    selected = context.selected_candidate_name or "No candidate selected"

    st.markdown(
        """
        <style>
        .tc-workflow-shell {border:1px solid rgba(128,128,128,.22); border-radius:18px; padding:16px 18px; margin:8px 0 22px 0; background:rgba(255,255,255,.025)}
        .tc-workflow-head {display:flex; justify-content:space-between; gap:12px; align-items:flex-start; margin-bottom:12px}
        .tc-workflow-role {font-size:1.03rem; font-weight:700}
        .tc-workflow-meta {font-size:.82rem; opacity:.72}
        .tc-workflow-steps {display:grid; grid-template-columns:repeat(9,minmax(70px,1fr)); gap:6px; overflow-x:auto}
        .tc-workflow-step {padding:9px 7px; border-radius:11px; text-align:center; font-size:.72rem; line-height:1.2; border:1px solid rgba(128,128,128,.16)}
        .tc-workflow-step.current {border-color:rgba(72,120,255,.75); box-shadow:0 0 0 1px rgba(72,120,255,.2) inset}
        .tc-workflow-step.done {opacity:.8}
        .tc-workflow-step.locked {opacity:.38}
        @media(max-width:900px){.tc-workflow-steps{grid-template-columns:repeat(9,110px)}}
        </style>
        """,
        unsafe_allow_html=True,
    )

    steps_html = []
    for item in states:
        css = "current" if item.current else "done" if item.completed else "locked" if not item.available else ""
        symbol = _status_symbol(item.completed, item.current, item.available)
        steps_html.append(
            f'<div class="tc-workflow-step {css}" title="{escape(item.reason)}">'
            f'<div><strong>{symbol}</strong></div><div>{escape(item.label)}</div></div>'
        )

    st.markdown(
        f'<div class="tc-workflow-shell"><div class="tc-workflow-head">'
        f'<div><div class="tc-workflow-role">{escape(context.role_title)}</div>'
        f'<div class="tc-workflow-meta">{escape(selected)} · {int(progress * 100)}% complete</div></div>'
        f'<div class="tc-workflow-meta">Active workflow</div></div>'
        f'<div class="tc-workflow-steps">{"".join(steps_html)}</div></div>',
        unsafe_allow_html=True,
    )

    left, middle, right = st.columns([1, 3, 1.35])
    with left:
        if previous and st.button("← Previous", key=f"workflow_previous_{current_page}", use_container_width=True):
            request_page(previous.page_label, reason=f"Returned to {previous.label}.")
            st.rerun()
    with middle:
        current = next((item for item in states if item.current), states[0])
        if not current.available and current.reason:
            st.info(current.reason)
        elif next_step:
            st.caption(f"Next recommended step: **{next_step.label}**")
        else:
            st.caption("Workflow complete. Review the final decision record.")
    with right:
        if next_step:
            label = service.primary_action(context)
            if st.button(label + " →", type="primary", key=f"workflow_continue_{current_page}", use_container_width=True):
                request_page(next_step.page_label, reason=f"Continued to {next_step.label}.")
                st.rerun()
