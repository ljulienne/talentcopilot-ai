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

        /* Release 7.8.0 — Premium navigation shell */
        [data-testid="stSidebar"] {{
            width: 302px !important;
            background:
                radial-gradient(circle at 20% 0%, rgba(0,212,255,.16), transparent 18rem),
                linear-gradient(180deg, #07152F 0%, #0A1835 58%, #071229 100%);
            border-right: 1px solid rgba(148,163,184,.18);
        }}
        [data-testid="stSidebar"] > div:first-child {{ padding-top: .75rem; }}
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] label {{ color: #AFC0DA; }}
        .tc-brand-lockup {{display:flex;align-items:center;gap:.72rem;padding:.35rem .15rem 1rem;margin-bottom:.2rem;border-bottom:1px solid rgba(148,163,184,.16);text-decoration:none!important;border-radius:12px}}
        .tc-brand-lockup:hover {{background:rgba(59,130,246,.08)}}
        .tc-brand-mark {{width:48px;height:48px;display:grid;place-items:center;flex:0 0 48px}}
        .tc-brand-copy {{min-width:0}}
        .tc-brand-name {{color:#F8FAFC;font-weight:850;font-size:1rem;letter-spacing:-.02em;white-space:nowrap}}
        .tc-brand-slogan {{color:#7DD3FC;font-size:.67rem;font-weight:650;line-height:1.25;margin-top:.12rem}}
        .tc-brand-version {{display:inline-block;margin-top:.22rem;color:#7387A6;font-size:.62rem}}
        .tc-mission-card {{border:1px solid rgba(125,211,252,.18);border-radius:15px;padding:.82rem .86rem;margin:.55rem 0 .75rem;background:linear-gradient(135deg,rgba(30,64,175,.22),rgba(14,165,233,.08));box-shadow:0 10px 28px rgba(0,0,0,.13)}}
        .tc-mission-kicker,.tc-sidebar-section,.tc-sidebar-next-kicker {{text-transform:uppercase;letter-spacing:.1em;font-size:.64rem;font-weight:850;color:#A8BAD2}}
        .tc-mission-role {{color:#F8FAFC;font-size:.89rem;font-weight:800;margin-top:.28rem;line-height:1.25}}
        .tc-mission-meta {{color:#C4D2E6;font-size:.72rem;margin-top:.22rem}}
        .tc-sidebar-section {{margin:1rem .35rem .35rem}}
        [data-testid="stSidebar"] .stButton > button {{min-height:2.65rem;border-radius:11px;justify-content:flex-start;text-align:left;padding:.56rem .74rem;color:#EEF4FC;background:transparent;border:1px solid transparent;box-shadow:none;font-weight:760;font-size:.89rem;letter-spacing:-.005em}}
        [data-testid="stSidebar"] .stButton > button:hover {{transform:none;color:#FFFFFF;background:rgba(59,130,246,.18);border-color:rgba(125,211,252,.28)}}
        [data-testid="stSidebar"] .stButton > button[kind="primary"] {{color:#FFFFFF;background:linear-gradient(105deg,rgba(37,99,235,.94),rgba(6,182,212,.78));border:1px solid rgba(125,211,252,.35);box-shadow:0 10px 24px rgba(2,132,199,.18);position:relative}}
        [data-testid="stSidebar"] .stButton > button[kind="primary"]:before {{content:"";width:3px;position:absolute;left:0;top:7px;bottom:7px;border-radius:999px;background:#A5F3FC}}
        [data-testid="stSidebar"] details {{border-color:rgba(148,163,184,.16);background:rgba(255,255,255,.025)}}
        [data-testid="stSidebar"] details summary {{color:#E4EDF8;font-size:.82rem;font-weight:780}}
        [data-testid="stSidebar"] [data-baseweb="select"] > div {{background:rgba(255,255,255,.06);border-color:rgba(148,163,184,.18);color:#E2E8F0}}
        .tc-sidebar-next {{margin-top:1rem;border-radius:13px;padding:.78rem .82rem;background:rgba(124,58,237,.09);border:1px solid rgba(167,139,250,.2)}}
        .tc-sidebar-next-title {{color:#FFFFFF;font-weight:820;font-size:.84rem;margin-top:.22rem}}
        .tc-nav-notice {{margin:.45rem 0;padding:.52rem .65rem;border-radius:10px;background:rgba(14,165,233,.09);border:1px solid rgba(125,211,252,.15);color:#BAE6FD;font-size:.7rem}}
        [data-testid="stSidebar"] div[role="radiogroup"] {{display:none !important;}}
        .stButton > button[kind="primary"] {{background:linear-gradient(135deg,#1D4ED8 0%,#06B6D4 100%) !important;color:white !important;border:0 !important;box-shadow:0 9px 24px rgba(29,78,216,.22) !important}}
        .stButton > button[kind="primary"]:hover {{background:linear-gradient(135deg,#1E40AF 0%,#0891B2 100%) !important}}
        .stTabs [data-baseweb="tab-list"] {{gap:.4rem;border-bottom:0;background:#EEF2F7;padding:.28rem;border-radius:13px;margin-bottom:.75rem}}
        .stTabs [data-baseweb="tab"] {{height:2.45rem;border-radius:10px;font-size:.82rem;padding:0 .9rem;color:#64748B}}
        .stTabs [aria-selected="true"] {{background:#FFFFFF;color:#1D4ED8;box-shadow:0 2px 8px rgba(15,23,42,.08)}}
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{color:#D7E3F2}}
        [data-testid="stSidebar"] .stCaptionContainer p {{color:#BDCCE0}}
        [data-testid="stSidebar"] .stButton > button:focus-visible {{outline:2px solid #67E8F9;outline-offset:2px}}
        .tc-page-export-row {{display:flex;justify-content:flex-end;gap:.5rem;margin:-.35rem 0 .8rem}}

        @media (max-width: 760px) {{
            .block-container {{ padding-left: 1rem; padding-right: 1rem; }}
            .tc-hero {{ padding: 1.3rem 1.2rem; border-radius: 19px; }}
            .tc-card {{ padding: 1rem; }}
        }}
        </style>
        ''',
        unsafe_allow_html=True,
    )
