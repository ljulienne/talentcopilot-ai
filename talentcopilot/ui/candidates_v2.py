from talentcopilot.services.streamlit_session_bridge import get_streamlit_session
from talentcopilot.ui.enterprise_components import hero, safe_render
from talentcopilot.ui.feature_restoration_components import (
    candidate_kpi_strip,
    decision_summary_for_analysis,
    page_purpose,
    session_required_hint,
)


@safe_render
def render_candidates_v2(*args, **kwargs):
    import streamlit as st

    hero(
        "Candidates",
        "Inspect candidate-level evidence, ranking and decision signals.",
        "Analyze",
    )

    page_purpose(
        "Candidates",
        "This page is for detailed candidate review.",
        [
            "Review every analyzed candidate.",
            "Understand match score and ranking.",
            "Inspect decisions, copilot summaries and errors.",
        ],
    )

    session = get_streamlit_session()
    if not session_required_hint(session):
        return

    candidate_kpi_strip(session)

    st.subheader("Candidate detail cards")
    for analysis in session.ranked_analyses:
        with st.expander(f"#{analysis.rank} · {analysis.candidate_name} · {analysis.match_score:.0f}%"):
            st.write(f"Status: {analysis.status.value}")
            decision_summary_for_analysis(analysis)

            if analysis.recruiter_copilot_report:
                st.markdown("**Recruiter Copilot Summary**")
                st.write(analysis.recruiter_copilot_report.recruiter_summary)

            if analysis.errors:
                for error in analysis.errors:
                    st.warning(error)
