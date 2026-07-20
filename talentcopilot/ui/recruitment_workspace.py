from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.recruitment_pipeline_service import RecruitmentPipelineService
from talentcopilot.services.recruitment_tasks_service import RecruitmentTasksService
from talentcopilot.services.recruitment_workspace_service import RecruitmentWorkspaceService
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session, set_streamlit_session
from talentcopilot.ui.design_system.components import enterprise_hero, metric_grid, next_action_card, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def _pipeline_deep_view(pipeline_report):
    import streamlit as st

    st.markdown('<div class="tc-card">', unsafe_allow_html=True)
    st.subheader("Recruitment Pipeline")
    st.progress(max(0, min(100, pipeline_report.overall_readiness)) / 100)
    st.caption(f"Overall pipeline readiness: {pipeline_report.overall_readiness}%")
    st.markdown("</div>", unsafe_allow_html=True)

    for stage in pipeline_report.stages:
        with st.expander(f"{stage.name} · {stage.status} · {stage.readiness}%"):
            c1, c2, c3 = st.columns(3)
            c1.metric("Status", stage.status)
            c2.metric("Count", stage.count)
            c3.metric("Readiness", f"{stage.readiness}%")
            st.write(f"**Recommended action:** {stage.action.title}")
            st.caption(f"Owner: {stage.action.owner} · Priority: {stage.action.priority}")
            st.write(stage.action.rationale)


def _candidate_table(report):
    import streamlit as st

    rows = [
        {
            "Interview Priority": c.interview_priority or c.rank,
            "Mission Rank": c.mission_rank or c.rank,
            "Candidate": c.name,
            "Mission Fit": c.match_score,
            "Career Fit": c.career_fit_score,
            "Confidence": c.confidence,
            "Stage": c.stage,
            "Recommendation": c.recommendation,
        }
        for c in report.candidates
    ]
    st.dataframe(rows, use_container_width=True) if rows else st.info("No candidates available yet.")


def _timeline(report):
    import streamlit as st

    for event in report.timeline:
        if event.status == "done":
            st.success(f"{event.label} — {event.description}")
        elif event.status == "active":
            st.info(f"{event.label} — {event.description}")
        else:
            st.caption(f"{event.label} — {event.description}")


def _task_board(task_report):
    import streamlit as st

    metric_grid([
        ("Tasks", str(task_report.total_tasks), "Total"),
        ("Open", str(task_report.open_tasks), "To do"),
        ("Blockers", str(len(task_report.blockers)), "Attention"),
    ])

    if task_report.blockers:
        section_title("Blockers")
        for blocker in task_report.blockers:
            st.warning(blocker)

    section_title("Task Board")
    rows = [
        {
            "Task": task.title,
            "Owner": task.owner,
            "Priority": task.priority,
            "Status": task.status,
            "Detail": task.detail,
        }
        for task in task_report.tasks
    ]
    st.dataframe(rows, use_container_width=True)

    for task in task_report.tasks:
        with st.expander(f"{task.priority} · {task.title}"):
            st.write(task.detail)
            st.caption(f"Owner: {task.owner} · Status: {task.status}")


def render_recruitment_workspace():
    import streamlit as st

    apply_enterprise_theme()

    session = get_streamlit_session()
    workspace_report = RecruitmentWorkspaceService().build(session)
    pipeline_report = RecruitmentPipelineService().build(session)
    task_report = RecruitmentTasksService().build(session)

    enterprise_hero(
        "Recruitment Workspace",
        "One recruitment, one evidence base, one consistent interview priority.",
        "Recruitment",
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Load Enterprise Demo"):
            session = create_demo_recruitment_session()
            set_streamlit_session(session)
            workspace_report = RecruitmentWorkspaceService().build(session)
            pipeline_report = RecruitmentPipelineService().build(session)
            task_report = RecruitmentTasksService().build(session)
            st.success("Enterprise demo loaded.")
    with col2:
        st.caption(f"Active recruitment: {workspace_report.role_title} · Status: {workspace_report.status}")

    metric_grid([
        ("Role", workspace_report.role_title, workspace_report.status),
        ("Candidates", str(workspace_report.candidates_count), "Total"),
        ("Analyzed", str(workspace_report.analyzed_count), "AI completed"),
        ("Open Tasks", str(task_report.open_tasks), "Operational"),
    ])

    tab_pipeline, tab_candidates, tab_timeline, tab_actions = st.tabs([
        "Pipeline",
        "Candidates",
        "Timeline",
        "Actions & Tasks",
    ])

    with tab_pipeline:
        _pipeline_deep_view(pipeline_report)

    with tab_candidates:
        section_title(
            "Candidates in this recruitment",
            "Mission Fit is the objective match. Interview Priority is the recommended review order.",
        )
        _candidate_table(workspace_report)

    with tab_timeline:
        section_title("Recruitment Timeline")
        _timeline(workspace_report)

    with tab_actions:
        _task_board(task_report)
        if task_report.tasks:
            first = task_report.tasks[0]
            next_action_card(first.title, first.detail, "Continue")
