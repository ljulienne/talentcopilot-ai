from talentcopilot.decision_core.workspace_bridge import DecisionCoreWorkspaceBridge
from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session, set_streamlit_session
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def _profiles(report):
    import streamlit as st

    rows = []
    for output in report.outputs:
        profile = output.profile
        rows.append(
            {
                "Candidate": profile.candidate_name,
                "Fit": profile.fit_score,
                "Risk": profile.risk_level,
                "Confidence": profile.confidence_score,
                "Recommendation": profile.recommendation,
                "Decision Quality": profile.metadata.get("decision_quality", "-"),
            }
        )
    if rows:
        st.dataframe(rows, use_container_width=True)
    else:
        st.info("No Decision Core profiles available.")


def _trace_preview(report):
    import streamlit as st

    if not report.outputs:
        st.info("No trace available.")
        return

    names = [output.profile.candidate_name for output in report.outputs]
    selected = st.selectbox("Candidate trace", names)
    output = report.outputs[names.index(selected)]

    for index, step in enumerate(output.profile.decision_trace.steps, start=1):
        with st.expander(f"{index}. {step.engine} · {step.action}"):
            st.write(step.explanation)
            st.caption(f"Output: {step.output_ref}")


def render_decision_core_bridge():
    import streamlit as st

    apply_enterprise_theme()

    bridge = DecisionCoreWorkspaceBridge()
    session = get_streamlit_session()
    report = bridge.build_from_session(session)

    enterprise_hero(
        "Decision Core Bridge",
        "Convert current recruitment session data into CandidateDecisionProfiles using Decision Core v2.",
        "Migration Bridge",
    )

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("Load Enterprise Demo"):
            session = create_demo_recruitment_session()
            set_streamlit_session(session)
            report = bridge.build_from_session(session)
            st.success("Enterprise demo loaded.")
    with col2:
        if st.button("Run Bridge Demo"):
            report = bridge.build_demo()
            st.success("Bridge demo executed.")
    with col3:
        st.caption("This page helps migrate existing workspaces progressively to Decision Core v2.")

    metric_grid([
        ("Role", report.role_title, report.status),
        ("Candidates", str(report.total_candidates), "Session"),
        ("Profiles", str(report.profiles_created), "Decision Core"),
        ("Status", report.status, "Bridge"),
    ])

    insight_card(
        "Migration strategy",
        "Existing workspaces remain stable. The bridge produces CandidateDecisionProfiles that future workspaces can consume.",
        "Decision Core v2",
    )

    tab_profiles, tab_trace = st.tabs(["Profiles", "Decision Trace"])

    with tab_profiles:
        section_title("CandidateDecisionProfiles")
        _profiles(report)

    with tab_trace:
        section_title("Trace Preview")
        _trace_preview(report)
