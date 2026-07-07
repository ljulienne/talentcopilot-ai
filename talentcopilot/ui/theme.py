
def apply_theme():
    """
    Applies TalentCopilot UI theme.

    Safe fallback implementation used when the full design system
    is not available.
    """
    try:
        import streamlit as st

        st.markdown(
            '''
            <style>
            .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
            }

            h1, h2, h3 {
                letter-spacing: -0.02em;
            }

            div[data-testid="stMetric"] {
                background: rgba(250, 250, 250, 0.04);
                border-radius: 14px;
                padding: 12px;
                border: 1px solid rgba(120, 120, 120, 0.15);
            }
            </style>
            ''',
            unsafe_allow_html=True,
        )
    except Exception:
        return
