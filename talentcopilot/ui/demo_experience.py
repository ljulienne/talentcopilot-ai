from talentcopilot.services.demo_experience_service import DemoExperienceService
from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session, set_streamlit_session
from talentcopilot.ui.design_system.components import enterprise_hero, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def render_demo_experience():
    import streamlit as st

    apply_enterprise_theme()

    session = get_streamlit_session()
    service = DemoExperienceService()
    report = service.build(session)

    enterprise_hero(
        "Demo Experience",
        "Prepare a reliable enterprise demo scenario across the full TalentCopilot workflow.",
        "Administration",
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Load Enterprise Demo"):
            session = create_demo_recruitment_session()
            set_streamlit_session(session)
            report = service.build(session)
            st.success("Enterprise demo loaded.")
    with col2:
        st.caption(f"Scenario: {report.scenario_name}")

    metric_grid([
        ("Demo Readiness", f"{report.readiness_score}%", "Scenario"),
        ("Role", report.role_title, "Active"),
        ("Steps", str(len(report.steps)), "Journey"),
        ("Session", report.session_id[:8] if report.session_id else "-", "Active"),
    ])

    section_title("Session Checks")
    for check in report.checks:
        if check.status == "OK":
            st.success(f"{check.name} — {check.detail}")
        else:
            st.error(f"{check.name} — {check.detail}")

    section_title("Demo Journey")
    for step in report.steps:
        with st.expander(f"{step.order}. {step.workspace}"):
            st.write(f"**Objective:** {step.objective}")
            st.write(f"**Expected value:** {step.expected_value}")

    section_title("Presenter Notes")
    for note in report.presenter_notes:
        st.write(f"- {note}")
