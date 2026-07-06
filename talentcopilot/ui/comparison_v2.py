import streamlit as st


def render_comparison_v2():
    with st.container(border=True):
        st.caption("Decision Comparison")
        st.title("⚖️ Candidate Comparison")
        st.write(
            "Compare candidates beyond scores: evidence quality, demonstrated skills, "
            "risks, uncertainty, and interview priorities."
        )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Candidates Compared", "3")
    with col2:
        st.metric("Top Confidence", "91%")
    with col3:
        st.metric("Main Trade-offs", "4")
    with col4:
        st.metric("Risks to Validate", "6")

    st.divider()

    left, right = st.columns([2, 1], gap="large")

    with left:
        with st.container(border=True):
            st.subheader("🏆 Recommendation")
            st.success("Alice Martin is currently the strongest candidate to prioritize.")
            st.write(
                "Alice shows the best balance of demonstrated skills, evidence quality, "
                "manageable risk, and interview readiness."
            )

        with st.container(border=True):
            st.subheader("📊 Decision matrix")

            rows = [
                ("Evidence Quality", "High", "Medium", "Medium"),
                ("Demonstrated Skills", "High", "Medium", "High"),
                ("Business Impact", "Strong", "Limited", "Moderate"),
                ("Risk Level", "Medium", "High", "Medium"),
                ("Interview Readiness", "High", "Medium", "High"),
            ]

            st.table(
                {
                    "Dimension": [r[0] for r in rows],
                    "Alice Martin": [r[1] for r in rows],
                    "Bob Lee": [r[2] for r in rows],
                    "Maria Garcia": [r[3] for r in rows],
                }
            )

        with st.container(border=True):
            st.subheader("🔁 Trade-offs")
            st.info(
                "Alice is stronger for immediate readiness. Bob may be interesting if "
                "the organization values technical potential and can invest in onboarding."
            )
            st.warning(
                "Maria appears operationally strong but requires validation of leadership scope."
            )

    with right:
        with st.container(border=True):
            st.subheader("🥇 Ranking")
            st.write("1. **Alice Martin** · 91%")
            st.write("2. **Maria Garcia** · 82%")
            st.write("3. **Bob Lee** · 74%")

        with st.container(border=True):
            st.subheader("🎯 Interview focus")
            st.write("**Alice**: validate budget ownership.")
            st.write("**Maria**: clarify team scope.")
            st.write("**Bob**: validate business stakeholder exposure.")

        with st.container(border=True):
            st.subheader("⚖️ Challenge")
            st.warning(
                "The recommendation could change if the hiring priority shifts from "
                "immediate readiness to long-term potential."
            )
