import streamlit as st


def render_copilot_panel():
    with st.container(border=True):
        st.subheader("🤖 Recruiter Copilot")
        st.caption("Always-on decision assistant")

        st.info("Ask questions about candidates, risks, evidence, or next steps.")

        st.markdown("**Suggested prompts**")
        st.button("Why this recommendation?", use_container_width=True, disabled=True)
        st.button("What are the main risks?", use_container_width=True, disabled=True)
        st.button("Prepare interview questions", use_container_width=True, disabled=True)
        st.button("Summarize for hiring manager", use_container_width=True, disabled=True)


def render_page_shell(page_renderer):
    main, right = st.columns([4, 1.25], gap="large")

    with main:
        page_renderer()

    with right:
        render_copilot_panel()
