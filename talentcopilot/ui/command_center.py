from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.streamlit_session_bridge import (
    clear_streamlit_session,
    get_streamlit_session,
    set_streamlit_session,
)
from talentcopilot.ui.design_system.components import (
    activity_item,
    enterprise_hero,
    insight_card,
    metric_grid,
    next_action_card,
    section_title,
)


def _best_candidate(session):
    if session and getattr(session, "ranked_analyses", None):
        return session.ranked_analyses[0].candidate_name
    return "No active session"


def render_command_center():
    import streamlit as st

    session = get_streamlit_session()

    enterprise_hero(
        "Recruitment Command Center",
        "Your daily cockpit for explainable AI-assisted hiring decisions.",
        "Better Hiring Decisions. Explained.",
    )

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("Load Enterprise Demo"):
            session = create_demo_recruitment_session()
            set_streamlit_session(session)
            st.success("Enterprise demo loaded.")
    with col2:
        if st.button("Clear Demo"):
            clear_streamlit_session()
            session = None
            st.info("Demo cleared.")
    with col3:
        if session:
            st.caption(f"Active recruitment: {session.role_title} · {session.session_id}")
        else:
            st.caption("No active recruitment loaded.")

    metric_grid([
        ("Active Recruitments", "1" if session else "0", "Demo-ready"),
        ("Candidates", str(session.candidate_count) if session else "0", "Analyzed" if session else "Load demo"),
        ("Pending Decisions", "1" if session else "0", "Human review"),
        ("Best Match", _best_candidate(session), "AI ranking"),
    ])

    left, right = st.columns([1.15, 0.85])

    with left:
        section_title("Today's AI Priorities", "Recommended actions based on the active recruitment session.")
        if session:
            insight_card(
                "Review the top-ranked candidate",
                f"{_best_candidate(session)} is currently the strongest profile. Review evidence before progressing.",
                "AI Priority",
            )
            insight_card(
                "Prepare Hiring Manager interview",
                "Use the Recruiter Copilot to generate targeted questions and validation points.",
                "Next Step",
            )
            insight_card(
                "Generate executive summary",
                "A recruitment report can be prepared from the active session.",
                "Report Ready",
            )
        else:
            insight_card(
                "Load the Enterprise Demo",
                "Start with a complete scenario to explore the full recruitment decision workflow.",
                "Demo Mode",
            )

    with right:
        section_title("Recent Activity", "AI and recruitment workflow events.")
        if session:
            activity_item("09:41", "Recruitment session loaded", session.role_title)
            activity_item("09:42", "Candidates analyzed", f"{session.analyzed_count} analysis result(s)")
            activity_item("09:43", "Ranking updated", f"Best match: {_best_candidate(session)}")
            activity_item("09:44", "Report preview ready", "Executive reporting can be generated")
        else:
            activity_item("Now", "No active session", "Load the Enterprise Demo to start")

    next_action_card(
        "Continue the recruitment workflow",
        "Move from the Command Center to Candidate Workspace or Decision Center to continue the review.",
        "Open next workspace",
    )
