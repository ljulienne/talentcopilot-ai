from html import escape

import streamlit as st


def apply_next_style():
    st.markdown(
        """
        <style>
        .block-container {max-width: 1180px; padding-top: 1.4rem;}
        .tc-hero {padding: 2.1rem 2.25rem; border-radius: 24px; background: linear-gradient(135deg,#111827 0%,#1f2937 62%,#374151 100%); color:white; margin-bottom:1.4rem;}
        .tc-hero h1 {margin:0; font-size:2.35rem; letter-spacing:-.04em;}
        .tc-hero p {margin:.75rem 0 0; font-size:1.05rem; color:#e5e7eb; max-width:860px;}
        .tc-pill {display:inline-block; padding:.25rem .65rem; border-radius:999px; background:rgba(255,255,255,.12); color:#f9fafb; font-size:.78rem; margin-bottom:.65rem;}
        .tc-card,.tc-recommendation,.tc-diagnostic {border:1px solid #e5e7eb; background:#fff; box-shadow:0 8px 24px rgba(15,23,42,.05);}
        .tc-card {padding:1.18rem 1.28rem; border-radius:18px; margin-bottom:1rem; min-height:145px;}
        .tc-card h3,.tc-recommendation h3 {margin-top:0; margin-bottom:.48rem;}
        .tc-card p,.tc-recommendation p {color:#374151; margin-bottom:.45rem;}
        .tc-muted {color:#6b7280; font-size:.92rem;}
        .tc-recommendation {padding:1.35rem; border-radius:20px; margin-bottom:1rem;}
        .tc-diagnostic {padding:1rem 1.1rem; border-radius:16px; margin-bottom:.8rem;}
        .tc-diagnostic strong {display:block; margin-bottom:.25rem;}
        .tc-signal {padding:.9rem 1rem; border-radius:14px; background:#f9fafb; border:1px solid #e5e7eb; margin-bottom:.65rem;}
        .tc-signal small {display:block; color:#6b7280; margin-top:.2rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, tag: str = "TalentCopilot Next"):
    st.markdown(f'<div class="tc-hero"><div class="tc-pill">{escape(tag)}</div><h1>{escape(title)}</h1><p>{escape(subtitle)}</p></div>', unsafe_allow_html=True)


def insight_card(title: str, body: str, footer: str | None = None):
    footer_html = f'<div class="tc-muted">{escape(footer)}</div>' if footer else ""
    st.markdown(f'<div class="tc-card"><h3>{escape(title)}</h3><p>{escape(body)}</p>{footer_html}</div>', unsafe_allow_html=True)


def recommendation_block(title: str, body: str):
    st.markdown(f'<div class="tc-recommendation"><h3>{escape(title)}</h3><p>{escape(body)}</p></div>', unsafe_allow_html=True)


def diagnostic_card(title: str, question: str, status: str):
    st.markdown(f'<div class="tc-diagnostic"><strong>{escape(title)}</strong><div>{escape(question)}</div><div class="tc-muted">{escape(status)}</div></div>', unsafe_allow_html=True)


def signal_row(title: str, detail: str, evidence: str):
    st.markdown(f'<div class="tc-signal"><strong>{escape(title)}</strong><div>{escape(detail)}</div><small>{escape(evidence)}</small></div>', unsafe_allow_html=True)
