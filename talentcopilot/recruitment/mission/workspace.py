"""Single-page Recruitment Mission workspace using the Enterprise Workspace Engine."""

from __future__ import annotations

from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.recruitment_pdf_service import RecruitmentPdfService
from talentcopilot.services.streamlit_session_bridge import (
    get_streamlit_session,
    set_streamlit_session,
)
from talentcopilot.ui.design_system.theme import apply_enterprise_theme
from talentcopilot.ui.design_system.v2.workspace import render_enterprise_workspace
from talentcopilot.ui.recruitment_upload_panel import render_recruitment_upload_panel
from talentcopilot.ui.navigation_actions import request_page

from .enterprise_adapter import build_enterprise_workspace_model
from .navigation import MISSION_SECTIONS
from .sections.comparison import render_comparison
from .sections.decision import render_decision
from .sections.interview import render_interview
from .sections.overview import render_overview
from .sections.ranking import render_ranking
from .sections.reasoning import render_reasoning
from .sections.report import render_report
from .state import build_recruitment_mission_state


_RENDERERS = {
    "overview": render_overview,
    "ranking": render_ranking,
    "reasoning": render_reasoning,
    "comparison": render_comparison,
    "interview": render_interview,
    "decision": render_decision,
    "report": render_report,
}


def _empty_state() -> None:
    import streamlit as st

    st.info("Create or reopen a recruitment mission, or load the enterprise demo.")
    if st.button("Load Enterprise Demo", key="tc60a_load_demo", type="primary"):
        set_streamlit_session(create_demo_recruitment_session())
        st.rerun()


def render_recruitment_mission_workspace() -> None:
    apply_enterprise_theme()

    session = render_recruitment_upload_panel(get_streamlit_session())
    if session is None:
        _empty_state()
        return

    state = build_recruitment_mission_state(session)

    import streamlit as st

    # After the first completed analysis, route the recruiter to the whole-pool
    # Dashboard Perspective. The marker prevents repeated redirects when the
    # user later returns to Overview.
    redirect_key = f"tc_dashboard_perspective_opened:{getattr(session, 'session_id', 'session')}"
    if state.has_analysis and not st.session_state.get(redirect_key, False):
        st.session_state[redirect_key] = True
        request_page(
            "Dashboard Perspective",
            reason="Candidate analysis completed. Opened Dashboard Perspective.",
        )
        st.rerun()

    if state.has_analysis:
        export = RecruitmentPdfService().mission(state)
        export_col, dashboard_col = st.columns([1, 1])
        with export_col:
            st.download_button(
                "Download recruitment overview (PDF)",
                data=export.data,
                file_name=export.file_name,
                mime=export.mime,
                key="recruitment_overview_pdf",
                use_container_width=True,
            )
        with dashboard_col:
            if st.button(
                "Open Dashboard Perspective →",
                type="primary",
                key="recruitment_overview_dashboard",
                use_container_width=True,
            ):
                request_page(
                    "Dashboard Perspective",
                    reason="Opened the candidate dashboard from Recruitment Overview.",
                )
                st.rerun()

    model = build_enterprise_workspace_model(
        state,
        section_definitions=MISSION_SECTIONS,
        renderers=_RENDERERS,
    )
    render_enterprise_workspace(model)
