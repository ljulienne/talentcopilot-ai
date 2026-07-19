import streamlit as st
from .tokens import TOKENS

def apply_enterprise_v2_theme() -> None:
    t = TOKENS
    st.markdown(f'''
    <style>
    :root {{
      --tc2-brand:{t.brand_500}; --tc2-brand-dark:{t.brand_900};
      --tc2-surface:{t.surface}; --tc2-muted:{t.surface_muted};
      --tc2-border:{t.border}; --tc2-text:{t.text_primary};
      --tc2-text-2:{t.text_secondary}; --tc2-success:{t.success};
      --tc2-warning:{t.warning}; --tc2-risk:{t.risk}; --tc2-info:{t.info};
    }}
    .tc2-page{{max-width:1440px;margin:0 auto;padding-bottom:40px}}
    .tc2-hero{{padding:28px 30px;margin:4px 0 24px;border:1px solid rgba(43,108,176,.16);
      border-radius:18px;background:radial-gradient(circle at top right,rgba(43,108,176,.14),transparent 34%),
      linear-gradient(135deg,#fff 0%,#f7faff 100%);box-shadow:{t.shadow_md}}}
    .tc2-eyebrow{{color:var(--tc2-brand);font-size:.76rem;font-weight:750;letter-spacing:.09em;text-transform:uppercase}}
    .tc2-title{{color:var(--tc2-brand-dark);font-size:clamp(1.65rem,2vw,2.35rem);line-height:1.12;font-weight:780;margin:8px 0 0}}
    .tc2-subtitle{{color:var(--tc2-text-2);font-size:1rem;line-height:1.55;max-width:880px;margin:10px 0 0}}
    .tc2-meta{{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px}}
    .tc2-card{{height:100%;padding:18px 19px;border:1px solid var(--tc2-border);border-radius:12px;background:#fff;box-shadow:{t.shadow_sm}}}
    .tc2-label{{color:{t.text_muted};font-size:.76rem;font-weight:700;letter-spacing:.045em;text-transform:uppercase}}
    .tc2-value{{color:var(--tc2-text);font-size:1.72rem;line-height:1.15;font-weight:780;margin:8px 0 4px}}
    .tc2-caption{{color:var(--tc2-text-2);font-size:.86rem;line-height:1.45}}
    .tc2-section{{margin:28px 0 12px}}
    .tc2-section-title{{color:var(--tc2-brand-dark);font-size:1.12rem;font-weight:760}}
    .tc2-section-description{{color:var(--tc2-text-2);font-size:.9rem;margin-top:4px}}
    .tc2-badge{{display:inline-flex;padding:5px 9px;border-radius:999px;font-size:.76rem;font-weight:720}}
    .tc2-neutral{{color:var(--tc2-text-2);background:#eef2f7}}
    .tc2-success{{color:var(--tc2-success);background:#e8f6ef}}
    .tc2-warning{{color:var(--tc2-warning);background:#fff4d8}}
    .tc2-risk{{color:var(--tc2-risk);background:#fdecec}}
    .tc2-info{{color:var(--tc2-info);background:#eaf2fb}}
    .tc2-panel{{padding:20px;margin:10px 0;border-radius:12px;border:1px solid var(--tc2-border);background:#fff;box-shadow:{t.shadow_sm}}}
    .tc2-panel-title{{color:var(--tc2-brand-dark);font-weight:760;font-size:1rem;margin-bottom:8px}}
    .tc2-panel-body{{color:var(--tc2-text-2);line-height:1.58;font-size:.91rem}}
    .tc2-accent-info{{border-left:4px solid var(--tc2-info)}}
    .tc2-accent-success{{border-left:4px solid var(--tc2-success)}}
    .tc2-accent-warning{{border-left:4px solid var(--tc2-warning)}}
    .tc2-accent-risk{{border-left:4px solid var(--tc2-risk)}}
    .tc2-empty{{text-align:center;padding:38px 24px;border:1px dashed var(--tc2-border);border-radius:18px;background:var(--tc2-muted)}}
    @media(max-width:768px){{.tc2-hero{{padding:22px 20px}}.tc2-value{{font-size:1.45rem}}}}
    </style>
    ''', unsafe_allow_html=True)
