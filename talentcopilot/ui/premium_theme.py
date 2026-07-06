import streamlit as st


def apply_premium_ui() -> None:
    st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #F8FAFC 0%, #EEF2FF 100%);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F172A 0%, #1E1B4B 100%);
}

[data-testid="stSidebar"] * {
    color: #F8FAFC !important;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 4rem;
    max-width: 1320px;
}

h1, h2, h3 {
    color: #0F172A;
    letter-spacing: -0.03em;
}

div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #E5E7EB;
    padding: 18px 20px;
    border-radius: 18px;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
}

div[data-testid="stMetric"] label {
    color: #64748B !important;
    font-weight: 700;
}

div[data-testid="stMetricValue"] {
    color: #2563EB;
    font-weight: 900;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 20px;
    border-color: #E5E7EB;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
    background: white;
}

.stButton button {
    border-radius: 999px;
    border: 1px solid #CBD5E1;
    padding: 0.55rem 1.1rem;
    font-weight: 700;
    background: white;
    color: #0F172A;
}

.stButton button:hover {
    border-color: #2563EB;
    color: #2563EB;
    background: #EFF6FF;
}

div[data-testid="stExpander"] {
    background: white;
    border-radius: 16px;
    border: 1px solid #E5E7EB;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
}

div[data-testid="stAlert"] {
    border-radius: 16px;
}

hr {
    margin: 2rem 0;
}

.tc-page-shell {
    background: white;
    border-radius: 26px;
    padding: 28px;
    border: 1px solid #E5E7EB;
    box-shadow: 0 12px 32px rgba(15, 23, 42, 0.07);
    margin-bottom: 24px;
}

.tc-brand {
    font-size: 1.15rem;
    font-weight: 900;
    letter-spacing: -0.04em;
}

.tc-brand-subtitle {
    font-size: 0.8rem;
    opacity: 0.78;
}
</style>
""", unsafe_allow_html=True)


def premium_sidebar_brand(version: str = "") -> None:
    st.sidebar.markdown(
        f"""
<div class="tc-brand">🧠 TalentCopilot AI</div>
<div class="tc-brand-subtitle">Decision Intelligence Platform · {version}</div>
""",
        unsafe_allow_html=True,
    )
