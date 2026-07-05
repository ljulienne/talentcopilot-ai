import streamlit as st

from talentcopilot.i18n import tr


def render_risk_card(risks, title: str | None = None):
    """
    Displays candidate hiring risks.
    Pure UI component.
    """

    st.subheader(title or f"⚠️ {tr('decision.risks')}")

    if not risks:
        st.success("No major hiring risk detected.")
        return

    for risk in risks[:5]:
        st.markdown(
            f"""
<div style="
background:#fff7ed;
border:1px solid #fed7aa;
border-radius:12px;
padding:16px;
margin-bottom:10px;
">
<strong>⚠️ Risk to validate</strong>
<p style="margin-bottom:0;color:#7c2d12;">
{risk}
</p>
</div>
""",
            unsafe_allow_html=True,
        )
