
import streamlit as st

def card(title, body="", badge=None):
    badge_html = f'<span class="tc-badge">{badge}</span>' if badge else ""
    st.markdown(f"""
    <div class="tc-card">
        {badge_html}
        <h3>{title}</h3>
        <p class="tc-muted">{body}</p>
    </div>
    """, unsafe_allow_html=True)

def metric_row(items):
    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        label, value, help_text = item
        col.metric(label, value, help=help_text)

def score_badge(score):
    if score >= 85:
        return "🟢 Excellent"
    if score >= 70:
        return "🟡 Strong"
    if score >= 50:
        return "🟠 Potential"
    return "🔴 Weak"
