from talentcopilot.ui.enterprise_components import context_panel, hero, metric_row, safe_render


@safe_render
def render_candidates_v2(*args, **kwargs):
    import streamlit as st
    from talentcopilot.services.session_store import SessionStore

    hero("Candidates", "Review analyzed candidates from the active RecruitmentSession.", "Candidate Workspace")
    session = SessionStore.get_current_session()
    if not session:
        context_panel()
        return

    metric_row([("Role", session.role_title), ("Candidates", str(session.candidate_count)), ("Analyzed", str(session.analyzed_count)), ("Errors", str(session.error_count))])

    for analysis in session.ranked_analyses:
        with st.expander(f"#{analysis.rank} — {analysis.candidate_name} · Match {analysis.match_score:.0f}%", expanded=analysis.rank == 1):
            st.write(f"Status: **{analysis.status.value}**")
            decision = analysis.decision_report
            if decision:
                recommendation = getattr(decision.recommendation, "value", decision.recommendation)
                st.success(f"Decision: {recommendation} · Score {decision.decision_score:.0f}%")
                st.write(decision.executive_summary)
                if decision.concerns:
                    st.warning(f"{len(decision.concerns)} concern(s) detected.")
            if analysis.governance_report:
                card = analysis.governance_report.decision_card
                st.info(f"Governance: confidence {card.confidence_score:.0f}% · risk {card.risk_level}")
            if analysis.errors:
                for error in analysis.errors:
                    st.error(error)
