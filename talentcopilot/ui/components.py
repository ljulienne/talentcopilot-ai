
import streamlit as st

def section_title(title, subtitle=""):
    st.markdown(f"""
    <div style="margin-bottom:20px;">
        <h2 style="margin-bottom:0;">{title}</h2>
        <p style="color:#64748B;margin-top:4px;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def metric_card(title, value, subtitle="", color="#4F46E5"):
    st.markdown(f"""
    <div style="
        background:white;
        border-radius:18px;
        padding:20px;
        border-left:6px solid {color};
        box-shadow:0 4px 12px rgba(0,0,0,.08);
        margin-bottom:15px;
    ">
        <div style="font-size:14px;color:#64748B;">{title}</div>
        <div style="font-size:34px;font-weight:700;margin-top:6px;color:#0F172A;">{value}</div>
        <div style="color:#64748B;">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def assistant_panel(title, message):
    st.markdown(f"""
    <div style="
        background:#EEF2FF;
        border-radius:18px;
        padding:18px;
        border:1px solid #C7D2FE;
        margin-bottom:16px;
    ">
        <h4>🤖 {title}</h4>
        <p>{message}</p>
    </div>
    """, unsafe_allow_html=True)


def candidate_card(name, score, recommendation):
    color = "#10B981" if score >= 85 else "#F59E0B" if score >= 70 else "#EF4444"

    st.markdown(f"""
    <div style="
        background:white;
        border-radius:18px;
        padding:18px;
        border:1px solid #E2E8F0;
        margin-bottom:12px;
        box-shadow:0 4px 12px rgba(0,0,0,.05);
    ">
        <h4>{name}</h4>
        <div style="font-size:28px;font-weight:bold;color:{color};">{score}%</div>
        <div>{recommendation}</div>
    </div>
    """, unsafe_allow_html=True)


def card(title, body="", badge=None):
    badge_html = (
        f'<span style="background:#EEF2FF;color:#4338CA;'
        f'padding:4px 10px;border-radius:999px;'
        f'font-size:12px;font-weight:600;">{badge}</span>'
        if badge else ""
    )

    st.markdown(f"""
    <div style="
        background:white;
        border-radius:18px;
        padding:20px;
        border:1px solid #E2E8F0;
        box-shadow:0 4px 12px rgba(0,0,0,.05);
        margin-bottom:16px;
    ">
        {badge_html}
        <h3 style="margin-top:12px;">{title}</h3>
        <p style="color:#64748B;">{body}</p>
    </div>
    """, unsafe_allow_html=True)
