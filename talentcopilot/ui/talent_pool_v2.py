import streamlit as st

from talentcopilot.services.session_manager import get_current_session


def render_talent_pool_v2():
    session = get_current_session()
    ranked = session.ranked_results

    with st.container(border=True):
        st.caption("Talent Intelligence")
        st.title("🌐 Talent Pool")
        st.write(
            "Keep track of promising candidates, reusable profiles, and future hiring opportunities."
        )

    high_potential = len([r for r in ranked if r.candidate.decision_confidence >= 85])
    interview_ready = len([r for r in ranked if r.candidate.decision_confidence >= 80])

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Available Talents", len(ranked))
    with col2:
        st.metric("High Potential", high_potential)
    with col3:
        st.metric("Interview Ready", interview_ready)
    with col4:
        st.metric("Avg Confidence", f"{session.average_confidence}%")

    st.divider()

    if not ranked:
        with st.container(border=True):
            st.subheader("No talents available yet")
            st.info("Run candidate analyses to populate the Talent Pool with live profiles.")
        return

    left, right = st.columns([2, 1], gap="large")

    with left:
        st.subheader("🧠 Live talent profiles")

        for index, result in enumerate(ranked):
            talent = result.candidate
            confidence = talent.decision_confidence or talent.score

            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 1, 1])

                with c1:
                    st.markdown(f"### {talent.name}")
                    st.caption(talent.role or session.job.title)
                    st.write(talent.summary or "Reusable candidate profile from current recruitment analysis.")

                    if talent.skills:
                        st.caption("Skills: " + ", ".join(talent.skills[:6]))

                with c2:
                    if confidence >= 85:
                        st.success("High priority")
                    elif confidence >= 75:
                        st.info("Reusable profile")
                    else:
                        st.warning("Needs validation")

                    if talent.risks:
                        st.caption("Risk")
                        st.write(talent.risks[0])

                with c3:
                    st.caption("Decision Confidence")
                    st.markdown(f"## {int(confidence)}%")
                    st.button("Open Profile", use_container_width=True, disabled=True, key=f"open_talent_{index}")
                    st.button("Match to Job", use_container_width=True, disabled=True, key=f"match_talent_{index}")

    with right:
        with st.container(border=True):
            st.subheader("⚡ Talent actions")
            st.button("Add Talent", use_container_width=True, disabled=True)
            st.button("Search Talent Pool", use_container_width=True, disabled=True)
            st.button("Find Similar Profiles", use_container_width=True, disabled=True)

        with st.container(border=True):
            st.subheader("🤖 Copilot suggestions")
            best = session.best_candidate
            if best:
                st.info(f"{best.name} could be reused for similar roles.")
            st.warning("Validate profiles with low confidence before future shortlisting.")
            st.success("High-confidence profiles can feed future recruitment campaigns.")
