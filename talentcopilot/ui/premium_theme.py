def apply_premium_ui():
    try:
        import streamlit as st
        st.markdown(
            """
            <style>
            [data-testid="stSidebar"] { border-right: 1px solid rgba(120,120,120,.18); }
            div[data-testid="stMetric"] {
                border-radius: 16px;
                padding: 14px;
                border: 1px solid rgba(120,120,120,.16);
                background: rgba(250,250,250,.025);
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    except Exception:
        return


def premium_sidebar_brand(*args, **kwargs):
    try:
        import streamlit as st
        with st.sidebar:
            st.markdown("## TalentCopilot-AI")
            st.caption("AI Recruitment Intelligence")
    except Exception:
        return
