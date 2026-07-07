import streamlit as st

from talentcopilot.services.session_manager import get_current_session


def render_recruiter_copilot_v2():
    session = get_current_session()
    best = session.best_candidate

    with st.container(border=True):
        st.caption("AI Recruiter Assistant")
        st.title("🤖 Recruiter Copilot")
        st.write(
            "Ask questions about candidates, risks, evidence, interviews, and recommendations."
        )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Active Context", session.job.title)
    with col2:
        st.metric("Candidates", session.total_candidates)
    with col3:
        st.metric("Avg Confidence", f"{session.average_confidence}%")
    with col4:
        st.metric("Top Candidate", best.name if best else "None")

    st.divider()

    if not best:
        with st.container(border=True):
            st.subheader("No live context yet")
            st.info("Run a recruitment analysis first to activate Copilot with real candidate data.")
        return

    left, right = st.columns([2, 1], gap="large")

    with left:
        with st.container(border=True):
            st.subheader("💬 Ask Copilot")

            st.text_area(
                "Your question",
                placeholder=f"Example: Why is {best.name} recommended?",
                height=120,
            )

            st.button("Ask Copilot", use_container_width=True, disabled=True)
            st.caption("Conversational reasoning will be activated progressively.")

        with st.container(border=True):
            st.subheader("🧠 Context-aware example answer")

            st.info(
                f"{best.name} is currently the strongest available candidate for "
                f"{session.job.title}. The recommendation is based on a decision confidence "
                f"of {int(best.decision_confidence)}%, the available skills, and the current "
                f"analysis results. The recruiter should still validate key risks and missing "
                f"information before making a final decision."
            )

        with st.container(border=True):
            st.subheader("📌 Suggested prompts")

            prompts = [
                f"Why is {best.name} recommended?",
                "What are the top risks?",
                "What should I validate during the interview?",
                "Summarize this candidate for a hiring manager.",
                "Challenge the recommendation.",
                "Which candidate should I interview first?",
            ]

            for index, item in enumerate(prompts):
                st.button(item, use_container_width=True, disabled=True, key=f"copilot_prompt_{index}")

    with right:
        with st.container(border=True):
            st.subheader("🎯 Copilot modes")
            st.success("Decision explanation")
            st.info("Interview preparation")
            st.warning("Risk validation")
            st.info("Hiring manager summary")

        with st.container(border=True):
            st.subheader("🔎 Current context")
            st.write(f"**Candidate:** {best.name}")
            st.write(f"**Role:** {session.job.title}")
            st.write(f"**Recommendation:** {best.recommendation}")
            st.write(f"**Confidence:** {int(best.decision_confidence)}%")

        with st.container(border=True):
            st.subheader("⚡ Next actions")
            st.button("Open Decision Workspace", use_container_width=True, disabled=True)
            st.button("Generate Interview Guide", use_container_width=True, disabled=True)
            st.button("Create Report Summary", use_container_width=True, disabled=True)
