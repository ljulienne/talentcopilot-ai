from talentcopilot.services.session_report_builder import SessionReportBuilder
from talentcopilot.services.report_export_service import ReportExportService
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

    export = ReportExportService().from_markdown(
        markdown_report,
        file_name="talentcopilot_recruitment_report.pdf",
        title="TalentCopilot Recruitment Report",
    )
    st.download_button(
        "Download recruitment report (PDF)",
        data=export.data,
        file_name=export.file_name,
        mime=export.mime,
    )
