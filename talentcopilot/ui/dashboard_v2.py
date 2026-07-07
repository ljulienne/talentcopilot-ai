from talentcopilot.ui.enterprise_components import hero, safe_render
from talentcopilot.ui.session_driven_components import session_action_bar, session_overview, ranked_candidates_table


@safe_render
def render_dashboard_v2(*args, **kwargs):
    import streamlit as st

    hero(
        "Decision Center",
        "Central view of the active RecruitmentSession and candidate ranking.",
        "Session-driven",
    )

    session = session_action_bar()
    session_overview(session)

    st.subheader("Ranked candidates")
    ranked_candidates_table(session)
