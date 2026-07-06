import streamlit as st


def render_reports_v2():
    with st.container(border=True):
        st.caption("Decision Reporting")
        st.title("📄 Decision Reports")
        st.write(
            "Generate clear, evidence-based reports to explain hiring recommendations "
            "to hiring managers and HR leaders."
        )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Reports Ready", "3")
    with col2:
        st.metric("Pending Reports", "2")
    with col3:
        st.metric("Avg Confidence", "86%")
    with col4:
        st.metric("Explainability", "100%")

    st.divider()

    left, right = st.columns([2, 1], gap="large")

    with left:
        with st.container(border=True):
            st.subheader("🧠 Report Preview")

            st.markdown("### Alice Martin · Transformation Lead")
            st.success("Strong candidate to interview")

            st.markdown("**Executive Summary**")
            st.write(
                "Alice Martin shows strong alignment with the role based on demonstrated "
                "project leadership, stakeholder management, and measurable transformation impact."
            )

            st.markdown("**Key Evidence**")
            st.write("- Led a transformation project across 4 countries.")
            st.write("- Managed executive stakeholders during a process redesign.")
            st.write("- Reduced processing time by 35% through workflow automation.")

            st.markdown("**Decision Risks**")
            st.warning("Budget ownership and exact team size should be validated during interview.")

        with st.container(border=True):
            st.subheader("🎯 Interview Priorities")
            st.write("1. Validate real ownership of transformation delivery.")
            st.write("2. Clarify stakeholder complexity and decision authority.")
            st.write("3. Confirm measurable business impact.")

    with right:
        with st.container(border=True):
            st.subheader("⚡ Report Actions")
            st.button("Generate PDF", use_container_width=True, disabled=True)
            st.button("Share with Hiring Manager", use_container_width=True, disabled=True)
            st.button("Export Evidence Summary", use_container_width=True, disabled=True)

        with st.container(border=True):
            st.subheader("📌 Report Quality")
            st.success("Evidence linked")
            st.success("Risks documented")
            st.success("Interview questions ready")
            st.info("PDF v2 coming next")

        with st.container(border=True):
            st.subheader("🤖 Copilot")
            st.info("Ask Copilot to rewrite this report for a hiring manager or HR Director.")
