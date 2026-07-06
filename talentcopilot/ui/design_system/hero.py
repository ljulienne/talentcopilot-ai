import streamlit as st


def render_hero(
    title: str,
    subtitle: str = "",
    icon: str = "🧠",
    badge: str | None = None,
) -> None:
    badge_html = ""
    if badge:
        badge_html = f'<div class="tc-badge">{badge}</div>'

    html = f"""
<style>
.tc-hero {{
    padding: 32px;
    border-radius: 20px;
    background: linear-gradient(135deg, #2563EB, #4F46E5);
    color: white;
    margin-bottom: 25px;
    box-shadow: 0 10px 30px rgba(0,0,0,.12);
}}

.tc-title {{
    font-size: 38px;
    font-weight: 700;
    margin-bottom: 8px;
}}

.tc-subtitle {{
    opacity: .9;
    font-size: 18px;
}}

.tc-badge {{
    display: inline-block;
    margin-top: 18px;
    padding: 8px 18px;
    border-radius: 999px;
    background: rgba(255,255,255,.18);
    backdrop-filter: blur(8px);
    font-weight: 600;
}}
</style>
<div class="tc-hero">
<div style="font-size:52px">{icon}</div>
<div class="tc-title">{title}</div>
<div class="tc-subtitle">{subtitle}</div>
{badge_html}
</div>
"""

    st.markdown(html, unsafe_allow_html=True)
