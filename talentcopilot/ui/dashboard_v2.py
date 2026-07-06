import streamlit as st


def render_dashboard_v2():
    with st.container(border=True):
        st.caption("AI Recruitment Decision Intelligence")
        st.title("📊 Decision Center")
        st.write("Your recruitment cockpit for priorities, decisions, and AI-assisted hiring actions.")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Open Recruitments", "3", "+1")
    with col2:
        st.metric("Candidates Analysed", "48", "+12")
    with col3:
        st.metric("Interview Ready", "9", "+3")
    with col4:
        st.metric("Avg Confidence", "86%", "+4%")

    left, right = st.columns([2, 1], gap="large")

    with left:
        with st.container(border=True):
            st.subheader("🚀 Today's priorities")
            st.success("Review 3 strong candidates ready for interview.")
            st.warning("Validate missing information for 2 profiles.")
            st.info("Generate decision reports for shortlisted candidates.")

        with st.container(border=True):
            st.subheader("🧠 Recent Decision Workspaces")
            st.write("**Alice Martin** · Transformation Lead · Strong candidate")
            st.write("**Bob Lee** · Data Analyst · Targeted validation needed")
            st.write("**Maria Garcia** · Restaurant Manager · Interview ready")

    with right:
        with st.container(border=True):
            st.subheader("📌 Current focus")
            st.write("Transformation Lead")
            st.caption("3 candidates shortlisted")

        with st.container(border=True):
            st.subheader("⚡ Quick actions")
            st.button("Open Decision Workspace", use_container_width=True, disabled=True)
            st.button("Generate Report", use_container_width=True, disabled=True)
            st.button("Compare Candidates", use_container_width=True, disabled=True)
