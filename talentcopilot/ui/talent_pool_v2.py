from talentcopilot.ui.enterprise_components import context_panel, hero, metric_row, safe_render


@safe_render
def render_talent_pool_v2(*args, **kwargs):
    import streamlit as st
    from talentcopilot.ai.talent_locator_engine import TalentLocatorEngine
    from talentcopilot.services.session_store import SessionStore
    from talentcopilot.ui.talent_locator_cards import render_talent_locator_results

    hero("Talent Pool", "Locate promising profiles from the active recruitment session.", "Talent Locator")
    session = SessionStore.get_current_session()
    if not session:
        context_panel()
        return

    report = TalentLocatorEngine().locate(session.job, session.candidates, limit=10)
    metric_row([("Role", session.role_title), ("Pool size", str(report.total_candidates)), ("Recommended", str(report.recommended_count)), ("Source", session.metadata.get("source", "session"))])
    render_talent_locator_results(report)
