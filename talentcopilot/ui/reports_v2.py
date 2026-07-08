from talentcopilot.services.session_report_builder import SessionReportBuilder
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session
from talentcopilot.ui.enterprise_components import hero, safe_render
from talentcopilot.ui.feature_restoration_components import page_purpose, session_required_hint


@safe_render
def render_reports_v2(*args, **kwargs):
    import streamlit as st

    hero(
        "Reports",
        "Prepare recruiter-ready outputs from the active session.",
        "Deliver",
    )

    page_purpose(
        "Reports",
        "This page is for producing outputs, not reviewing raw analysis.",
        [
            "Preview a structured recruitment report.",
            "Export the current session summary.",
            "Prepare stakeholder communication.",
        ],
    )

    session = get_streamlit_session()
    if not session_required_hint(session):
        return

    markdown_report = SessionReportBuilder().build_markdown(session)
    st.markdown(markdown_report)

    st.download_button(
        "Download markdown report",
        data=markdown_report,
        file_name="talentcopilot_recruitment_report.md",
        mime="text/markdown",
    )
