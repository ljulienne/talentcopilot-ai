from talentcopilot.ui.design_system.foundations import COLORS, RADIUS, SHADOWS, TYPOGRAPHY


def apply_enterprise_theme():
    try:
        import streamlit as st
    except ImportError:
        return

    st.markdown(
        f'''
        <style>
        :root {{
            --tc-primary: {COLORS["primary"]};
            --tc-secondary: {COLORS["secondary"]};
            --tc-ai: {COLORS["ai"]};
            --tc-bg: {COLORS["background"]};
            --tc-surface: {COLORS["surface"]};
            --tc-text: {COLORS["text"]};
            --tc-muted: {COLORS["muted"]};
            --tc-border: {COLORS["border"]};
        }}
        html, body, [class*="css"] {{ font-family: {TYPOGRAPHY["font_family"]}; }}
        .stApp {{
            background: radial-gradient(circle at top left, rgba(37, 99, 235, 0.08), transparent 32rem),
                        linear-gradient(180deg, #F8FAFC 0%, #EEF2FF 100%);
        }}
        .block-container {{ max-width: 1280px; padding-top: 1.4rem; padding-bottom: 3rem; }}
        .tc-card {{
            background: var(--tc-surface);
            border: 1px solid var(--tc-border);
            border-radius: {RADIUS["lg"]};
            box-shadow: {SHADOWS["md"]};
            padding: 1.15rem;
            margin-bottom: 1rem;
        }}
        .tc-hero {{
            background: linear-gradient(135deg, #0F172A 0%, #1D4ED8 58%, #7C3AED 100%);
            color: white;
            border-radius: 26px;
            padding: 1.8rem;
            margin-bottom: 1.25rem;
            box-shadow: {SHADOWS["lg"]};
        }}
        .tc-hero h1 {{ margin: 0 0 0.35rem 0; font-size: {TYPOGRAPHY["h1"]}; letter-spacing: -0.045em; }}
        .tc-hero p {{ margin: 0; opacity: 0.88; font-size: 1rem; max-width: 780px; }}
        .tc-badge {{
            display: inline-flex; align-items: center; border-radius: 999px;
            padding: 0.25rem 0.7rem; background: rgba(255,255,255,0.14);
            border: 1px solid rgba(255,255,255,0.18); font-size: 0.78rem;
            font-weight: 700; margin-bottom: 0.75rem;
        }}
        .tc-section-title {{ font-size: 1.05rem; font-weight: 800; color: var(--tc-text); margin: 1.15rem 0 0.6rem 0; }}
        .tc-muted {{ color: var(--tc-muted); }}
        .tc-insight {{
            border-left: 4px solid var(--tc-ai); background: white; border-radius: 16px;
            padding: 0.95rem 1rem; margin-bottom: 0.65rem;
            border-top: 1px solid var(--tc-border); border-right: 1px solid var(--tc-border);
            border-bottom: 1px solid var(--tc-border);
        }}
        .tc-activity {{ display: flex; gap: 0.75rem; padding: 0.75rem 0; border-bottom: 1px solid var(--tc-border); }}
        .tc-status {{
            display: inline-flex; align-items: center; padding: 0.22rem 0.55rem;
            border-radius: 999px; font-weight: 700; font-size: 0.78rem;
            border: 1px solid var(--tc-border);
        }}
        </style>
        ''',
        unsafe_allow_html=True,
    )
