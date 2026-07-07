from typing import Any


def render_recruitment_session_overview(session: Any) -> None:
    try:
        import streamlit as st
    except ImportError:
        return

    st.subheader("Enterprise Recruitment Session")

    if session is None:
        st.info("No recruitment session available yet.")
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Role", session.role_title)
    col2.metric("Candidates", session.candidate_count)
    col3.metric("Analyzed", session.analyzed_count)
    col4.metric("Errors", session.error_count)

    st.caption(f"Session ID: {session.session_id}")
    st.caption(f"Status: {session.status.value}")

    if session.analyses:
        st.markdown("### Ranked analyses")
        for analysis in session.ranked_analyses:
            label = f"#{analysis.rank} {analysis.candidate_name}" if analysis.rank else analysis.candidate_name
            with st.expander(f"{label} — Match {analysis.match_score:.0f}%"):
                st.write(f"Status: {analysis.status.value}")
                if analysis.decision_report:
                    recommendation = getattr(analysis.decision_report.recommendation, "value", analysis.decision_report.recommendation)
                    st.write(f"Decision: {recommendation}")
                if analysis.recruiter_copilot_report:
                    st.write(analysis.recruiter_copilot_report.recruiter_summary)
                if analysis.errors:
                    for error in analysis.errors:
                        st.warning(error)


def render_pipeline_empty_state() -> None:
    try:
        import streamlit as st
    except ImportError:
        return

    st.info("Run the Enterprise Pipeline to create a recruitment session.")
