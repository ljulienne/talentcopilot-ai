import streamlit as st

from talentcopilot.services.session_manager import get_current_session


def _priority_item(kind: str, title: str, detail: str):
    if kind == "success":
        st.success(f"**{title}**\n\n{detail}")
    elif kind == "warning":
        st.warning(f"**{title}**\n\n{detail}")
    else:
        st.info(f"**{title}**\n\n{detail}")


def render_dashboard_v2():
    session = get_current_session()

    total_candidates = session.total_candidates
    avg_confidence = session.average_confidence
    best_candidate = session.best_candidate

    with st.container(border=True):
        st.caption("AI Recruitment Decision Intelligence")
        st.title("📊 Decision Center")
        st.write(
            "Your daily cockpit to track recruitments, review AI recommendations, "
            "and move faster from evidence to hiring decisions."
        )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Open Recruitments", "3", "+1")
    with col2:
        st.metric("Candidates Analysed", total_candidates)
    with col3:
        st.metric("Interview Ready", "9", "+3")
    with col4:
        st.metric("Avg Confidence", f"{avg_confidence}%")

    st.divider()

    left, middle, right = st.columns([1.4, 1.4, 1], gap="large")

    with left:
        with st.container(border=True):
            st.subheader("🚀 Today's priorities")
            _priority_item(
                "success",
                "3 candidates ready for interview",
                "Strong evidence and sufficient decision readiness detected.",
            )
            _priority_item(
                "warning",
                "2 profiles require validation",
                "Missing information should be clarified before recommendation.",
            )
            _priority_item(
                "info",
                "1 report waiting to be generated",
                "A decision report can be prepared for the hiring manager.",
            )

    with middle:
        with st.container(border=True):
            st.subheader("🧭 Recruitment pipeline")
            st.progress(0.72, text="72% of active candidates analysed")
            st.write("**New** · 12 candidates")
            st.write("**Analysed** · 48 candidates")
            st.write("**Shortlisted** · 9 candidates")
            st.write("**Interview** · 4 candidates")
            st.write("**Decision** · 2 candidates")

    with right:
        with st.container(border=True):
            st.subheader("⚡ Quick actions")
            st.button("New Recruitment", use_container_width=True, disabled=True)
            st.button("Open Decision Workspace", use_container_width=True, disabled=True)
            st.button("Compare Candidates", use_container_width=True, disabled=True)
            st.button("Generate Report", use_container_width=True, disabled=True)

    st.divider()

    col_a, col_b = st.columns([2, 1], gap="large")

    with col_a:
        with st.container(border=True):
            st.subheader("🧠 Recent Decision Workspaces")

            candidates = [
                ("Alice Martin", "Transformation Lead", "Strong candidate", "91%"),
                ("Bob Lee", "Data Analyst", "Targeted validation", "74%"),
                ("Maria Garcia", "Restaurant Manager", "Interview ready", "82%"),
            ]

            for name, role, status, confidence in candidates:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2, 2, 1])
                    with c1:
                        st.markdown(f"**{name}**")
                        st.caption(role)
                    with c2:
                        st.write(status)
                    with c3:
                        st.caption("Confidence")
                        st.markdown(f"**{confidence}**")

    with col_b:
        with st.container(border=True):
            st.subheader("🤖 AI suggestions")
            st.info("Start with candidates that have high confidence and low uncertainty.")
            st.warning("Validate missing evidence before sharing a recommendation.")
            st.success("Use Interview Intelligence before moving shortlisted candidates forward.")
