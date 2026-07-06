import html
import streamlit as st


def section_card(title: str, icon: str = "🧠", body: str = "") -> None:
    safe_body = body or ""

    st.markdown(
        f"""
<div class="tc-section-card">
  <div class="tc-section-title">{icon} {html.escape(title)}</div>
  <div class="tc-section-body">{safe_body}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def info_card(title: str, body: str, icon: str = "ℹ️", color: str = "#2563EB") -> None:
    st.markdown(
        f"""
<div class="tc-info-card" style="border-left-color:{color};">
  <div class="tc-info-title">{icon} {html.escape(title)}</div>
  <div class="tc-info-body">{body}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def inject_card_styles() -> None:
    st.markdown(
        """
<style>
.tc-section-card {
    background: white;
    border-radius: 22px;
    padding: 28px;
    box-shadow: 0 10px 28px rgba(15, 23, 42, 0.08);
    border: 1px solid #E5E7EB;
    margin-bottom: 22px;
}

.tc-section-title {
    font-size: 21px;
    font-weight: 850;
    color: #0F172A;
    margin-bottom: 14px;
}

.tc-section-body {
    font-size: 15px;
    line-height: 1.75;
    color: #334155;
}

.tc-info-card {
    background: #F8FAFC;
    border-radius: 18px;
    padding: 18px;
    border-left: 5px solid #2563EB;
    margin-bottom: 14px;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
}

.tc-info-title {
    font-size: 15px;
    font-weight: 800;
    color: #0F172A;
}

.tc-info-body {
    font-size: 14px;
    color: #475569;
    margin-top: 8px;
    line-height: 1.6;
}
</style>
""",
        unsafe_allow_html=True,
    )
