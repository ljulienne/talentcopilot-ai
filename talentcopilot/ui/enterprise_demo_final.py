from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.enterprise_demo_final_service import EnterpriseDemoFinalService
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session, set_streamlit_session
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def render_enterprise_demo_final():
    import streamlit as st

    apply_enterprise_theme()

    service = EnterpriseDemoFinalService()
    session = get_streamlit_session()
    report = service.build(session)

    enterprise_hero(
        "Enterprise Demo Final",
        report.positioning,
        report.title,
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Load Enterprise Demo"):
            session = create_demo_recruitment_session()
            set_streamlit_session(session)
            report = service.build(session)
            st.success("Enterprise demo loaded.")
    with col2:
        st.caption("Use this page as the presenter cockpit before a full product demonstration.")

    metric_grid([
        ("Demo Readiness", f"{report.readiness_score}%", "Scenario"),
        ("Duration", f"{report.total_duration_minutes} min", "Estimated"),
        ("Workspaces", str(len(report.steps)), "Covered"),
        ("Release", "1.1", "Enterprise Demo"),
    ])

    insight_card(
        "Demo narrative",
        report.closing_message,
        "Storyline",
    )

    tab_checklist, tab_script, tab_talking_points = st.tabs([
        "Readiness Checklist",
        "Demo Script",
        "Talking Points",
    ])

    with tab_checklist:
        section_title("Demo readiness")
        for item in report.readiness_items:
            if item.status == "OK":
                st.success(f"{item.name} — {item.detail}")
            elif item.status == "WARN":
                st.warning(f"{item.name} — {item.detail}")
            else:
                st.error(f"{item.name} — {item.detail}")

    with tab_script:
        section_title("20–30 minute demo script")
        for step in report.steps:
            with st.expander(f"{step.order}. {step.workspace} · {step.expected_duration_minutes} min"):
                st.write(f"**Business question:** {step.business_question}")
                st.write(f"**Talking point:** {step.talking_point}")
                st.caption(f"Status: {step.status}")

    with tab_talking_points:
        section_title("Key messages")
        st.write("- TalentCopilot is not only a CV matching tool.")
        st.write("- It separates candidate fit, budget feasibility, interview evidence and decision readiness.")
        st.write("- AI recommends, humans decide.")
        st.write("- Every major decision should be explainable and stakeholder-ready.")
