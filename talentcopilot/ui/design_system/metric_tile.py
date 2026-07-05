import streamlit as st


def render_metric_tile(
    title: str,
    value,
    subtitle: str = "",
    help_text: str = "",
    variant: str = "default",
):
    """
    Reusable Enterprise metric tile for TalentCopilot.

    Parameters:
    - title: metric label
    - value: main displayed value
    - subtitle: small supporting text
    - help_text: optional tooltip-like explanation
    - variant: default, success, warning, danger, info
    """

    colors = {
        "default": "#0f172a",
        "success": "#16a34a",
        "warning": "#d97706",
        "danger": "#dc2626",
        "info": "#2563eb",
    }

    color = colors.get(variant, colors["default"])

    help_block = ""
    if help_text:
        help_block = f'<div style="font-size:12px;color:#64748b;margin-top:6px;">{help_text}</div>'

    st.markdown(
        f"""
<div style="
    background:white;
    border:1px solid #e2e8f0;
    border-radius:16px;
    padding:18px;
    box-shadow:0 4px 12px rgba(15,23,42,0.06);
    min-height:120px;
">
    <div style="font-size:13px;color:#64748b;font-weight:600;">
        {title}
    </div>

    <div style="font-size:32px;font-weight:800;color:{color};margin-top:8px;">
        {value}
    </div>

    <div style="font-size:13px;color:#64748b;margin-top:4px;">
        {subtitle}
    </div>

    {help_block}
</div>
""",
        unsafe_allow_html=True,
    )
