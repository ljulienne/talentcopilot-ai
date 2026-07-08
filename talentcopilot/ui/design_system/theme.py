from talentcopilot.ui.design_system.foundations import COLORS, RADIUS, SHADOWS


def apply_enterprise_theme():
    try:
        import streamlit as st
    except ImportError:
        return

    st.markdown(
        f"""
        <style>
        :root {{
            --tc-primary: {COLORS["primary"]};
            --tc-secondary: {COLORS["secondary"]};
            --tc-ai: {COLORS["ai"]};
            --tc-success: {COLORS["success"]};
            --tc-warning: {COLORS["warning"]};
            --tc-danger: {COLORS["danger"]};
            --tc-bg: {COLORS["background"]};
            --tc-surface: {COLORS["surface"]};
            --tc-text: {COLORS["text"]};
            --tc-muted: {COLORS["muted"]};
            --tc-border: {COLORS["border"]};
        }}

        .stApp {{
            background: linear-gradient(180deg, #F8FAFC 0%, #EEF2FF 100%);
        }}

        .block-container {{
            max-width: 1280px;
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }}

        [data-testid="stSidebar"] {{
            background: #0F172A;
            color: white;
            border-right: 1px solid rgba(255,255,255,0.08);
        }}

        [data-testid="stSidebar"] * {{
            color: inherit;
        }}

        .tc-shell-card {{
            background: white;
            border: 1px solid var(--tc-border);
            border-radius: {RADIUS["lg"]};
            box-shadow: {SHADOWS["md"]};
            padding: 1.25rem;
            margin-bottom: 1rem;
        }}

        .tc-hero {{
            background: linear-gradient(135deg, #0F172A 0%, #1D4ED8 58%, #7C3AED 100%);
            color: white;
            border-radius: 24px;
            padding: 1.75rem;
            margin-bottom: 1.25rem;
            box-shadow: {SHADOWS["md"]};
        }}

        .tc-hero h1 {{
            margin: 0 0 0.35rem 0;
            font-size: 2rem;
            letter-spacing: -0.04em;
        }}

        .tc-hero p {{
            margin: 0;
            opacity: 0.85;
            font-size: 1rem;
        }}

        .tc-badge {{
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.25rem 0.65rem;
            background: rgba(255,255,255,0.14);
            border: 1px solid rgba(255,255,255,0.18);
            font-size: 0.78rem;
            font-weight: 600;
            margin-bottom: 0.8rem;
        }}

        .tc-section-title {{
            font-size: 1.05rem;
            font-weight: 750;
            color: var(--tc-text);
            margin: 1.2rem 0 0.6rem 0;
        }}

        .tc-muted {{
            color: var(--tc-muted);
        }}

        .tc-priority {{
            border-left: 4px solid var(--tc-ai);
            background: white;
            border-radius: 14px;
            padding: 0.95rem 1rem;
            margin-bottom: 0.65rem;
            border-top: 1px solid var(--tc-border);
            border-right: 1px solid var(--tc-border);
            border-bottom: 1px solid var(--tc-border);
        }}

        .tc-activity {{
            display: flex;
            gap: 0.75rem;
            padding: 0.75rem 0;
            border-bottom: 1px solid var(--tc-border);
        }}

        .tc-logo-mark {{
            width: 38px;
            height: 38px;
            border-radius: 12px;
            background: linear-gradient(135deg, #2563EB, #7C3AED);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 800;
            margin-right: 0.6rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
