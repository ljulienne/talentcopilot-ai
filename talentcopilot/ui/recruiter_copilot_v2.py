from talentcopilot.ui.enterprise_components import context_panel, hero, metric_row, safe_render


@safe_render
def render_recruiter_copilot_v2(*args, **kwargs):
    import streamlit as st
    from talentcopilot.services.session_store import SessionStore
    from talentcopilot.ui.recruiter_copilot_cards import render_recruiter_copilot_card

    hero("Recruiter Copilot", "Actionable guidance generated from the active session.", "Recruiter Guidance")
    session = SessionStore.get_current_session()
    if not session:
        context_panel()
        return

    available = [a for a in session.ranked_analyses if a.recruiter_copilot_report]
    metric_row([("Role", session.role_title), ("Copilot reports", str(len(available))), ("Candidates", str(session.candidate_count)), ("Top rank", available[0].candidate_name if available else "—")])

    if not available:
        st.info("No Recruiter Copilot report available yet. Run the Enterprise Pipeline with Decision Intelligence enabled.")
        return

    names = [a.candidate_name for a in available]
    selected = st.selectbox("Candidate", names)
    analysis = next(a for a in available if a.candidate_name == selected)
    render_recruiter_copilot_card(analysis.recruiter_copilot_report)
