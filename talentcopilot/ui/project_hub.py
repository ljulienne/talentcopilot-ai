from __future__ import annotations

from datetime import datetime
from html import escape
from typing import Any, Mapping, Sequence

from talentcopilot.models.recruitment_session import RecruitmentSession
from talentcopilot.models.recruitment_workflow import RecruitmentWorkflowContext
from talentcopilot.services.recruitment_project_persistence import (
    load_project,
    persistence_enabled,
    save_project,
    session_from_project_payload,
    workflow_context_from_payload,
)
from talentcopilot.services.recruitment_project_portfolio import (
    LIFECYCLE_ANALYZING,
    LIFECYCLE_ARCHIVED,
    LIFECYCLE_DECIDED,
    LIFECYCLE_DECISION_READY,
    LIFECYCLE_DRAFT,
    LIFECYCLE_INTERVIEW,
    LIFECYCLE_LABELS,
    LIFECYCLE_REVIEW,
    PRIORITY_VALUES,
    PROJECT_MANAGEMENT_KEY,
    PROJECT_PORTFOLIO_VERSION,
    ProjectPortfolioSummary,
    archive_project,
    build_project_summaries as _build_project_summaries,
    filter_project_summaries,
    portfolio_metrics,
    reopen_project,
    summary_from_session as _summary_from_session,
    summary_from_stored as _summary_from_stored,
    update_active_project_details,
    update_project_details,
)
from talentcopilot.services.streamlit_session_bridge import (
    get_streamlit_session,
    set_streamlit_session,
)
from talentcopilot.services.recruitment_workflow_state import WORKFLOW_CONTEXT_KEY
from talentcopilot.storage.recruitment_store import list_recruitments
from talentcopilot.ui.navigation_actions import request_page


# Compatibility aliases retained for historical tests and downstream imports.
ProjectSummary = ProjectPortfolioSummary


def summary_from_session(session: Any | None) -> ProjectSummary | None:
    return _summary_from_session(session)


def summary_from_stored(item: Mapping[str, Any]) -> ProjectSummary:
    return _summary_from_stored(item)


def build_project_summaries(
    active_session: Any | None,
    stored_recruitments: Sequence[Mapping[str, Any]] | None,
) -> tuple[ProjectSummary, ...]:
    return _build_project_summaries(active_session, stored_recruitments)


