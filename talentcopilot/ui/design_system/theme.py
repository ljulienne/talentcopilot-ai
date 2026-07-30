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
        [data-testid="stSidebar"] .stButton > button[kind="primary"],
        [data-testid="stSidebar"] button[data-testid="stBaseButton-primary"],
        [data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {{
            color:#FFFFFF !important;
            background:linear-gradient(105deg,rgba(37,99,235,.96),rgba(6,182,212,.82)) !important;
            border:1px solid rgba(125,211,252,.38) !important;
            box-shadow:0 10px 24px rgba(2,132,199,.18) !important;
            position:relative;
        }}
        [data-testid="stSidebar"] .stButton > button[kind="primary"]:before,
        [data-testid="stSidebar"] button[data-testid="stBaseButton-primary"]:before,
        [data-testid="stSidebar"] [data-testid="stBaseButton-primary"]:before {{
            content:"";
            width:3px;
            position:absolute;
            left:0;
            top:7px;
            bottom:7px;
            border-radius:999px;
            background:#A5F3FC;
        }}
        [data-testid="stSidebar"] details {{border-color:rgba(148,163,184,.16);background:rgba(255,255,255,.025)}}
        [data-testid="stSidebar"] details summary {{color:#E4EDF8;font-size:.82rem;font-weight:780}}
        [data-testid="stSidebar"] [data-baseweb="select"] > div {{background:rgba(255,255,255,.06);border-color:rgba(148,163,184,.18);color:#E2E8F0}}
        .tc-sidebar-next {{margin-top:1rem;border-radius:13px;padding:.78rem .82rem;background:rgba(124,58,237,.09);border:1px solid rgba(167,139,250,.2)}}
        .tc-sidebar-next-title {{color:#FFFFFF;font-weight:820;font-size:.84rem;margin-top:.22rem}}
        .tc-nav-notice {{margin:.45rem 0;padding:.52rem .65rem;border-radius:10px;background:rgba(14,165,233,.09);border:1px solid rgba(125,211,252,.15);color:#BAE6FD;font-size:.7rem}}
        [data-testid="stSidebar"] div[role="radiogroup"] {{display:none !important;}}
        .stButton > button[kind="primary"],
        button[data-testid="stBaseButton-primary"],
        [data-testid="stBaseButton-primary"] {{background:linear-gradient(135deg,#1D4ED8 0%,#06B6D4 100%) !important;color:white !important;border:0 !important;box-shadow:0 9px 24px rgba(29,78,216,.22) !important}}
        .stButton > button[kind="primary"]:hover,
        button[data-testid="stBaseButton-primary"]:hover,
        [data-testid="stBaseButton-primary"]:hover {{background:linear-gradient(135deg,#1E40AF 0%,#0891B2 100%) !important}}
        .stTabs [data-baseweb="tab-list"] {{gap:.4rem;border-bottom:0;background:#EEF2F7;padding:.28rem;border-radius:13px;margin-bottom:.75rem}}
        .stTabs [data-baseweb="tab"] {{height:2.45rem;border-radius:10px;font-size:.82rem;padding:0 .9rem;color:#64748B}}
        .stTabs [aria-selected="true"] {{background:#FFFFFF;color:#1D4ED8;box-shadow:0 2px 8px rgba(15,23,42,.08)}}
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{color:#D7E3F2}}
        [data-testid="stSidebar"] .stCaptionContainer p {{color:#BDCCE0}}
        [data-testid="stSidebar"] .stButton > button:focus-visible {{outline:2px solid #67E8F9;outline-offset:2px}}
        .tc-page-export-row {{display:flex;justify-content:flex-end;gap:.5rem;margin:-.35rem 0 .8rem}}


        /* Release 7.9.0 — Premium UX consolidation */
        .block-container {{
            max-width: 1380px;
            padding-top: .45rem;
        }}
        .tc-page-header {{
            position: relative;
            overflow: hidden;
            margin: .15rem 0 .85rem;
            padding: 1rem 1.15rem 1rem 1.35rem;
            border: 1px solid #DCE6F3;
            border-radius: 16px;
            background: rgba(255,255,255,.94);
            box-shadow: 0 8px 24px rgba(15,23,42,.055);
        }}
        .tc-page-header-accent {{
            position: absolute;
            inset: 0 auto 0 0;
            width: 5px;
            background: linear-gradient(180deg,#1D4ED8 0%,#06B6D4 100%);
        }}
        .tc-page-header-main {{
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1rem;
        }}
        .tc-page-eyebrow {{
            color: #2563EB;
            font-size: .65rem;
            font-weight: 850;
            letter-spacing: .105em;
            text-transform: uppercase;
        }}
        .tc-page-header h1 {{
            margin: .18rem 0 .2rem;
            color: #0F172A;
            font-size: clamp(1.45rem,2.2vw,2rem);
            line-height: 1.08;
            letter-spacing: -.038em;
        }}
        .tc-page-header p {{
            max-width: 860px;
            margin: 0;
            color: #52647D;
            font-size: .87rem;
            line-height: 1.45;
        }}
        .tc-page-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: .42rem;
            margin-top: .58rem;
        }}
        .tc-page-meta span,.tc-page-status {{
            display: inline-flex;
            align-items: center;
            min-height: 1.65rem;
            padding: .18rem .56rem;
            border: 1px solid #D8E4F2;
            border-radius: 999px;
            background: #F8FAFC;
            color: #475569;
            font-size: .68rem;
            font-weight: 760;
        }}
        .tc-page-status {{
            color: #075985;
            background: #ECFEFF;
            border-color: #A5F3FC;
            white-space: nowrap;
        }}
        .tc-recommended-action {{
            position: relative;
            margin: .7rem 0 .85rem;
            padding: .88rem 1rem .88rem 1.15rem;
            border: 1px solid #C7D2FE;
            border-radius: 14px;
            background: linear-gradient(135deg,#F8FAFF 0%,#EEF2FF 100%);
            box-shadow: 0 6px 18px rgba(49,46,129,.055);
        }}
        .tc-recommended-action:before {{
            content: "";
            position: absolute;
            left: 0;
            top: 12px;
            bottom: 12px;
            width: 4px;
            border-radius: 0 999px 999px 0;
            background: linear-gradient(180deg,#1D4ED8,#06B6D4);
        }}
        .tc-recommended-kicker {{
            color: #4338CA;
            font-size: .62rem;
            font-weight: 850;
            letter-spacing: .095em;
            text-transform: uppercase;
        }}
        .tc-recommended-title {{
            margin-top: .2rem;
            color: #0F172A;
            font-size: .98rem;
            font-weight: 840;
        }}
        .tc-recommended-body {{
            margin-top: .16rem;
            color: #52647D;
            font-size: .8rem;
            line-height: 1.42;
        }}
        .tc-empty-state {{
            display: flex;
            align-items: center;
            gap: .9rem;
            padding: 1rem;
            margin: .65rem 0;
            border: 1px dashed #C7D2E2;
            border-radius: 14px;
            background: #F8FAFC;
        }}
        .tc-empty-icon {{
            display: grid;
            place-items: center;
            width: 2.3rem;
            height: 2.3rem;
            flex: 0 0 2.3rem;
            border-radius: 12px;
            color: #1D4ED8;
            background: #E0EAFF;
            font-weight: 900;
        }}
        .tc-empty-title {{color:#0F172A;font-weight:820;font-size:.92rem}}
        .tc-empty-body {{color:#64748B;font-size:.78rem;line-height:1.4;margin-top:.12rem}}
        .tc-skeleton {{padding:1rem;border:1px solid #E2E8F0;border-radius:14px;background:#FFFFFF}}
        .tc-skeleton-line {{display:block;height:.72rem;margin:.55rem 0;border-radius:999px;background:linear-gradient(90deg,#E8EEF6 20%,#F8FAFC 50%,#E8EEF6 80%);background-size:220% 100%;animation:tcShimmer 1.45s infinite}}
        .tc-skeleton-line:nth-child(2) {{width:78%}}
        .tc-skeleton-line:nth-child(3) {{width:58%}}
        @keyframes tcShimmer {{0%{{background-position:100% 0}}100%{{background-position:-100% 0}}}}
        .tc-candidate-row {{
            display: grid;
            grid-template-columns: minmax(190px,1.6fr) repeat(4,minmax(90px,.65fr)) minmax(240px,1.7fr);
            gap: .7rem;
            align-items: center;
            min-height: 70px;
            padding: .72rem .86rem;
            margin: .38rem 0;
            border: 1px solid #E1E8F2;
            border-radius: 13px;
            background: rgba(255,255,255,.96);
            box-shadow: 0 2px 8px rgba(15,23,42,.035);
        }}
        .tc-candidate-row:hover {{border-color:#B9CBE4;box-shadow:0 7px 18px rgba(15,23,42,.065)}}
        .tc-candidate-name {{color:#0F172A;font-size:.9rem;font-weight:840}}
        .tc-candidate-rank {{color:#64748B;font-size:.65rem;font-weight:820;text-transform:uppercase;letter-spacing:.07em}}
        .tc-candidate-value {{color:#0F172A;font-size:.82rem;font-weight:820}}
        .tc-candidate-label {{color:#7A8AA1;font-size:.59rem;font-weight:820;text-transform:uppercase;letter-spacing:.065em}}
        .tc-candidate-insight {{color:#475569;font-size:.69rem;line-height:1.38}}
        .tc-candidate-insight strong {{color:#25364D}}
        .tc-toolbar {{
            padding: .68rem .78rem;
            margin: .45rem 0 .75rem;
            border: 1px solid #E2E8F0;
            border-radius: 14px;
            background: rgba(248,250,252,.86);
        }}
        div[data-testid="stMetric"] {{padding:.7rem .82rem}}
        div[data-testid="stMetricValue"] {{font-size:1.55rem}}
        .stDownloadButton > button,.stButton > button {{min-height:2.35rem;border-radius:10px;font-size:.82rem}}
        .stDownloadButton > button {{font-weight:720;border-color:#CBD5E1;color:#334155;background:#FFFFFF}}
        [data-testid="stSidebar"] {{width:286px !important}}
        [data-testid="stSidebar"] .stButton > button {{
            min-height:2.48rem;
            padding:.48rem .7rem;
            color:#F4F8FF;
            font-size:.86rem;
            font-weight:780;
        }}
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] label {{color:#D6E3F4}}
        .tc-mission-card {{padding:.72rem .78rem;margin:.45rem 0 .62rem}}
        .tc-sidebar-section {{margin:.82rem .3rem .3rem;color:#C5D4E8}}
        .tc-brand-lockup {{padding:.28rem .1rem .8rem}}
        .tc-brand-mark {{width:42px;height:42px;flex-basis:42px}}
        .tc-brand-name {{font-size:.94rem}}
        .tc-brand-slogan {{font-size:.64rem}}
        .stTabs [data-baseweb="tab-list"] {{position:sticky;top:6.15rem;z-index:30;background:rgba(238,242,247,.96);backdrop-filter:blur(10px)}}



        /* Release 7.9.2 — Unified light shell and accessible navigation */
        .stApp {{
            background:
                radial-gradient(circle at 0% 0%, rgba(37,99,235,.055), transparent 26rem),
                radial-gradient(circle at 100% 4%, rgba(6,182,212,.045), transparent 24rem),
                linear-gradient(180deg,#F8FAFD 0%,#F3F7FC 100%) !important;
        }}
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        section.main {{
            background: transparent !important;
        }}
        [data-testid="stHeader"] {{
            background: rgba(248,250,253,.92) !important;
            border-bottom: 1px solid rgba(220,230,243,.88);
            backdrop-filter: blur(14px);
        }}
        [data-testid="stSidebar"] {{
            width: 286px !important;
            background: linear-gradient(180deg,#F8FBFF 0%,#F3F7FC 100%) !important;
            border-right: 1px solid #DCE6F3 !important;
            box-shadow: 8px 0 28px rgba(15,23,42,.035) !important;
        }}
        [data-testid="stSidebar"] > div:first-child,
        [data-testid="stSidebarContent"] {{
            background: transparent !important;
        }}
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stCaptionContainer p {{
            color: #475569 !important;
            opacity: 1 !important;
        }}
        .tc-brand-lockup {{
            margin: 0 0 .28rem;
            padding: .42rem .45rem .82rem;
            border-bottom: 1px solid #DCE6F3;
            border-radius: 12px 12px 0 0;
        }}
        .tc-brand-lockup:hover {{background:#EEF4FB !important}}
        .tc-brand-name {{color:#0F172A !important}}
        .tc-brand-slogan {{color:#2563EB !important}}
        .tc-brand-version {{color:#64748B !important}}
        .tc-brand-mark svg {{filter:none !important}}
        .tc-mission-card {{
            margin: .48rem .15rem .68rem;
            padding: .74rem .78rem;
            border: 1px solid #CFE0F5 !important;
            background: linear-gradient(135deg,#FFFFFF 0%,#EEF5FF 100%) !important;
            box-shadow: 0 5px 16px rgba(37,99,235,.055) !important;
        }}
        .tc-mission-kicker,
        .tc-sidebar-section,
        .tc-sidebar-next-kicker {{color:#52647D !important}}
        .tc-mission-role {{color:#0F172A !important}}
        .tc-mission-meta {{color:#52647D !important}}
        .tc-sidebar-section {{
            margin: .9rem .55rem .28rem !important;
            font-size: .64rem;
            letter-spacing: .105em;
        }}
        [data-testid="stSidebar"] .stButton {{margin:.08rem .15rem !important}}
        [data-testid="stSidebar"] .stButton > button,
        [data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"],
        [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {{
            min-height: 2.42rem !important;
            justify-content: flex-start !important;
            text-align: left !important;
            padding: .5rem .72rem !important;
            color: #334155 !important;
            background: transparent !important;
            border: 1px solid transparent !important;
            border-radius: 9px !important;
            box-shadow: none !important;
            font-size: .86rem !important;
            font-weight: 720 !important;
            opacity: 1 !important;
        }}
        [data-testid="stSidebar"] .stButton > button p,
        [data-testid="stSidebar"] .stButton > button span,
        [data-testid="stSidebar"] button[data-testid^="stBaseButton"] p,
        [data-testid="stSidebar"] button[data-testid^="stBaseButton"] span {{
            color: inherit !important;
            opacity: 1 !important;
        }}
        [data-testid="stSidebar"] .stButton > button:hover,
        [data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:hover,
        [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover {{
            transform: none !important;
            color: #1E3A5F !important;
            background: #EEF4FB !important;
            border-color: #D8E4F2 !important;
        }}
        [data-testid="stSidebar"] .stButton > button[kind="primary"],
        [data-testid="stSidebar"] button[data-testid="stBaseButton-primary"],
        [data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {{
            color: #0F4CD8 !important;
            background: #E8F0FF !important;
            border: 1px solid #C7D7FE !important;
            box-shadow: inset 3px 0 0 #2563EB, 0 3px 10px rgba(37,99,235,.06) !important;
            font-weight: 800 !important;
        }}
        [data-testid="stSidebar"] .stButton > button[kind="primary"]:before,
        [data-testid="stSidebar"] button[data-testid="stBaseButton-primary"]:before,
        [data-testid="stSidebar"] [data-testid="stBaseButton-primary"]:before {{
            display:none !important;
            content:none !important;
        }}
        [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover,
        [data-testid="stSidebar"] button[data-testid="stBaseButton-primary"]:hover,
        [data-testid="stSidebar"] [data-testid="stBaseButton-primary"]:hover {{
            color:#0B3FB8 !important;
            background:#DBEAFE !important;
            border-color:#AFC7F5 !important;
        }}
        [data-testid="stSidebar"] .stButton > button:disabled,
        [data-testid="stSidebar"] button[data-testid^="stBaseButton"]:disabled {{
            color:#94A3B8 !important;
            background:#F1F5F9 !important;
            border-color:transparent !important;
            opacity:1 !important;
        }}
        [data-testid="stSidebar"] .stButton > button:focus-visible {{
            outline: 3px solid rgba(37,99,235,.22) !important;
            outline-offset: 1px !important;
        }}
        [data-testid="stSidebar"] details {{
            border: 1px solid transparent !important;
            background: transparent !important;
            box-shadow: none !important;
        }}
        [data-testid="stSidebar"] details:hover {{background:#EEF4FB !important}}
        [data-testid="stSidebar"] details summary {{color:#334155 !important}}
        [data-testid="stSidebar"] [data-baseweb="select"] > div {{
            color:#334155 !important;
            background:#FFFFFF !important;
            border-color:#CBD5E1 !important;
        }}
        .tc-sidebar-next {{
            margin: .92rem .15rem 0;
            background: linear-gradient(135deg,#FFFFFF 0%,#EEF5FF 100%) !important;
            border:1px solid #CFE0F5 !important;
            box-shadow:0 4px 14px rgba(37,99,235,.045);
        }}
        .tc-sidebar-next-title {{color:#0F172A !important}}
        .tc-nav-notice {{
            color:#075985 !important;
            background:#ECFEFF !important;
            border-color:#BAE6FD !important;
        }}
        .tc-hero {{
            color:#0F172A !important;
            background:
                radial-gradient(circle at 88% 14%,rgba(6,182,212,.12),transparent 15rem),
                linear-gradient(135deg,#FFFFFF 0%,#EEF4FF 58%,#F0FDFF 100%) !important;
            border-color:#D9E5F3 !important;
            box-shadow:0 12px 32px rgba(15,23,42,.06) !important;
        }}
        .tc-hero h1 {{color:#0F172A !important}}
        .tc-hero p {{color:#52647D !important;opacity:1 !important}}
        .tc-hero .tc-badge {{
            color:#1D4ED8 !important;
            background:#E8F0FF !important;
            border-color:#C7D7FE !important;
        }}
        .block-container {{
            padding-left: 1.55rem;
            padding-right: 1.55rem;
        }}

        @media (max-width: 760px) {{
            .block-container {{ padding-left: 1rem; padding-right: 1rem; }}
            .tc-hero {{ padding: 1.3rem 1.2rem; border-radius: 19px; }}
            .tc-card {{ padding: 1rem; }}
            .tc-page-header {{padding:.9rem 1rem .9rem 1.15rem}}
            .tc-page-header-main {{display:block}}
            .tc-page-status {{margin-top:.6rem}}
            .tc-candidate-row {{grid-template-columns:1fr 1fr;gap:.55rem}}
            .tc-candidate-row .tc-candidate-insight {{grid-column:1 / -1}}
            .stTabs [data-baseweb="tab-list"] {{position:relative;top:auto;overflow-x:auto}}
        }}


        /* Release 8.0.0 — Premium unified balanced experience */
        .stApp {{
            background:
                radial-gradient(circle at 91% 4%,rgba(21,184,207,.08),transparent 24rem),
                radial-gradient(circle at 18% 0%,rgba(52,87,229,.07),transparent 30rem),
                linear-gradient(180deg,#F5F7FC 0%,#EFF3FA 100%) !important;
        }}
        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(180deg,rgba(248,250,255,.76),rgba(241,245,251,.78)) !important;
        }}
        [data-testid="stHeader"] {{
            background: rgba(244,247,252,.88) !important;
            border-bottom: 1px solid rgba(203,215,232,.82) !important;
            backdrop-filter: blur(16px);
        }}
        .block-container {{
            max-width: 1390px;
            padding-top: .7rem;
            padding-left: 1.8rem;
            padding-right: 1.8rem;
        }}
        [data-testid="stSidebar"] {{
            width: 288px !important;
            background:
                radial-gradient(circle at 8% 0%,rgba(21,184,207,.18),transparent 18rem),
                linear-gradient(180deg,#102A56 0%,#153764 58%,#102B53 100%) !important;
            border-right: 1px solid #284B78 !important;
            box-shadow: 10px 0 32px rgba(23,43,76,.12) !important;
        }}
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stCaptionContainer p {{
            color:#C8D7EA !important;
        }}
        .tc-brand-lockup {{
            margin:0 0 .34rem;
            padding:.45rem .42rem .9rem;
            border-bottom:1px solid rgba(210,226,245,.16) !important;
            border-radius:13px 13px 0 0;
        }}
        .tc-brand-lockup:hover {{background:rgba(255,255,255,.055) !important}}
        .tc-brand-name {{color:#FFFFFF !important;font-size:.98rem !important}}
        .tc-brand-slogan {{color:#A9DDF4 !important}}
        .tc-brand-version {{color:#87A4C8 !important}}
        .tc-brand-mark svg {{filter:drop-shadow(0 5px 11px rgba(0,207,232,.16)) !important}}
        .tc-mission-card {{
            margin:.48rem .12rem .72rem;
            padding:.78rem .82rem;
            border:1px solid rgba(174,205,239,.20) !important;
            background:linear-gradient(135deg,rgba(255,255,255,.09),rgba(63,105,174,.15)) !important;
            box-shadow:0 10px 24px rgba(4,19,43,.13) !important;
        }}
        .tc-mission-kicker,.tc-sidebar-section,.tc-sidebar-next-kicker {{color:#AFC8E8 !important}}
        .tc-mission-role {{color:#FFFFFF !important}}
        .tc-mission-meta {{color:#C4D5E9 !important}}
        .tc-sidebar-section {{margin:.95rem .52rem .3rem !important}}
        [data-testid="stSidebar"] .stButton {{margin:.08rem .12rem !important}}
        [data-testid="stSidebar"] .stButton > button,
        [data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"],
        [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {{
            min-height:2.45rem !important;
            justify-content:flex-start !important;
            text-align:left !important;
            padding:.5rem .72rem !important;
            color:#E7F0FC !important;
            background:transparent !important;
            border:1px solid transparent !important;
            border-radius:10px !important;
            box-shadow:none !important;
            font-size:.86rem !important;
            font-weight:710 !important;
            opacity:1 !important;
        }}
        [data-testid="stSidebar"] .stButton > button p,
        [data-testid="stSidebar"] .stButton > button span,
        [data-testid="stSidebar"] button[data-testid^="stBaseButton"] p,
        [data-testid="stSidebar"] button[data-testid^="stBaseButton"] span {{
            color:inherit !important;
            opacity:1 !important;
        }}
        [data-testid="stSidebar"] .stButton > button:hover,
        [data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:hover,
        [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover {{
            transform:none !important;
            color:#FFFFFF !important;
            background:rgba(110,160,226,.16) !important;
            border-color:rgba(176,209,244,.19) !important;
        }}
        [data-testid="stSidebar"] .stButton > button[kind="primary"],
        [data-testid="stSidebar"] button[data-testid="stBaseButton-primary"],
        [data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {{
            color:#FFFFFF !important;
            background:linear-gradient(105deg,#2949B8 0%,#365FCB 74%,#267FAD 100%) !important;
            border:1px solid rgba(159,208,238,.32) !important;
            box-shadow:inset 3px 0 0 #63D4E7,0 8px 18px rgba(5,22,54,.17) !important;
            font-weight:790 !important;
        }}
        [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover,
        [data-testid="stSidebar"] button[data-testid="stBaseButton-primary"]:hover,
        [data-testid="stSidebar"] [data-testid="stBaseButton-primary"]:hover {{
            color:#FFFFFF !important;
            background:linear-gradient(105deg,#2441A6 0%,#3158BE 70%,#24789F 100%) !important;
            border-color:rgba(173,216,242,.42) !important;
        }}
        [data-testid="stSidebar"] .stButton > button:disabled,
        [data-testid="stSidebar"] button[data-testid^="stBaseButton"]:disabled {{
            color:#89A1C1 !important;
            background:rgba(255,255,255,.035) !important;
            border-color:transparent !important;
            opacity:1 !important;
        }}
        [data-testid="stSidebar"] details {{
            border:1px solid rgba(174,205,239,.08) !important;
            background:rgba(255,255,255,.025) !important;
        }}
        [data-testid="stSidebar"] details:hover {{background:rgba(255,255,255,.055) !important}}
        [data-testid="stSidebar"] details summary {{color:#E7F0FC !important}}
        [data-testid="stSidebar"] [data-baseweb="select"] > div {{
            color:#EAF2FC !important;
            background:rgba(255,255,255,.07) !important;
            border-color:rgba(188,211,239,.18) !important;
        }}
        .tc-sidebar-next {{
            margin:.95rem .12rem 0;
            padding:.82rem .85rem !important;
            background:linear-gradient(135deg,rgba(255,255,255,.09),rgba(96,114,205,.14)) !important;
            border:1px solid rgba(188,211,239,.18) !important;
            box-shadow:0 9px 22px rgba(5,22,54,.12) !important;
        }}
        .tc-sidebar-next-title {{color:#FFFFFF !important}}
        .tc-sidebar-next-copy {{color:#BFD0E5;font-size:.67rem;line-height:1.4;margin-top:.28rem}}
        .tc-nav-notice {{
            color:#D9F7FB !important;
            background:rgba(21,184,207,.12) !important;
            border-color:rgba(127,220,234,.22) !important;
        }}
        .tc-card,
        div[data-testid="stMetric"],
        div[data-testid="stExpander"],
        [data-testid="stVerticalBlockBorderWrapper"] {{
            background:#FCFDFE !important;
            border-color:#DCE4F0 !important;
            box-shadow:0 7px 22px rgba(37,54,82,.055) !important;
        }}
        .tc-page-header {{
            background:
                radial-gradient(circle at 92% 12%,rgba(21,184,207,.09),transparent 12rem),
                linear-gradient(135deg,#FCFDFE 0%,#F6F8FD 100%) !important;
            border-color:#D9E3F0 !important;
            box-shadow:0 8px 23px rgba(37,54,82,.055) !important;
        }}
        .tc-page-header-accent {{background:linear-gradient(180deg,#3457E5 0%,#15B8CF 100%) !important}}
        .tc-page-eyebrow {{color:#3457E5 !important}}
        .tc-page-header h1 {{color:#14213D !important}}
        .tc-page-header p {{color:#5B6B82 !important}}
        .tc-page-meta span {{background:#F4F7FC !important;border-color:#D8E2EF !important;color:#53647C !important}}
        .tc-page-status {{background:#EAF9FC !important;border-color:#BDEAF1 !important;color:#16677B !important}}
        .tc-hero {{
            color:#FFFFFF !important;
            background:
                radial-gradient(circle at 88% 10%,rgba(91,222,238,.19),transparent 14rem),
                linear-gradient(135deg,#24437E 0%,#4658C2 64%,#5465D3 100%) !important;
            border-color:rgba(255,255,255,.14) !important;
            box-shadow:0 16px 38px rgba(37,63,120,.16) !important;
        }}
        .tc-hero h1 {{color:#FFFFFF !important}}
        .tc-hero p {{color:#E8EEFF !important;opacity:1 !important}}
        .tc-hero .tc-badge {{color:#F2FAFF !important;background:rgba(255,255,255,.12) !important;border-color:rgba(255,255,255,.18) !important}}
        .tc-insight,.tc-recommended-action {{
            background:linear-gradient(135deg,#FCFDFE 0%,#F5F3FF 100%) !important;
            border-color:#DDDDF4 !important;
        }}
        .stButton > button[kind="primary"],
        button[data-testid="stBaseButton-primary"],
        [data-testid="stBaseButton-primary"] {{
            background:linear-gradient(135deg,#3457E5 0%,#5368E7 72%,#318CAA 100%) !important;
            color:#FFFFFF !important;
            border:0 !important;
            box-shadow:0 8px 20px rgba(52,87,229,.20) !important;
        }}
        .stButton > button[kind="primary"]:hover,
        button[data-testid="stBaseButton-primary"]:hover,
        [data-testid="stBaseButton-primary"]:hover {{
            background:linear-gradient(135deg,#2948C6 0%,#465CCF 72%,#287E99 100%) !important;
        }}
        .stDownloadButton > button {{
            color:#31445F !important;
            background:#FCFDFE !important;
            border-color:#C8D5E6 !important;
        }}
        .stTabs [data-baseweb="tab-list"] {{background:#E9EEF7 !important}}
        .stTabs [data-baseweb="tab"] {{color:#5B6B82 !important}}
        .stTabs [aria-selected="true"] {{color:#314FC9 !important;background:#FCFDFE !important}}

        @media (max-width:760px) {{
            .block-container {{padding-left:1rem;padding-right:1rem}}
            [data-testid="stSidebar"] {{width:284px !important}}
        }}
        </style>
        ''',
        unsafe_allow_html=True,
    )
