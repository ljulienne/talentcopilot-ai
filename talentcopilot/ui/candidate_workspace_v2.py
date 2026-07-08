from talentcopilot.services.candidate_workspace_v2_service import CandidateWorkspaceV2Service
from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session, set_streamlit_session
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def _evidence_graph(profile):
    import streamlit as st

    nodes = [
        {
            "Type": node.node_type,
            "Label": node.label,
            "Confidence": node.confidence,
            "Sources": ", ".join(node.source_ids),
        }
        for node in profile.evidence_graph.nodes
    ]
    edges = [
        {
            "Source": edge.source_node_id,
            "Relationship": edge.relationship,
            "Target": edge.target_node_id,
            "Confidence": edge.confidence,
        }
        for edge in profile.evidence_graph.edges
    ]

    st.write("**Evidence Nodes**")
    st.dataframe(nodes, use_container_width=True)
    st.write("**Evidence Edges**")
    st.dataframe(edges, use_container_width=True)


def _decision_trace(profile):
    import streamlit as st

    for index, step in enumerate(profile.decision_trace.steps, start=1):
        with st.expander(f"{index}. {step.engine} · {step.action}"):
            st.write(step.explanation)
            st.caption(f"Output: {step.output_ref}")


def _signals(profile):
    import streamlit as st

    rows = [{"Signal": key, "Value": value} for key, value in profile.metadata.items()]
    st.dataframe(rows, use_container_width=True)


def render_candidate_workspace_v2():
    import streamlit as st

    apply_enterprise_theme()

    service = CandidateWorkspaceV2Service()
    session = get_streamlit_session()
    report = service.build_from_session(session)

    enterprise_hero(
        "Candidate Workspace v2",
        "Review candidates through CandidateDecisionProfile and Decision Intelligence Core v2.",
        "Decision Core Migration",
    )

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("Load Enterprise Demo"):
            session = create_demo_recruitment_session()
            set_streamlit_session(session)
            report = service.build_from_session(session)
            st.success("Enterprise demo loaded.")
    with col2:
        if st.button("Run Candidate Demo"):
            report = service.build_demo()
            st.success("Candidate demo executed.")
    with col3:
        st.caption("This workspace validates the future CandidateDecisionProfile-based UI.")

    if not report.outputs:
        st.info("No Decision Core candidate profile available. Load demo or run Candidate Demo.")
        return

    names = [output.profile.candidate_name for output in report.outputs]
    selected = st.selectbox("Candidate", names)
    output = report.outputs[names.index(selected)]
    profile = output.profile

    metric_grid([
        ("Candidate", profile.candidate_name, profile.role_title),
        ("Fit", f"{profile.fit_score}%", profile.metadata.get("fit_status", "-")),
        ("Risk", profile.risk_level or "-", profile.metadata.get("risk_score", "-")),
        ("Confidence", f"{profile.confidence_score}%", profile.metadata.get("confidence_level", "-")),
    ])

    insight_card(
        "Recommendation",
        f"{profile.recommendation}: {profile.metadata.get('recommendation_rationale', '-')}",
        profile.metadata.get("recommendation_category", "Decision Core"),
    )

    tab_summary, tab_signals, tab_evidence, tab_trace = st.tabs([
        "Summary",
        "Signals",
        "Evidence Graph",
        "Decision Trace",
    ])

    with tab_summary:
        section_title("Executive Summary")
        st.write(profile.metadata.get("executive_summary", "-"))
        section_title("Recruiter Summary")
        st.write(profile.metadata.get("recruiter_summary", "-"))

    with tab_signals:
        section_title("CandidateDecisionProfile Signals")
        _signals(profile)

    with tab_evidence:
        section_title("Evidence Graph Preview")
        _evidence_graph(profile)

    with tab_trace:
        section_title("Decision Trace")
        _decision_trace(profile)
