import streamlit as st

from talentcopilot.services.session_manager import get_current_session


def render_dashboard_v2():
    session = get_current_session()
    ranked = session.ranked_results
    best = session.best_candidate

    with st.container(border=True):
        st.caption("AI Recruitment Decision Intelligence")
        st.title("📊 Decision Center")
        st.write(
            "Your daily cockpit to track recruitments, review AI recommendations, "
            "and move faster from evidence to hiring decisions."
        )

    total = session.total_candidates
    avg = session.average_confidence
    interview_ready = len([r for r in ranked if r.candidate.decision_confidence >= 80])
    validation_needed = len([r for r in ranked if r.candidate.decision_confidence < 80])

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Candidates Analysed", total)
    with col2:
        st.metric("Interview Ready", interview_ready)
    with col3:
        st.metric("Need Validation", validation_needed)
    with col4:
        st.metric("Avg Confidence", f"{avg}%")

    st.divider()

    if not ranked:
        with st.container(border=True):
            st.subheader("No live analysis yet")
            st.info("Create or open a recruitment, upload CVs, and run the analysis to populate the Decision Center.")
        return

    left, middle, right = st.columns([1.4, 1.4, 1], gap="large")

    with left:
        with st.container(border=True):
            st.subheader("🚀 Today's priorities")

            if best:
                st.success(f"**Review top candidate**\n\nStart with {best.name} for {session.job.title}.")

            if validation_needed:
                st.warning(f"**Validate uncertain profiles**\n\n{validation_needed} candidate(s) require additional validation.")

            st.info("**Prepare interviews**\n\nUse Interview Intelligence before moving candidates forward.")

    with middle:
        with st.container(border=True):
            st.subheader("🧭 Recruitment pipeline")

            analysed_ratio = min(1.0, total / max(total, 1))
            st.progress(analysed_ratio, text=f"{total} candidate(s) analysed")

            st.write(f"**Analysed** · {total}")
            st.write(f"**Interview Ready** · {interview_ready}")
            st.write(f"**Need Validation** · {validation_needed}")
            st.write(f"**Top Candidate** · {best.name if best else 'None'}")

    with right:
        with st.container(border=True):
            st.subheader("📌 Current focus")
            st.write(session.job.title)
            if session.job.company:
                st.caption(session.job.company)
            if best:
                st.caption(f"Top candidate: {best.name}")

        with st.container(border=True):
            st.subheader("⚡ Quick actions")
            st.button("Open Decision Workspace", use_container_width=True, disabled=True)
            st.button("Compare Candidates", use_container_width=True, disabled=True)
            st.button("Generate Report", use_container_width=True, disabled=True)

    st.divider()

    col_a, col_b = st.columns([2, 1], gap="large")

    with col_a:
        with st.container(border=True):
            st.subheader("🧠 Recent Decision Workspaces")

            for index, result in enumerate(ranked[:5], start=1):
                candidate = result.candidate
                confidence = candidate.decision_confidence or candidate.score

                with st.container(border=True):
                    c1, c2, c3 = st.columns([2, 2, 1])
                    with c1:
                        st.markdown(f"**{index}. {candidate.name}**")
                        st.caption(candidate.role or session.job.title)
                    with c2:
                        st.write(candidate.recommendation)
                    with c3:
                        st.caption("Confidence")
                        st.markdown(f"**{int(confidence)}%**")

    with col_b:
        with st.container(border=True):
            st.subheader("🤖 AI suggestions")

            if best:
                st.info(f"Start with {best.name}: highest current decision confidence.")

            if validation_needed:
                st.warning("Review candidates below 80% confidence before shortlisting.")

            st.success("Generate interview questions before final decision.")
