from talentcopilot.ui.enterprise_components import hero, safe_render
from talentcopilot.ui.session_driven_components import session_action_bar, report_readiness


@safe_render
def render_reports_v2(*args, **kwargs):
    import streamlit as st

    hero(
        "Reports",
        "Session-based reporting readiness and candidate decision summary.",
        "Session-driven",
    )

    session = session_action_bar()

    st.subheader("Report readiness")
    report_readiness(session)
