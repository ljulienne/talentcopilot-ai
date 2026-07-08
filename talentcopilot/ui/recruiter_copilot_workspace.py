from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.recruiter_copilot_workspace_service import RecruiterCopilotWorkspaceService
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session, set_streamlit_session
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def _render_actions(actions):
    import streamlit as st

    if not actions:
        st.info("No action available.")
        return

    for action in actions:
        with st.expander(f"{action.priority} · {action.title}"):
            st.write(action.rationale)
            st.caption(f"Owner: {action.owner}")


def _render_questions(questions):
    import streamlit as st

    if not questions:
        st.info("No interview questions available.")
        return

    for question in questions:
        st.markdown(f"**{question.question}**")
        st.caption(f"Purpose: {question.purpose}")
        if question.expected_signal:
            st.info(f"Expected signal: {question.expected_signal}")


def _render_alerts(alerts):
    import streamlit as st

    if not alerts:
        st.success("No major alert for this candidate.")
        return

    for alert in alerts:
        if alert.severity.lower() == "high":
            st.error(f"**{alert.title}** — {alert.detail}")
        else:
            st.warning(f"**{alert.title}** — {alert.detail}")


def render_recruiter_copilot_workspace():
    import streamlit as st

    apply_enterprise_theme()

    session = get_streamlit_session()
    report = RecruiterCopilotWorkspaceService().build(session)

    enterprise_hero(
        "Recruiter Copilot",
        "Turn AI analysis into clear recruiter actions, interview questions and stakeholder communication.",
        "Action Workspace",
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Load Enterprise Demo"):
            session = create_demo_recruitment_session()
            set_streamlit_session(session)
            report = RecruiterCopilotWorkspaceService().build(session)
            st.success("Enterprise demo loaded.")
    with col2:
        st.caption(f"Active recruitment: {report.role_title}")

    metric_grid([
        ("Workspace", "Recruiter Copilot", "Action"),
        ("Candidates", str(len(report.candidates)), "With guidance"),
        ("Global Actions", str(len(report.global_actions)), "Recommended"),
        ("Session", report.session_id[:8] if report.session_id else "-", "Active"),
    ])

    section_title("Global AI Actions", "What the recruiter should do next.")
    _render_actions(report.global_actions)

    if not report.candidates:
        st.info("No candidate guidance available yet. Load the Enterprise Demo to activate the Copilot.")
        return

    candidate_names = [candidate.candidate_name for candidate in report.candidates]
    selected = st.selectbox("Select candidate", candidate_names)
    candidate = report.candidates[candidate_names.index(selected)]

    insight_card(candidate.headline, candidate.recruiter_summary, "Recruiter Copilot")

    tab_actions, tab_questions, tab_alerts, tab_summary = st.tabs([
        "Actions",
        "Interview Guide",
        "Alerts",
        "Stakeholder Summary",
    ])

    with tab_actions:
        section_title("Candidate Actions")
        _render_actions(candidate.actions)

    with tab_questions:
        section_title("Interview Guide")
        _render_questions(candidate.questions)

    with tab_alerts:
        section_title("Alerts & Missing Evidence")
        _render_alerts(candidate.alerts)

    with tab_summary:
        section_title("Stakeholder Summary")
        st.info(candidate.stakeholder_summary)
