import streamlit as st


def render_sidebar_brand(version: str) -> None:
    st.sidebar.markdown("## 🧠 TalentCopilot AI")
    st.sidebar.caption(f"Decision Intelligence Platform · v{version}")
    st.sidebar.markdown("---")


def render_sidebar_workflow() -> None:
    st.sidebar.markdown("### 🚀 Workflow")

    with st.sidebar.container(border=True):
        st.markdown("**1 · Create**")
        st.caption("New recruitment context")

        st.markdown("**2 · Analyze**")
        st.caption("AI candidate analysis")

        st.markdown("**3 · Decide**")
        st.caption("Decision Workspace")

        st.markdown("**4 · Validate**")
        st.caption("Interview Intelligence")

        st.markdown("**5 · Report**")
        st.caption("Decision report")

    st.sidebar.markdown("---")


def render_sidebar_context(context) -> None:
    if not context:
        st.sidebar.info("No active recruitment yet.")
        return

    with st.sidebar.container(border=True):
        st.markdown("**Current Recruitment**")
        st.caption(context.get("job_title", "Untitled recruitment"))
        if context.get("company"):
            st.caption(context.get("company"))
        if context.get("location"):
            st.caption(context.get("location"))

    st.sidebar.markdown("---")
