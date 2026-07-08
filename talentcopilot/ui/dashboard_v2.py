from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session, set_streamlit_session, clear_streamlit_session
from talentcopilot.ui.enterprise_components import hero, safe_render
from talentcopilot.ui.feature_restoration_components import candidate_kpi_strip, page_purpose


@safe_render
def render_dashboard_v2(*args, **kwargs):
    import streamlit as st

    hero(
        "Decision Center",
        "Operational control center for the current recruitment session.",
        "Decide",
    )

    page_purpose(
        "Decision Center",
        "This page controls the active recruitment session.",
        [
            "Create a demo recruitment session.",
            "Refresh the current analysis.",
            "Check the current ranking before moving to detailed pages.",
        ],
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Create demo recruitment session"):
            session = create_demo_recruitment_session()
            set_streamlit_session(session)
            st.success("Demo session created.")

    with col2:
        if st.button("Clear active session"):
            clear_streamlit_session()
            st.info("Session cleared.")

    session = get_streamlit_session()
    candidate_kpi_strip(session)

    if session:
        st.subheader("Current ranking")
        rows = [
            {
                "Rank": analysis.rank,
                "Candidate": analysis.candidate_name,
                "Match": analysis.match_score,
                "Status": analysis.status.value,
            }
            for analysis in session.ranked_analyses
        ]
        st.dataframe(rows, use_container_width=True)
