from talentcopilot.ui.enterprise_components import context_panel, hero, metric_row, ranked_candidate_table, safe_render


@safe_render
def render_comparison_v2(*args, **kwargs):
    import streamlit as st
    from talentcopilot.services.session_store import SessionStore

    hero("Comparison", "Compare candidates using ranked session analyses.", "Candidate Comparison")
    session = SessionStore.get_current_session()
    if not session:
        context_panel()
        return

    metric_row([("Role", session.role_title), ("Candidates", str(session.candidate_count)), ("Analyzed", str(session.analyzed_count)), ("Shortlist", str(len([a for a in session.analyses if a.match_score >= 70])))])
    ranked_candidate_table(session)

    st.subheader("Top candidate details")
    for analysis in session.ranked_analyses[:3]:
        decision = analysis.decision_report
        with st.expander(f"#{analysis.rank} {analysis.candidate_name}"):
            st.write(f"Match score: **{analysis.match_score:.0f}%**")
            if decision:
                st.write(decision.executive_summary)
                if decision.strengths:
                    st.success("Strengths: " + ", ".join([s.title for s in decision.strengths[:3]]))
                if decision.concerns:
                    st.warning("Concerns: " + ", ".join([c.title for c in decision.concerns[:3]]))
