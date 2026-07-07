from talentcopilot.ui.enterprise_components import context_panel, hero, metric_row, safe_render


@safe_render
def render_reports_v2(*args, **kwargs):
    import streamlit as st
    from talentcopilot.ai.product_readiness_engine import ProductReadinessEngine
    from talentcopilot.ai.recruiter_workflow_engine import RecruiterWorkflowEngine
    from talentcopilot.services.session_store import SessionStore

    hero("Reports", "Session-driven recruitment report preview.", "Reporting")
    session = SessionStore.get_current_session()
    if not session:
        context_panel()
        return

    workflow = RecruiterWorkflowEngine().build_workflow(session)
    readiness = ProductReadinessEngine().assess(session, workflow)
    metric_row([("Role", session.role_title), ("Candidates", str(session.candidate_count)), ("Readiness", readiness.readiness_level.value), ("Report", "Preview")])

    st.subheader("Executive summary")
    st.write(f"Recruitment session **{session.session_id}** for **{session.role_title}** contains **{session.candidate_count}** candidate(s), with **{session.analyzed_count}** analyzed profile(s).")
    st.write(readiness.summary)

    st.subheader("Shortlist")
    shortlist = [a for a in session.ranked_analyses if a.match_score >= 70]
    if shortlist:
        for analysis in shortlist:
            st.success(f"#{analysis.rank} {analysis.candidate_name} — Match {analysis.match_score:.0f}%")
    else:
        st.info("No shortlist-ready candidate yet.")

    st.subheader("Recommended next action")
    st.info(workflow.recommended_next_action)
