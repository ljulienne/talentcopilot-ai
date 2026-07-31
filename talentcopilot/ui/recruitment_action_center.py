"""Recruitment Action Center UI for cross-project execution follow-up."""

from __future__ import annotations

from html import escape

from talentcopilot.models.recruitment_action_center import (
    ACTION_STATUS_DONE,
    ACTION_STATUS_IN_PROGRESS,
    ACTION_STATUS_OPEN,
)
from talentcopilot.services.recruitment_action_center import (
    RecruitmentActionCenterService,
    collect_action_states,
    update_active_action_status,
    update_saved_action_status,
)
from talentcopilot.services.recruitment_project_persistence import persistence_enabled
from talentcopilot.services.recruitment_project_portfolio import build_project_summaries
from talentcopilot.services.recruitment_workflow_state import get_workflow_context
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session
from talentcopilot.storage.recruitment_store import list_recruitments, load_recruitment
from talentcopilot.ui.design_system.components import enterprise_hero, metric_grid
from talentcopilot.ui.design_system.theme import apply_enterprise_theme
from talentcopilot.ui.navigation_actions import request_page
from talentcopilot.ui.project_hub import activate_recruitment_project


_STATUS_OPTIONS = ("All statuses", ACTION_STATUS_OPEN, ACTION_STATUS_IN_PROGRESS, ACTION_STATUS_DONE)
_SEVERITY_OPTIONS = ("All severities", "Critical", "High", "Medium", "Info")


