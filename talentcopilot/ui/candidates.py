def render_candidates(*args, **kwargs):
    try:
        import streamlit as st

        st.title("Candidates")
        st.caption("Candidate workspace.")

        cols = st.columns(4)
        for col, label, value in zip(cols, ['Status', 'AI', 'Evidence', 'Decision'], ['Ready', 'Enabled', 'Tracked', 'Supported']):
            col.metric(label, value)

        st.markdown("---")
        st.subheader("Candidates workspace")
        st.write("This page provides a stable candidates interface for TalentCopilot without temporary v2 labels.")

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
