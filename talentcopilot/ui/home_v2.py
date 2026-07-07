from talentcopilot.ui.enterprise_components import capability_grid, context_panel, hero, metric_row, ranked_candidate_table, safe_render, workflow_steps


@safe_render
def render_home_v2(*args, **kwargs):
    import streamlit as st
    from talentcopilot.services.demo_session_factory import DemoSessionFactory
    from talentcopilot.services.session_store import SessionStore
    from talentcopilot.services.versioning import get_app_version

    hero(
        "TalentCopilot-AI",
        "A session-driven, explainable AI recruitment intelligence platform.",
        "v0.7 Enterprise",
    )

    session = SessionStore.get_current_session()

    metric_row([
        ("Version", get_app_version()),
        ("Session", "Active" if session else "Not started"),
        ("Workflow", "Connected" if session else "Demo ready"),
        ("AI Pipeline", "Ready"),
    ])

    st.subheader("Start a complete demo workflow")
    st.write("Launch a demo recruitment session. The same session will then feed Decision Center, Candidates, Talent Pool, Recruiter Copilot, Comparison and Reports.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Launch enterprise demo session", type="primary"):
            session = DemoSessionFactory().create_demo_session(job_index=0, candidate_limit=8)
            st.success("Demo session created and analyzed.")
            st.rerun()
    with col2:
        if st.button("🧹 Clear current session"):
            SessionStore.clear()
            st.success("Session cleared.")
            st.rerun()

    st.subheader("Current session")
    context_panel()
    ranked_candidate_table(SessionStore.get_current_session())

    st.subheader("Product workflow")
    workflow_steps([
        "Launch or create a recruitment session.",
        "Run the enterprise pipeline once.",
        "Review ranked candidates and evidence.",
        "Use Recruiter Copilot to prepare next actions.",
        "Generate reports from the same session state.",
    ])

    st.subheader("Capabilities connected in this sprint")
    capability_grid([
        ("Shared session", "All major pages can read the same RecruitmentSession."),
        ("Demo pipeline", "Enterprise demo data is normalized and analyzed through EnterprisePipeline."),
        ("Workflow readiness", "Recruiter workflow and product readiness can be derived from the session."),
        ("Reduced fragmentation", "The app is moving from isolated modules to a coherent product flow."),
    ])
