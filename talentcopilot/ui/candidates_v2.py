from talentcopilot.ui.enterprise_components import hero, safe_render
from talentcopilot.ui.session_driven_components import session_action_bar, session_overview, candidate_detail_cards


@safe_render
def render_candidates_v2(*args, **kwargs):
    import streamlit as st

    hero(
        "Candidates",
        "Candidate workspace powered by the active RecruitmentSession.",
        "Session-driven",
    )

    session = session_action_bar()
    session_overview(session)

    st.subheader("Candidate details")
    candidate_detail_cards(session)
