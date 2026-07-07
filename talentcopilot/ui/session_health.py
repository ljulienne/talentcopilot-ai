import streamlit as st

from talentcopilot.services.session_manager import get_current_session


def render_session_health():
    session = get_current_session()

    with st.container(border=True):
        st.caption("System Health")
        st.title("🩺 Live Session Health")
        st.write("Check whether TalentCopilot is using live recruitment data correctly.")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Candidates", session.total_candidates)
    with col2:
        st.metric("Avg Confidence", f"{session.average_confidence}%")
    with col3:
        st.metric("Best Candidate", session.best_candidate.name if session.best_candidate else "None")
    with col4:
        st.metric("Job", session.job.title)

    st.divider()

    with st.container(border=True):
        st.subheader("Recruitment Context")
        st.json(session.job.__dict__)

    with st.container(border=True):
        st.subheader("Ranked Candidates")

        if not session.ranked_results:
            st.info("No analysed candidates in current session.")
            return

        for result in session.ranked_results:
            st.write(
                {
                    "rank": result.rank,
                    "name": result.candidate.name,
                    "confidence": result.candidate.decision_confidence,
                    "score": result.candidate.score,
                    "recommendation": result.candidate.recommendation,
                }
            )
