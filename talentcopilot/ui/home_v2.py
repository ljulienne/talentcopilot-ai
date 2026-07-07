def render_home_v2(*args, **kwargs):
    try:
        import streamlit as st

        st.title("Home")
        st.caption("TalentCopilot-AI recruitment intelligence workspace.")

        cols = st.columns(4)
        for col, label, value in zip(cols, ['Status', 'AI', 'Evidence', 'Decision'], ['Ready', 'Enabled', 'Tracked', 'Supported']):
            col.metric(label, value)

        st.markdown("---")
        st.subheader("Home workspace")
        st.write("This page provides a stable home interface for TalentCopilot without temporary v2 labels.")

        with st.expander("Available capabilities"):
            for item in ['Stable rendering', 'Recruitment context', 'Decision support', 'Future advanced UI']:
                st.write(f"- {item}")

        context = st.session_state.get("recruitment_context", None)
        if context:
            st.success("Active recruitment context detected.")
        else:
            st.info("No active recruitment context yet.")

    except Exception as exc:
        try:
            import streamlit as st
            st.warning("This page could not render completely.")
            st.caption(str(exc))
        except Exception:
            return
