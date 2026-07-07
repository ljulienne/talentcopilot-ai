
def render_sidebar_brand(app_version=None, *args, **kwargs):
    try:
        import streamlit as st
        with st.sidebar:
            st.markdown("## TalentCopilot-AI")
            st.caption(f"AI Recruitment Intelligence · {app_version}" if app_version else "AI Recruitment Intelligence")
    except Exception:
        return


def render_sidebar_context(context=None, *args, **kwargs):
    try:
        import streamlit as st
        with st.sidebar:
            st.markdown("---")
            st.caption("Context")
            if context:
                st.write(context)
            else:
                st.write("No active recruitment context")
    except Exception:
        return


def render_sidebar_workflow(*args, **kwargs):
    try:
        import streamlit as st
        with st.sidebar:
            st.markdown("---")
            st.caption("Workflow")
            st.write("1. New recruitment")
            st.write("2. Analyze candidates")
            st.write("3. Review evidence")
            st.write("4. Decide next step")
    except Exception:
        return
