
def render_sidebar_brand():
    try:
        import streamlit as st
        with st.sidebar:
            st.markdown("## TalentCopilot-AI")
            st.caption("AI Recruitment Intelligence")
    except Exception:
        return


def render_sidebar_context():
    try:
        import streamlit as st
        with st.sidebar:
            st.markdown("---")
            st.caption("Context")
            st.write("Decision-ready candidate intelligence")
    except Exception:
        return


def render_sidebar_workflow():
    try:
        import streamlit as st
        with st.sidebar:
            st.markdown("---")
            st.caption("Workflow")
            st.write("1. Upload CV")
            st.write("2. Analyze match")
            st.write("3. Review evidence")
            st.write("4. Decide next step")
    except Exception:
        return