def _display_date(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return "Not dated"
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return parsed.strftime("%d %b %Y · %H:%M")
    except ValueError:
        return text


def session_from_recruitment_data(data: Mapping[str, Any]) -> RecruitmentSession:
    """Backward-compatible public adapter used by historical tests and routes."""

    return session_from_project_payload(data)


def activate_recruitment_project(data: Mapping[str, Any]) -> RecruitmentSession:
    session = session_from_project_payload(data)
    workflow = workflow_context_from_payload(data.get("workflow_context"))
    if not workflow.session_id:
        workflow.session_id = session.session_id
    if not workflow.role_title or workflow.role_title == "Recruitment":
        workflow.role_title = session.role_title
    set_streamlit_session(session)
    try:
        import streamlit as st

        st.session_state[WORKFLOW_CONTEXT_KEY] = workflow
        st.session_state["recruitment_context"] = {
            "session_id": session.session_id,
            "title": session.role_title,
            "job_title": session.role_title,
            "candidate_count": session.candidate_count,
            "analyzed_count": session.analyzed_count,
            **{key: value for key, value in session.job.items() if key != "title"},
        }
        st.session_state["analysis_batch"] = data.get("analysis_batch") or {"success": True, "results": []}
        st.session_state["current_recruitment"] = session
    except Exception:
        pass
    return session


def _current_workflow(session: RecruitmentSession | None) -> RecruitmentWorkflowContext:
    try:
        import streamlit as st

        workflow = st.session_state.get(WORKFLOW_CONTEXT_KEY)
        if isinstance(workflow, RecruitmentWorkflowContext):
            return workflow
    except Exception:
        pass
    return RecruitmentWorkflowContext(
        session_id=str(getattr(session, "session_id", "") or ""),
        role_title=str(getattr(session, "role_title", "Recruitment") or "Recruitment"),
    )




def _sync_active_workflow_summary(session: RecruitmentSession | None) -> None:
    if session is None:
        return
    workflow = _current_workflow(session)
    metadata = dict(getattr(session, "metadata", {}) or {})
    management = dict(metadata.get(PROJECT_MANAGEMENT_KEY) or {})
    management.setdefault("version", PROJECT_PORTFOLIO_VERSION)
    management["workflow_context"] = {
        "decision_recorded": bool(workflow.decision_recorded),
        "finalists_compared": bool(workflow.finalists_compared),
        "interview_assessed_candidate_ids": list(workflow.interview_assessed_candidate_ids),
        "interview_prepared_candidate_ids": list(workflow.interview_prepared_candidate_ids),
    }
    management["interview_count"] = len(workflow.interview_assessed_candidate_ids)
    management["finalist_count"] = len(workflow.finalist_candidate_ids)
    metadata[PROJECT_MANAGEMENT_KEY] = management
    session.metadata = metadata

def _current_analysis_batch() -> Mapping[str, Any] | None:
    try:
        import streamlit as st

        batch = st.session_state.get("analysis_batch")
        return batch if isinstance(batch, Mapping) else None
    except Exception:
        return None


def _save_active_project(session: RecruitmentSession) -> bool:
    try:
        save_project(
            session,
            _current_workflow(session),
            analysis_batch=_current_analysis_batch(),
        )
        return True
    except Exception:
        return False


def _styles() -> None:
    import streamlit as st

    st.markdown(
        """
        <style>
        .tc-project-hero{padding:1.6rem 1.8rem;border:1px solid #b9cbe2;border-radius:24px;background:linear-gradient(135deg,#1f365d,#315a8b 55%,#317287);color:#fff;margin-bottom:1.1rem;box-shadow:0 16px 36px rgba(31,54,93,.16)}
        .tc-project-hero h1{margin:0 0 .38rem;font-size:2.25rem;letter-spacing:-.04em}.tc-project-hero p{margin:0;color:#dceafa;max-width:760px}
        .tc-project-card{padding:1.05rem 1.1rem;border:1px solid #dce5f0;border-radius:18px;background:linear-gradient(180deg,#fff,#fbfdff);min-height:226px;box-shadow:0 8px 24px rgba(15,23,42,.05)}
        .tc-project-card h3{margin:.5rem 0 .15rem;color:#14213d;font-size:1.08rem}.tc-project-card p{color:#607086;font-size:.87rem;margin:.18rem 0}
        .tc-project-badge{display:inline-block;padding:.22rem .55rem;border-radius:999px;background:#dbeafe;color:#1d4ed8;font-size:.7rem;font-weight:800;letter-spacing:.01em}
        .tc-project-active{background:#dcfce7;color:#166534}.tc-project-archived{background:#e2e8f0;color:#475569}.tc-project-ready{background:#ede9fe;color:#6d28d9}.tc-project-interview{background:#cffafe;color:#0e7490}.tc-project-priority{float:right;color:#475569;font-size:.72rem;font-weight:800}
        .tc-project-progress{height:7px;border-radius:999px;background:#e8eef6;overflow:hidden;margin:.75rem 0 .55rem}.tc-project-progress span{display:block;height:100%;background:linear-gradient(90deg,#3457e5,#22b8cf);border-radius:999px}
        .tc-project-meta{margin-top:.65rem;padding-top:.6rem;border-top:1px solid #edf2f7;color:#6b7b90;font-size:.78rem}
        .tc-project-empty{padding:1.5rem;border:1px dashed #c8d5e5;border-radius:18px;background:#f8fbff;color:#52637a;text-align:center}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _badge_class(project: ProjectSummary) -> str:
    if project.archived:
        return " tc-project-archived"
    if project.is_active:
        return " tc-project-active"
    if project.lifecycle in {LIFECYCLE_DECISION_READY, LIFECYCLE_DECIDED}:
        return " tc-project-ready"
    if project.lifecycle == LIFECYCLE_INTERVIEW:
        return " tc-project-interview"
    return ""


def _open_project(project: ProjectSummary) -> None:
    import streamlit as st

    if project.source == "storage":
        try:
            session, workflow, data = load_project(project.project_id)
            set_streamlit_session(session)
            st.session_state[WORKFLOW_CONTEXT_KEY] = workflow
            st.session_state["recruitment_context"] = {
                "session_id": session.session_id,
                "title": session.role_title,
                "job_title": session.role_title,
                "candidate_count": session.candidate_count,
                "analyzed_count": session.analyzed_count,
                **{key: value for key, value in session.job.items() if key != "title"},
            }
            st.session_state["analysis_batch"] = data.get("analysis_batch") or {"success": True, "results": []}
            st.session_state["current_recruitment"] = session
            st.success(f"{project.title} is now the active recruitment.")
        except Exception as exc:
            st.error("This saved project could not be opened.")
            st.caption(str(exc))
            return
    request_page("Recruitment Workspace", reason=f"Opened project: {project.title}")
    st.rerun()


def _manage_project(project: ProjectSummary, active_session: RecruitmentSession | None, index: int) -> None:
    import streamlit as st

    with st.expander("Manage project", expanded=False):
        name = st.text_input(
            "Project name",
            value=project.title,
            key=f"project_name_{project.project_id}_{index}",
        )
        owner = st.text_input(
            "Owner",
            value="" if project.owner == "Unassigned" else project.owner,
            placeholder="Recruiter or hiring lead",
            key=f"project_owner_{project.project_id}_{index}",
        )
        priority_index = PRIORITY_VALUES.index(project.priority) if project.priority in PRIORITY_VALUES else 0
        priority = st.selectbox(
            "Priority",
            PRIORITY_VALUES,
            index=priority_index,
            key=f"project_priority_{project.project_id}_{index}",
        )
        if st.button(
            "Save project details",
            key=f"project_details_save_{project.project_id}_{index}",
            use_container_width=True,
        ):
            try:
                if project.is_active and active_session is not None:
                    update_active_project_details(
                        active_session,
                        _current_workflow(active_session),
                        display_name=name,
                        owner=owner,
                        priority=priority,
                        analysis_batch=_current_analysis_batch(),
                    )
                else:
                    update_project_details(
                        project.project_id,
                        display_name=name,
                        owner=owner,
                        priority=priority,
                    )
                st.success("Project details updated.")
                st.rerun()
            except Exception as exc:
                st.error("Project details could not be updated.")
                st.caption(str(exc))

        if not project.is_active:
            st.divider()
            if project.archived:
                if st.button(
                    "Reopen project",
                    key=f"project_reopen_{project.project_id}_{index}",
                    use_container_width=True,
                ):
                    try:
                        reopen_project(project.project_id)
                        st.success("Project reopened.")
                        st.rerun()
                    except Exception as exc:
                        st.error("The project could not be reopened.")
                        st.caption(str(exc))
            else:
                confirm = st.checkbox(
                    "I confirm that this project should be archived",
                    key=f"project_archive_confirm_{project.project_id}_{index}",
                )
                if st.button(
                    "Archive project",
                    key=f"project_archive_{project.project_id}_{index}",
                    disabled=not confirm,
                    use_container_width=True,
                ):
                    try:
                        archive_project(project.project_id)
                        st.success("Project archived. Its decision evidence remains preserved.")
                        st.rerun()
                    except Exception as exc:
                        st.error("The project could not be archived.")
                        st.caption(str(exc))


def _render_project_card(
    project: ProjectSummary,
    index: int,
    active_session: RecruitmentSession | None,
) -> None:
    import streamlit as st

    st.markdown(
        f"""
        <div class="tc-project-card">
          <span class="tc-project-badge{_badge_class(project)}">{escape(project.status)}</span>
          <span class="tc-project-priority">{escape(project.priority)} priority</span>
          <h3>{escape(project.title)}</h3>
          <p>{escape(project.role_title)} · {escape(project.location)}</p>
          <p>Owner: <strong>{escape(project.owner)}</strong></p>
          <div class="tc-project-progress"><span style="width:{project.progress_percent}%"></span></div>
          <p><strong>{project.analyzed_count}/{project.candidate_count}</strong> candidates analysed · {project.interview_count} interviewed · {project.finalist_count} finalists</p>
          <div class="tc-project-meta">Updated {escape(_display_date(project.updated_at))}<br>Next: {escape(project.next_action)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if project.archived:
        st.caption("Reopen this project before continuing the recruitment workflow.")
    else:
        label = "Continue project" if project.is_active else "Open project"
        if st.button(
            label,
            key=f"project_hub_open_{project.project_id}_{index}",
            use_container_width=True,
        ):
            _open_project(project)
    _manage_project(project, active_session, index)


def render_project_hub() -> None:
    import streamlit as st

    _styles()
    active_session = get_streamlit_session()
    _sync_active_workflow_summary(active_session)
    try:
        stored = list_recruitments()
    except Exception:
        stored = []
    projects = build_project_summaries(active_session, stored)
    metrics = portfolio_metrics(projects)

    st.markdown(
        """
        <div class="tc-project-hero">
          <h1>Recruitment portfolio</h1>
          <p>Find, resume and govern every evidence-led recruitment decision from one workspace.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Open projects", metrics["projects"], "Excludes archived")
    c2.metric("Candidates", metrics["candidates"], "Across open projects")
    c3.metric("Decision ready", metrics["decision_ready"], "Ready or decided")
    c4.metric("Archived", metrics["archived"], "Evidence retained")

    if active_session is not None:
        saved = persistence_enabled(active_session)
        with st.container(border=True):
            status_col, action_col = st.columns([2.2, 1])
            with status_col:
                st.markdown("**Project continuity**")
                st.caption(
                    "Saved projects preserve official candidate IDs, scores, ranks, "
                    "interview evidence, compensation inputs and final-decision history."
                )
                if saved:
                    st.success("This project is saved. New workflow updates are persisted automatically.")
                else:
                    st.info("This project is active only in the current browser session until you save it.")
            with action_col:
                button_label = "Save latest state" if saved else "Save project"
                if st.button(
                    button_label,
                    type="primary" if not saved else "secondary",
                    key="project_hub_save_active",
                    use_container_width=True,
                ):
                    if _save_active_project(active_session):
                        st.success("Project saved successfully.")
                        st.rerun()
                    else:
                        st.error("The active project could not be saved.")

    if not projects:
        st.markdown(
            '<div class="tc-project-empty"><strong>No project is available yet.</strong><br>Start a recruitment from the Executive Brief.</div>',
            unsafe_allow_html=True,
        )
        if st.button("Return to Executive Brief", use_container_width=False):
            request_page("Executive Brief", reason="Start a new HR diagnostic.")
            st.rerun()
        return

    st.markdown("### Find a project")
    search_col, status_col, sort_col, archive_col = st.columns([2.2, 1.25, 1.25, .9])
    with search_col:
        query = st.text_input(
            "Search",
            placeholder="Role, project name, location or owner",
            label_visibility="collapsed",
            key="project_portfolio_search",
        )
    lifecycle_options = {
        "All stages": "all",
        "Draft": LIFECYCLE_DRAFT,
        "Analyzing": LIFECYCLE_ANALYZING,
        "Review": LIFECYCLE_REVIEW,
        "Interview": LIFECYCLE_INTERVIEW,
        "Decision ready": LIFECYCLE_DECISION_READY,
        "Decided": LIFECYCLE_DECIDED,
        "Archived": LIFECYCLE_ARCHIVED,
    }
    with status_col:
        lifecycle_label = st.selectbox(
            "Stage",
            tuple(lifecycle_options),
            label_visibility="collapsed",
            key="project_portfolio_stage",
        )
    sort_options = {
        "Recently updated": "recent",
        "Oldest updated": "oldest",
        "Project name": "name",
        "Progress": "progress",
        "Priority": "priority",
    }
    with sort_col:
        sort_label = st.selectbox(
            "Sort",
            tuple(sort_options),
            label_visibility="collapsed",
            key="project_portfolio_sort",
        )
    with archive_col:
        include_archived = st.checkbox(
            "Archived",
            value=lifecycle_options[lifecycle_label] == LIFECYCLE_ARCHIVED,
            key="project_portfolio_archived",
        )

    visible_projects = filter_project_summaries(
        projects,
        query=query,
        lifecycle=lifecycle_options[lifecycle_label],
        include_archived=include_archived or lifecycle_options[lifecycle_label] == LIFECYCLE_ARCHIVED,
        sort_by=sort_options[sort_label],
    )

    st.caption(f"{len(visible_projects)} project{'s' if len(visible_projects) != 1 else ''} shown")
    if not visible_projects:
        st.markdown(
            '<div class="tc-project-empty">No project matches the current search and filters.</div>',
            unsafe_allow_html=True,
        )
        return

    for row_start in range(0, len(visible_projects), 3):
        row = visible_projects[row_start : row_start + 3]
        columns = st.columns(3)
        for offset, (column, project) in enumerate(zip(columns, row)):
            with column:
                _render_project_card(project, row_start + offset, active_session)


def render_projects() -> None:
    render_project_hub()
