from talentcopilot.ui.enterprise_components import hero, safe_render
from talentcopilot.ui.session_driven_components import session_action_bar, ranked_candidates_table


@safe_render
def render_comparison_v2(*args, **kwargs):
    import streamlit as st

    hero(
        "Comparison",
        "Compare candidates using the same ranked analyses shared across the app.",
        "Session-driven",
    )

    session = session_action_bar()

    st.subheader("Comparison table")
    ranked_candidates_table(session)
