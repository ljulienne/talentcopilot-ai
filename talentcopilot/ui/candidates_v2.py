import streamlit as st

from talentcopilot.services.session_manager import get_current_session


def _status_from_confidence(confidence: float) -> str:
    if confidence >= 85:
        return "Strong candidate"
    if confidence >= 70:
        return "Targeted validation"
    return "Review required"


def render_candidates_v2():
    session = get_current_session()
    ranked = session.ranked_results

    with st.container(border=True):
        st.caption("Talent Review")
        st.title("👥 Candidates")
        st.write(
            "Review analysed candidates, understand their decision status, "
            "and open the right workspace for deeper assessment."
        )

    total = session.total_candidates
    strong = len([r for r in ranked if r.candidate.decision_confidence >= 85])
    validation = len([r for r in ranked if 70 <= r.candidate.decision_confidence < 85])
    avg = session.average_confidence

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Candidates", total)
    with col2:
        st.metric("Strong Fits", strong)
    with col3:
        st.metric("Need Validation", validation)
    with col4:
        st.metric("Avg Confidence", f"{avg}%")

    st.divider()

    if not ranked:
        with st.container(border=True):
            st.subheader("No candidates analysed yet")
            st.info("Create or open a recruitment, upload CVs, and run the analysis to populate this page.")
        return

    left, right = st.columns([2, 1], gap="large")

    with left:
        st.subheader("🧠 Candidate decision list")

        for index, result in enumerate(ranked):
            candidate = result.candidate
            confidence = candidate.decision_confidence or candidate.score
            status = candidate.recommendation or _status_from_confidence(confidence)

            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 1, 1])

                with c1:
                    st.markdown(f"### {candidate.name}")
                    st.caption(candidate.role or session.job.title)
                    st.write(candidate.summary or "No summary available yet.")

                    if candidate.skills:
                        st.caption("Skills: " + ", ".join(candidate.skills[:6]))

                with c2:
                    if "strong" in status.lower():
                        st.success(status)
                    elif "validation" in status.lower() or "review" in status.lower():
                        st.warning(status)
                    else:
                        st.info(status)

                    st.caption("Main risk")
                    if candidate.risks:
                        st.write(candidate.risks[0])
                    else:
                        st.write("No major risk documented.")

                with c3:
                    st.caption("Decision Confidence")
                    st.markdown(f"## {int(confidence)}%")
                    st.button("Open Workspace", use_container_width=True, disabled=True, key=f"open_workspace_{index}")
                    st.button("Compare", use_container_width=True, disabled=True, key=f"compare_candidate_{index}")

    with right:
        with st.container(border=True):
            st.subheader("⚡ Review priorities")

            best = session.best_candidate
            if best:
                st.success(f"Start with {best.name}.")

            low_confidence = [
                r.candidate.name for r in ranked
                if r.candidate.decision_confidence < 70
            ]

            if low_confidence:
                st.warning(f"Validate evidence for {low_confidence[0]}.")
            else:
                st.info("No low-confidence candidate detected.")

        with st.container(border=True):
            st.subheader("🤖 Copilot suggestions")
            st.caption("Why is the top candidate recommended?")
            st.caption("Which candidates require validation?")
            st.caption("Who is ready for interview?")
