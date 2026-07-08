from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.recruitment_workspace_service import RecruitmentWorkspaceService
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session, set_streamlit_session
from talentcopilot.ui.design_system.components import enterprise_hero, metric_grid, next_action_card, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def _pipeline(report):
    import streamlit as st

    st.markdown('<div class="tc-card">', unsafe_allow_html=True)
    st.subheader("Pipeline")
    cols = st.columns(len(report.pipeline) if report.pipeline else 1)
    for col, stage in zip(cols, report.pipeline):
        with col:
            if stage.status == "done":
                st.success(stage.name)
            elif stage.status == "active":
                st.info(stage.name)
            else:
                st.caption(stage.name)
            st.metric("Count", stage.count)
    st.markdown("</div>", unsafe_allow_html=True)


def _candidate_table(report):
    import streamlit as st

    rows = [
        {
            "Rank": c.rank,
            "Candidate": c.name,
            "Stage": c.stage,
            "Match": c.match_score,
            "Recommendation": c.recommendation,
        }
        for c in report.candidates
    ]

    if rows:
        st.dataframe(rows, use_container_width=True)
    else:
        st.info("No candidates available yet.")


def _timeline(report):
    import streamlit as st

    st.markdown('<div class="tc-card">', unsafe_allow_html=True)
    st.subheader("Recruitment Timeline")
    for event in report.timeline:
        if event.status == "done":
            st.success(f"{event.label} — {event.description}")
        elif event.status == "active":
            st.info(f"{event.label} — {event.description}")
        else:
            st.caption(f"{event.label} — {event.description}")
    st.markdown("</div>", unsafe_allow_html=True)


def render_recruitment_workspace():
    import streamlit as st

    apply_enterprise_theme()

    session = get_streamlit_session()
    report = RecruitmentWorkspaceService().build(session)

    enterprise_hero(
        "Recruitment Workspace",
        "Pilot the active recruitment from candidate analysis to hiring decision.",
        "Recruitment",
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Load Enterprise Demo"):
            session = create_demo_recruitment_session()
            set_streamlit_session(session)
            report = RecruitmentWorkspaceService().build(session)
            st.success("Enterprise demo loaded.")
    with col2:
        st.caption(f"Active recruitment: {report.role_title} · Status: {report.status}")

    metric_grid([
        ("Role", report.role_title, report.status),
        ("Candidates", str(report.candidates_count), "Total"),
        ("Analyzed", str(report.analyzed_count), "AI completed"),
        ("Session", report.session_id[:8] if report.session_id else "-", "Active"),
    ])

    _pipeline(report)

    left, right = st.columns([1.2, 0.8])

    with left:
        section_title("Candidates in this recruitment", "Candidate stage and recommendation summary.")
        _candidate_table(report)

    with right:
        _timeline(report)
        next_action_card(
            "Next recruitment action",
            report.next_actions[0] if report.next_actions else "Continue the recruitment workflow.",
            "Continue",
        )

    section_title("Recommended actions")
    for action in report.next_actions:
        st.write(f"- {action}")