def _styles() -> None:
    import streamlit as st

    st.markdown(
        """
        <style>
        .tc-action-intro{padding:.9rem 1rem;border:1px solid #d9e4f1;border-radius:15px;background:linear-gradient(135deg,#f9fbff,#f3f7fc);color:#53647b;font-size:.82rem;line-height:1.5;margin:.35rem 0 1rem}
        .tc-action-card{padding:1.05rem 1.1rem;border:1px solid #dce5f0;border-radius:18px;background:linear-gradient(180deg,#fff,#fbfdff);box-shadow:0 8px 24px rgba(15,23,42,.055);margin:.55rem 0 .35rem}
        .tc-action-top{display:flex;align-items:flex-start;justify-content:space-between;gap:1rem}.tc-action-title{color:#14213d;font-size:1rem;font-weight:850}.tc-action-meta{color:#728198;font-size:.7rem;margin-top:.16rem}
        .tc-action-summary{color:#52637a;font-size:.82rem;line-height:1.48;margin-top:.72rem}.tc-action-next{margin-top:.58rem;color:#234cb3;font-size:.8rem;font-weight:790}
        .tc-action-badge{display:inline-block;padding:.22rem .54rem;border-radius:999px;font-size:.67rem;font-weight:850;white-space:nowrap}.tc-action-critical{background:#fee2e2;color:#991b1b}.tc-action-high{background:#ffedd5;color:#9a3412}.tc-action-medium{background:#fef3c7;color:#92400e}.tc-action-info{background:#dbeafe;color:#1d4ed8}
        .tc-action-status{display:inline-block;margin-left:.35rem;padding:.2rem .5rem;border-radius:999px;background:#eef2ff;color:#4338ca;font-size:.65rem;font-weight:820}.tc-action-done{background:#dcfce7;color:#166534}.tc-action-progress{background:#cffafe;color:#0e7490}
        .tc-action-footer{margin-top:.62rem;padding-top:.58rem;border-top:1px solid #edf2f7;color:#6b7b90;font-size:.72rem}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _current_analysis_batch():
    try:
        import streamlit as st

        batch = st.session_state.get("analysis_batch")
        return batch if isinstance(batch, dict) else None
    except Exception:
        return None


def _open_action_project(action) -> None:
    import streamlit as st

    try:
        if not action.is_active:
            data = load_recruitment(action.project_id)
            activate_recruitment_project(data)
        request_page(
            "Recruitment Workspace",
            reason=f"Opened action project: {action.project_title}",
        )
        st.rerun()
    except Exception as exc:
        st.error("This recruitment project could not be opened.")
        st.caption(str(exc))


def _update_status(action, new_status: str, active_session, actor: str) -> None:
    import streamlit as st

    try:
        if action.is_active:
            if active_session is None or not persistence_enabled(active_session):
                st.warning("Save this project from Projects before tracking its action status.")
                return
            workflow = get_workflow_context(active_session, current_page="Action Center")
            update_active_action_status(
                active_session,
                workflow,
                action.action_id,
                new_status,
                actor=actor,
                analysis_batch=_current_analysis_batch(),
            )
        else:
            update_saved_action_status(
                action.project_id,
                action.action_id,
                new_status,
                actor=actor,
            )
        st.success(f"Action status updated to {new_status}.")
        st.rerun()
    except Exception as exc:
        st.error("The action status could not be updated.")
        st.caption(str(exc))


def _render_action(action, index: int, active_session, actor: str) -> None:
    import streamlit as st

    age = (
        f"{action.activity_age_days} day(s) since recorded activity"
        if action.activity_age_days is not None
        else "Activity age unavailable"
    )
    severity_class = action.severity.casefold()
    status_class = (
        " tc-action-done"
        if action.status == ACTION_STATUS_DONE
        else " tc-action-progress"
        if action.status == ACTION_STATUS_IN_PROGRESS
        else ""
    )
    state_meta = ""
    if action.status_updated_at:
        state_meta = f" · Status updated {action.status_updated_at}"
    if action.status_actor:
        state_meta += f" by {action.status_actor}"

    st.markdown(
        f"""
        <div class="tc-action-card">
          <div class="tc-action-top">
            <div>
              <div class="tc-action-title">{escape(action.project_title)}</div>
              <div class="tc-action-meta">{escape(action.role_title)} · {escape(action.category)} · {escape(action.owner)} · {escape(age)}</div>
            </div>
            <div>
              <span class="tc-action-badge tc-action-{escape(severity_class)}">{escape(action.severity)}</span>
              <span class="tc-action-status{status_class}">{escape(action.status)}</span>
            </div>
          </div>
          <div class="tc-action-summary">{escape(action.summary)}</div>
          <div class="tc-action-next">Next action · {escape(action.recommended_action)}</div>
          <div class="tc-action-footer">{escape(action.priority)} project priority · {escape(action.source)}{escape(state_meta)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    open_col, state_col, complete_col = st.columns([1.15, 1, 1])
    with open_col:
        if st.button(
            "Open project",
            key=f"action_center_open_{action.action_id}_{index}",
            use_container_width=True,
        ):
            _open_action_project(action)
    with state_col:
        if action.status == ACTION_STATUS_OPEN:
            if st.button(
                "Start action",
                key=f"action_center_start_{action.action_id}_{index}",
                use_container_width=True,
            ):
                _update_status(action, ACTION_STATUS_IN_PROGRESS, active_session, actor)
        elif action.status == ACTION_STATUS_IN_PROGRESS:
            if st.button(
                "Return to open",
                key=f"action_center_reopen_open_{action.action_id}_{index}",
                use_container_width=True,
            ):
                _update_status(action, ACTION_STATUS_OPEN, active_session, actor)
        else:
            if st.button(
                "Reopen action",
                key=f"action_center_reopen_{action.action_id}_{index}",
                use_container_width=True,
            ):
                _update_status(action, ACTION_STATUS_OPEN, active_session, actor)
    with complete_col:
        if action.status != ACTION_STATUS_DONE:
            if st.button(
                "Mark done",
                key=f"action_center_done_{action.action_id}_{index}",
                use_container_width=True,
            ):
                _update_status(action, ACTION_STATUS_DONE, active_session, actor)
        else:
            st.caption("Execution follow-up completed")


def render_recruitment_action_center() -> None:
    import streamlit as st

    apply_enterprise_theme()
    _styles()

    active_session = get_streamlit_session()
    try:
        stored = list_recruitments()
    except Exception:
        stored = []
    projects = build_project_summaries(active_session, stored)
    states = collect_action_states(active_session, stored)
    report = RecruitmentActionCenterService().build(
        projects,
        states_by_project=states,
    )

    enterprise_hero(
        "Recruitment Action Center",
        "Turn portfolio signals into accountable follow-up without changing candidate evidence, scores or ranks.",
        "Portfolio Execution",
    )

    metric_grid(
        [
            ("Open", str(report.open_actions), "Not started"),
            ("In progress", str(report.in_progress_actions), "Being handled"),
            ("High attention", str(report.critical_or_high_open_actions), "Critical or high"),
            ("Completed", str(report.done_actions), "Execution follow-up"),
        ]
    )

    st.markdown(
        f'<div class="tc-action-intro">{escape(report.limitation)}</div>',
        unsafe_allow_html=True,
    )

    if not report.actions:
        st.success("No open recruitment project currently requires an action.")
        if st.button("Open Projects", type="primary", key="action_center_empty_projects"):
            request_page("Projects", reason="Open or save a recruitment project.")
            st.rerun()
        return

    owners = tuple(sorted({action.owner for action in report.actions if action.owner}))
    filter_cols = st.columns([1.8, 1.15, 1.15, 1.15, 1.15])
    with filter_cols[0]:
        query = st.text_input(
            "Search actions",
            placeholder="Project, role, owner or action",
            label_visibility="collapsed",
            key="action_center_search",
        )
    with filter_cols[1]:
        selected_status = st.selectbox(
            "Status",
            _STATUS_OPTIONS,
            label_visibility="collapsed",
            key="action_center_status",
        )
    with filter_cols[2]:
        selected_severity = st.selectbox(
            "Severity",
            _SEVERITY_OPTIONS,
            label_visibility="collapsed",
            key="action_center_severity",
        )
    with filter_cols[3]:
        selected_owner = st.selectbox(
            "Owner",
            ("All owners", *owners),
            label_visibility="collapsed",
            key="action_center_owner",
        )
    with filter_cols[4]:
        actor = st.text_input(
            "Updated by",
            value="Recruiter",
            label_visibility="collapsed",
            key="action_center_actor",
            help="Name recorded with action-status changes.",
        )

    query_key = str(query or "").strip().casefold()
    visible = []
    for action in report.actions:
        if selected_status != "All statuses" and action.status != selected_status:
            continue
        if selected_severity != "All severities" and action.severity != selected_severity:
            continue
        if selected_owner != "All owners" and action.owner != selected_owner:
            continue
        searchable = " ".join(
            [
                action.project_title,
                action.role_title,
                action.owner,
                action.category,
                action.summary,
                action.recommended_action,
            ]
        ).casefold()
        if query_key and query_key not in searchable:
            continue
        visible.append(action)

    st.caption(f"{len(visible)} action{'s' if len(visible) != 1 else ''} shown")
    if not visible:
        st.info("No action matches the current filters.")
        return

    for index, action in enumerate(visible):
        _render_action(action, index, active_session, actor)


def render_action_center() -> None:
    render_recruitment_action_center()
