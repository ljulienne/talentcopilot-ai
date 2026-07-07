from talentcopilot.ui.enterprise_components import capability_grid, context_panel, hero, metric_row, ranked_candidate_table, safe_render


@safe_render
def render_dashboard_v2(*args, **kwargs):
    import streamlit as st
    from talentcopilot.ai.product_readiness_engine import ProductReadinessEngine
    from talentcopilot.ai.recruiter_workflow_engine import RecruiterWorkflowEngine
    from talentcopilot.services.session_store import SessionStore
    from talentcopilot.ui.product_readiness_cards import render_product_readiness
    from talentcopilot.ui.recruiter_workflow_cards import render_recruiter_workflow

    hero("Decision Center", "Central view of the active recruitment session and product readiness.", "Decision Intelligence")
    session = SessionStore.get_current_session()

    if session:
        workflow = RecruiterWorkflowEngine().build_workflow(session)
        readiness = ProductReadinessEngine().assess(session, workflow)
        metric_row([
            ("Role", session.role_title),
            ("Candidates", str(session.candidate_count)),
            ("Analyzed", str(session.analyzed_count)),
            ("Readiness", readiness.readiness_level.value),
        ])
        render_recruiter_workflow(workflow)
        render_product_readiness(readiness)
        st.subheader("Ranked candidates")
        ranked_candidate_table(session)
    else:
        metric_row([("Session", "Missing"), ("Candidates", "0"), ("Analyzed", "0"), ("Readiness", "Partial")])
        st.info("Launch the enterprise demo session from Home to populate the Decision Center.")
        capability_grid([
            ("Session required", "Decision Center is now driven by RecruitmentSession."),
            ("Single source of truth", "Candidate ranking, workflow and readiness come from the same session."),
        ])
        context_panel()
