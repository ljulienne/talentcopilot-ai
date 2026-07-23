from talentcopilot.ui.design_system.foundations import COLORS, RADIUS, SHADOWS, TYPOGRAPHY


def apply_enterprise_theme():
    """Apply the shared premium presentation layer.

    The function is intentionally import-safe outside Streamlit and contains no
    business logic.
    """
    try:
        import streamlit as st
    except ImportError:
        return

    st.markdown(
        f'''
        <style>
        :root {{
            --tc-primary: {COLORS["primary"]};
            --tc-primary-strong: {COLORS["primary_strong"]};
            --tc-secondary: {COLORS["secondary"]};
            --tc-ai: {COLORS["ai"]};
            --tc-success: {COLORS["success"]};
            --tc-warning: {COLORS["warning"]};
            --tc-danger: {COLORS["danger"]};
            --tc-info: {COLORS["info"]};
            --tc-bg: {COLORS["background"]};
            --tc-surface: {COLORS["surface"]};
            --tc-surface-subtle: {COLORS["surface_subtle"]};
            --tc-text: {COLORS["text"]};
            --tc-muted: {COLORS["muted"]};
            --tc-border: {COLORS["border"]};
            --tc-border-strong: {COLORS["border_strong"]};
        }}
        html, body, [class*="css"] {{
            font-family: {TYPOGRAPHY["font_family"]};
            color: var(--tc-text);
        }}
        .stApp {{
            background:
                radial-gradient(circle at 6% 0%, rgba(79,70,229,.08), transparent 30rem),
                radial-gradient(circle at 94% 5%, rgba(14,165,233,.07), transparent 28rem),
                linear-gradient(180deg, #FAFBFF 0%, var(--tc-bg) 100%);
        }}
        .block-container {{
            max-width: 1240px;
            padding-top: 1.15rem;
            padding-bottom: 3.5rem;
        }}
        [data-testid="stSidebar"] {{
            border-right: 1px solid var(--tc-border);
            background: rgba(255,255,255,.96);
        }}
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
            color: var(--tc-muted);
        }}
        h1, h2, h3 {{ letter-spacing: -.025em; }}
        p, li {{ line-height: 1.58; }}
        .tc-card {{
            background: rgba(255,255,255,.96);
            border: 1px solid var(--tc-border);
            border-radius: {RADIUS["lg"]};
            box-shadow: {SHADOWS["sm"]};
            padding: 1.15rem 1.2rem;
            margin-bottom: 1rem;
        }}
        .tc-card:hover {{
            border-color: var(--tc-border-strong);
            box-shadow: {SHADOWS["md"]};
        }}
        .tc-hero {{
            position: relative;
            overflow: hidden;
            background:
                radial-gradient(circle at 85% 20%, rgba(255,255,255,.18), transparent 16rem),
                linear-gradient(135deg, #111827 0%, #312E81 52%, #4F46E5 100%);
            color: white;
            border: 1px solid rgba(255,255,255,.12);
            border-radius: {RADIUS["xl"]};
            padding: 1.65rem 1.75rem;
            margin-bottom: 1.15rem;
            box-shadow: {SHADOWS["lg"]};
        }}
        .tc-hero h1 {{
            margin: 0 0 .38rem 0;
            font-size: {TYPOGRAPHY["h1"]};
            line-height: 1.08;
            letter-spacing: -.045em;
        }}
        .tc-hero p {{
            margin: 0;
            opacity: .88;
            font-size: .98rem;
            max-width: 790px;
        }}
        .tc-badge, .tc-status {{
            display: inline-flex;
            align-items: center;
            gap: .36rem;
            border-radius: {RADIUS["pill"]};
            padding: .28rem .68rem;
            font-size: .76rem;
            font-weight: 750;
            line-height: 1.2;
            border: 1px solid transparent;
        }}
        .tc-badge {{
            margin-bottom: .7rem;
            background: rgba(255,255,255,.13);
            border-color: rgba(255,255,255,.18);
        }}
        .tc-section-title {{
            font-size: {TYPOGRAPHY["h3"]};
            font-weight: 800;
            color: var(--tc-text);
            margin: 1.25rem 0 .2rem 0;
        }}
        .tc-section-subtitle {{
            color: var(--tc-muted);
            font-size: .86rem;
            margin: 0 0 .72rem 0;
        }}
        .tc-muted {{ color: var(--tc-muted); }}
        .tc-insight {{
            position: relative;
            border: 1px solid #DDD6FE;
            background: linear-gradient(135deg, #FFFFFF 0%, #FAF5FF 100%);
            border-radius: {RADIUS["lg"]};
            padding: 1rem 1.05rem;
            margin-bottom: .75rem;
            box-shadow: {SHADOWS["sm"]};
        }}
        .tc-insight:before {{
            content: "";
            position: absolute;
            left: 0;
            top: 14px;
            bottom: 14px;
            width: 4px;
            border-radius: 0 999px 999px 0;
            background: linear-gradient(180deg, var(--tc-ai), var(--tc-primary));
        }}
        .tc-activity {{
            display: flex;
            gap: .75rem;
            padding: .8rem 0;
            border-bottom: 1px solid var(--tc-border);
        }}
        div[data-testid="stMetric"] {{
            background: rgba(255,255,255,.94);
            border: 1px solid var(--tc-border);
            border-radius: {RADIUS["md"]};
            padding: .85rem .95rem;
            box-shadow: {SHADOWS["sm"]};
        }}
        div[data-testid="stMetric"] label {{ color: var(--tc-muted); }}
        div[data-testid="stMetricValue"] {{ letter-spacing: -.035em; }}
        div[data-testid="stExpander"] {{
            border: 1px solid var(--tc-border);
            border-radius: {RADIUS["md"]};
            background: rgba(255,255,255,.9);
            overflow: hidden;
        }}
        div[data-testid="stDataFrame"] {{
            border: 1px solid var(--tc-border);
            border-radius: {RADIUS["md"]};
            overflow: hidden;
        }}
        .stButton > button {{
            border-radius: 11px;
            min-height: 2.55rem;
            font-weight: 750;
            transition: transform .12s ease, box-shadow .12s ease, border-color .12s ease;
        }}
        .stButton > button:hover {{ transform: translateY(-1px); }}
        .stButton > button[kind="primary"] {{
            background: linear-gradient(135deg, var(--tc-primary-strong), var(--tc-primary));
            border: 0;
            box-shadow: 0 8px 22px rgba(79,70,229,.23);
        }}
        .stButton > button:focus-visible {{ box-shadow: {SHADOWS["focus"]}; }}
        .stTabs [data-baseweb="tab-list"] {{
            gap: .35rem;
            border-bottom: 1px solid var(--tc-border);
        }}
        .stTabs [data-baseweb="tab"] {{
            border-radius: 10px 10px 0 0;
            font-weight: 700;
        }}
        @media (max-width: 760px) {{
            .block-container {{ padding-left: 1rem; padding-right: 1rem; }}
            .tc-hero {{ padding: 1.3rem 1.2rem; border-radius: 19px; }}
            .tc-card {{ padding: 1rem; }}
        }}
        </style>
        ''',
        unsafe_allow_html=True,
    )
