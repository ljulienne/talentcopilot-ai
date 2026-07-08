from talentcopilot.ai.talent_locator_engine import TalentLocatorEngine
from talentcopilot.services.demo_session_factory import demo_job
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session
from talentcopilot.ui.enterprise_components import hero, safe_render
from talentcopilot.ui.feature_restoration_components import candidate_kpi_strip, page_purpose, session_required_hint
from talentcopilot.ui.talent_locator_cards import render_talent_locator_results


@safe_render
def render_talent_pool_v2(*args, **kwargs):
    import streamlit as st

    hero(
        "Talent Pool",
        "Use the internal talent pool and Talent Locator to identify promising profiles.",
        "Analyze",
    )

    page_purpose(
        "Talent Pool",
        "This page is for sourcing inside the available candidate pool, not for detailed candidate decisions.",
        [
            "View available candidates from the active session.",
            "Run Talent Locator against the current role.",
            "Identify shortlist candidates before comparison.",
        ],
    )

    session = get_streamlit_session()
    if not session_required_hint(session):
        return

    candidate_kpi_strip(session)

    st.subheader("Internal candidates")
    for candidate in session.candidates:
        with st.expander(candidate.get("name", "Candidate")):
            st.write("**Skills:** " + ", ".join(candidate.get("skills", [])))
            achievements = candidate.get("achievements", [])
            if achievements:
                st.markdown("**Evidence hints**")
                for item in achievements[:3]:
                    st.caption(item)

    st.subheader("Talent Locator")
    report = TalentLocatorEngine().locate(session.job or demo_job(), session.candidates)
    render_talent_locator_results(report)
