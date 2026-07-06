import streamlit as st


def render_candidates_v2():
    with st.container(border=True):
        st.caption("Talent Review")
        st.title("👥 Candidates")
        st.write(
            "Review analysed candidates, understand their decision status, "
            "and open the right workspace for deeper assessment."
        )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Candidates", "48")
    with col2:
        st.metric("Strong Fits", "9")
    with col3:
        st.metric("Need Validation", "17")
    with col4:
        st.metric("Avg Confidence", "86%")

    st.divider()

    candidates = [
        {
            "name": "Alice Martin",
            "role": "Transformation Lead",
            "status": "Strong candidate",
            "confidence": "91%",
            "summary": "Strong evidence of transformation leadership and stakeholder management.",
            "risk": "Budget ownership to validate.",
        },
        {
            "name": "Bob Lee",
            "role": "Data Analyst",
            "status": "Targeted validation",
            "confidence": "74%",
            "summary": "Good technical baseline, but stakeholder evidence is limited.",
            "risk": "Business impact not clearly quantified.",
        },
        {
            "name": "Maria Garcia",
            "role": "Restaurant Manager",
            "status": "Interview ready",
            "confidence": "82%",
            "summary": "Strong operational profile with team leadership signals.",
            "risk": "Leadership scope should be clarified.",
        },
    ]

    left, right = st.columns([2, 1], gap="large")

    with left:
        st.subheader("🧠 Candidate decision list")

        for index, candidate in enumerate(candidates):
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 1, 1])

                with c1:
                    st.markdown(f"### {candidate['name']}")
                    st.caption(candidate["role"])
                    st.write(candidate["summary"])

                with c2:
                    if candidate["status"] == "Strong candidate":
                        st.success(candidate["status"])
                    elif candidate["status"] == "Targeted validation":
                        st.warning(candidate["status"])
                    else:
                        st.info(candidate["status"])

                    st.caption("Main risk")
                    st.write(candidate["risk"])

                with c3:
                    st.caption("Confidence")
                    st.markdown(f"## {candidate['confidence']}")
                    st.button("Open Workspace", use_container_width=True, disabled=True, key=f"open_workspace_{index}")
                    st.button("Compare", use_container_width=True, disabled=True, key=f"compare_candidate_{index}")

    with right:
        with st.container(border=True):
            st.subheader("⚡ Review priorities")
            st.success("Start with Alice Martin.")
            st.warning("Validate Bob Lee before shortlisting.")
            st.info("Prepare interview questions for Maria Garcia.")

        with st.container(border=True):
            st.subheader("🤖 Copilot suggestions")
            st.write("Ask:")
            st.caption("Why is Alice recommended?")
            st.caption("What risks should I validate?")
            st.caption("Who is interview-ready?")
