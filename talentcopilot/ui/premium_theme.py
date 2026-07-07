
def apply_premium_ui():
    """
    Applies premium TalentCopilot UI styling.
    Safe fallback if the full design system is unavailable.
    """
    try:
        import streamlit as st

        st.markdown(
            '''
            <style>
            .block-container {
                max-width: 1200px;
                padding-top: 2rem;
            }

            [data-testid="stSidebar"] {
                border-right: 1px solid rgba(120, 120, 120, 0.18);
            }

            div[data-testid="stMetric"] {
                border-radius: 16px;
                padding: 14px;
                border: 1px solid rgba(120, 120, 120, 0.16);
            }
            </style>
            ''',
            unsafe_allow_html=True,
        )
    except Exception:
        return


def premium_sidebar_brand():
    """
    Renders a safe sidebar brand block.
    """
    try:
        import streamlit as st

        with st.sidebar:
            st.markdown("## TalentCopilot-AI")
            st.caption("AI Recruitment Intelligence")
    except Exception:
        return
