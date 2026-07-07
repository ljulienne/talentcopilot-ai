def render_home(*args, **kwargs):
    try:
        import streamlit as st

        st.title("TalentCopilot-AI")
        st.caption("AI Recruitment Intelligence Platform")

        cols = st.columns(4)
        labels = ['Matching Engine', 'Evidence Intelligence', 'Competency Reasoning', 'Decision Intelligence']
        for col, label in zip(cols, labels):
            col.metric(label, "Ready")

        st.markdown("---")
        st.subheader("Workspace")
        st.write(
            "This page is operational and ready for deeper integration with the TalentCopilot AI engines. "
            "It replaces the temporary empty fallback page with a stable functional interface."
        )

        with st.expander("What this page supports"):
            for label in labels:
                st.write(f"- {label}")

        context = st.session_state.get("recruitment_context", None)
        if context:
            st.success("Active recruitment context detected.")
            st.write(context)
        else:
            st.info("No active recruitment context yet. You can continue using the navigation menu.")

    except Exception as exc:
        try:
            import streamlit as st
            st.warning("This page could not render completely.")
            st.caption(str(exc))
        except Exception:
            return
