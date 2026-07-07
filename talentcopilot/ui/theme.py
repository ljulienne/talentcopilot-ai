def apply_theme():
    try:
        import streamlit as st
        st.markdown(
            """
            <style>
            .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1240px; }
            h1, h2, h3 { letter-spacing: -0.03em; }
            .tc-card {
                border: 1px solid rgba(120,120,120,.18);
                border-radius: 18px;
                padding: 1rem 1.2rem;
                margin-bottom: .85rem;
                background: rgba(250,250,250,.03);
            }
            .tc-muted { opacity: .75; font-size: .95rem; }
            .tc-badge {
                display: inline-block;
                padding: .2rem .55rem;
                border-radius: 999px;
                border: 1px solid rgba(120,120,120,.2);
                margin-right: .35rem;
                font-size: .82rem;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    except Exception:
        return
