from talentcopilot.ui.enterprise_components import hero, safe_render
from talentcopilot.ui.session_driven_components import session_action_bar, copilot_guidance


@safe_render
def render_recruiter_copilot_v2(*args, **kwargs):
    import streamlit as st

    hero(
        "Recruiter Copilot",
        "Recruiter guidance generated from Decision Intelligence.",
        "Session-driven",
    )

    session = session_action_bar()

    st.subheader("Guidance by candidate")
    copilot_guidance(session)
