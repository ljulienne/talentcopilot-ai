from talentcopilot.services.command_center_service import CommandCenterService
from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.streamlit_session_bridge import (
    clear_streamlit_session,
    get_streamlit_session,
    set_streamlit_session,
)
from talentcopilot.ui.design_system.components import (
    activity_item,
    enterprise_hero,
    insight_card,
    metric_grid,
    next_action_card,
    section_title,
)
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def _health_block(health):
    import streamlit as st

    st.markdown('<div class="tc-card">', unsafe_allow_html=True)
    st.subheader("Recruitment Health")
    st.metric("Overall Health", f"{health.overall_score}%")
    st.progress(max(0, min(100, health.overall_score)) / 100)

    c1, c2 = st.columns(2)
    c1.metric("Evidence Coverage", f"{health.evidence_coverage}%")
    c2.metric("Interview Readiness", f"{health.interview_readiness}%")

    c3, c4 = st.columns(2)
    c3.metric("AI Confidence", f"{health.decision_confidence}%")
    c4.metric("Bias Risk", health.bias_risk)

    st.caption(f"Data completeness: {health.data_completeness}%")
    st.markdown('</div>', unsafe_allow_html=True)


def _workflow_tracker():
    import streamlit as st

    steps = ["Job Definition", "Candidate Analysis", "Comparison", "Decision", "Interview", "Offer", "Reporting"]
    st.markdown("### Recruitment Workflow")
    cols = st.columns(len(steps))
    for index, step in enumerate(steps):
        with cols[index]:
            if index <= 3:
                st.success(step)
            else:
                st.caption(step)


def render_command_center():
    import streamlit as st

    apply_enterprise_theme()

    session = get_streamlit_session()
    report = CommandCenterService().build(session)

    enterprise_hero(
        "Recruitment Command Center",
        "Your daily cockpit for explainable, evidence-based hiring decisions.",
        "Better Hiring Decisions. Explained.",
    )

    col1, col2, col3 = st.columns([1.2, 1, 2.2])
    with col1:
        if st.button("Load Enterprise Demo"):
            session = create_demo_recruitment_session()
            set_streamlit_session(session)
            st.success("Enterprise demo loaded.")
            report = CommandCenterService().build(session)
    with col2:
        if st.button("Clear Demo"):
            clear_streamlit_session()
            session = None
            report = CommandCenterService().build(None)
            st.info("Demo cleared.")
    with col3:
        st.caption(f"Active recruitment: {report.role_title}")

    metric_grid([(m.label, m.value, m.delta) for m in report.metrics])

    _workflow_tracker()

    left, right = st.columns([1.2, 0.8])

    with left:
        section_title("Today's AI Priorities", "Recommended actions for the current recruitment.")
        for priority in report.priorities:
            insight_card(priority.title, priority.description, priority.badge)

        section_title("Recent Activity", "What happened recently in the recruitment workflow.")
        for activity in report.activities:
            activity_item(activity.time, activity.title, activity.detail)

    with right:
        _health_block(report.health)
        next_action_card(report.next_action_title, report.next_action_body, "Continue")
