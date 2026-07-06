import streamlit as st


def render_home_v2():
    with st.container(border=True):
        st.caption("AI Recruitment Decision Intelligence Platform")
        st.title("🧠 TalentCopilot AI")
        st.write(
            "Make hiring decisions faster, clearer, and more defensible with "
            "evidence-based AI."
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            st.button("Start New Recruitment", use_container_width=True, disabled=True)

        with c2:
            st.button("Open Decision Center", use_container_width=True, disabled=True)

        with c3:
            st.button("Explore Demo", use_container_width=True, disabled=True)

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.subheader("📎 Evidence First")
            st.write(
                "Every recommendation is grounded in candidate evidence, not opaque scoring."
            )

    with col2:
        with st.container(border=True):
            st.subheader("🧠 Explain Everything")
            st.write(
                "Understand why a candidate is recommended, what risks exist, and what to validate."
            )

    with col3:
        with st.container(border=True):
            st.subheader("👤 Human-in-the-loop")
            st.write(
                "TalentCopilot supports recruiters. It never replaces human hiring decisions."
            )

    st.divider()

    left, right = st.columns([2, 1], gap="large")

    with left:
        with st.container(border=True):
            st.subheader("🚀 How TalentCopilot works")

            steps = [
                ("1", "Create recruitment", "Define the role, context, and hiring expectations."),
                ("2", "Analyze candidates", "Extract evidence, skills, risks, and uncertainty."),
                ("3", "Prepare interviews", "Generate targeted questions and validation points."),
                ("4", "Make better decisions", "Use recommendations, challenges, and reports."),
            ]

            for number, title, detail in steps:
                st.markdown(f"**{number} · {title}**")
                st.caption(detail)

    with right:
        with st.container(border=True):
            st.subheader("🎯 Product focus")
            st.metric("Decision Confidence", "91%")
            st.metric("Interview Readiness", "88%")
            st.metric("Explainability", "100%")

        with st.container(border=True):
            st.subheader("🤖 Recruiter Copilot")
            st.info(
                "Soon: ask questions about candidates, evidence, risks, interview strategy, "
                "and recommendations."
            )
