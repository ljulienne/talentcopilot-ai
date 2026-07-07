def render_sidebar_brand(app_version=None, *args, **kwargs):
    try:
        import streamlit as st
        with st.sidebar:
            st.markdown("## 🧠 TalentCopilot-AI")
            st.caption(f"AI Recruitment Intelligence · {app_version}" if app_version else "AI Recruitment Intelligence")
    except Exception:
        return


def render_sidebar_context(context=None, *args, **kwargs):
    try:
        import streamlit as st
        with st.sidebar:
            st.markdown("---")
            st.caption("Recruitment Context")
            if context:
                if isinstance(context, dict):
                    st.write(context.get("title") or context.get("role") or "Active recruitment")
                else:
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
            st.write("1. Create recruitment")
            st.write("2. Upload or review candidates")
            st.write("3. Analyze evidence")
            st.write("4. Decide next step")
    except Exception:
        return
