from talentcopilot.ui.enterprise_components import context_panel, hero, metric_row, safe_render


@safe_render
def render_decision_workspace(*args, **kwargs):
    import streamlit as st
    from talentcopilot.services.session_store import SessionStore
    from talentcopilot.ui.decision_cards import render_decision_intelligence_card
    from talentcopilot.ui.governance_cards import render_governance_card

    hero("Decision Workspace", "Inspect decisions, governance and validation needs from the active session.", "Decision Workspace")
    session = SessionStore.get_current_session()
    if not session:
        context_panel()
        return

    metric_row([("Role", session.role_title), ("Candidates", str(session.candidate_count)), ("Analyzed", str(session.analyzed_count)), ("Errors", str(session.error_count))])
    names = [a.candidate_name for a in session.ranked_analyses]
    selected = st.selectbox("Candidate", names)
    analysis = next(a for a in session.ranked_analyses if a.candidate_name == selected)

    st.subheader(f"#{analysis.rank} {analysis.candidate_name}")
    st.metric("Match score", f"{analysis.match_score:.0f}%")

    if analysis.decision_report:
        render_decision_intelligence_card(analysis.decision_report)
    else:
        st.info("No decision report available for this candidate.")

    if analysis.governance_report:
        render_governance_card(analysis.governance_report)
    else:
        st.info("No governance report available for this candidate.")
