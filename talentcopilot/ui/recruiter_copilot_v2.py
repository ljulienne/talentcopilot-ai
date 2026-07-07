import streamlit as st


def render_recruiter_copilot_v2():
    with st.container(border=True):
        st.caption("AI Recruiter Assistant")
        st.title("🤖 Recruiter Copilot")
        st.write(
            "Ask questions about candidates, risks, evidence, interviews, and recommendations."
        )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Active Context", "Decision")
    with col2:
        st.metric("Evidence Items", "12")
    with col3:
        st.metric("Risks Detected", "3")
    with col4:
        st.metric("Interview Questions", "8")

    st.divider()

    left, right = st.columns([2, 1], gap="large")

    with left:
        with st.container(border=True):
            st.subheader("💬 Ask Copilot")

            prompt = st.text_area(
                "Your question",
                placeholder="Example: Why is Alice Martin recommended?",
                height=120,
            )

            st.button("Ask Copilot", use_container_width=True, disabled=True)

            st.caption("Conversational reasoning will be activated progressively.")

        with st.container(border=True):
            st.subheader("🧠 Example answer")

            st.info(
                "Alice Martin is recommended because her profile shows strong evidence of "
                "transformation leadership, stakeholder management, and measurable impact. "
                "The recommendation should still be challenged by validating budget ownership "
                "and the exact scope of her leadership responsibilities."
            )

        with st.container(border=True):
            st.subheader("📌 Suggested prompts")

            prompts = [
                "Why is this candidate recommended?",
                "What are the top 3 risks?",
                "What should I validate during the interview?",
                "Summarize this candidate for a hiring manager.",
                "Challenge the recommendation.",
                "Compare Alice and Maria on leadership.",
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
            st.write("**Candidate:** Alice Martin")
            st.write("**Role:** Transformation Lead")
            st.write("**Recommendation:** Strong candidate")
            st.write("**Confidence:** 91%")

        with st.container(border=True):
            st.subheader("⚡ Next actions")
            st.button("Open Decision Workspace", use_container_width=True, disabled=True)
            st.button("Generate Interview Guide", use_container_width=True, disabled=True)
            st.button("Create Report Summary", use_container_width=True, disabled=True)
