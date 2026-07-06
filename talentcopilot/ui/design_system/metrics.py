import streamlit as st


def metric_card(
    title: str,
    value: str,
    icon: str = "📊",
    subtitle: str = "",
    color: str = "#2563EB",
) -> None:
    st.markdown(
        f"""
        <div style="
            background: white;
            border-radius: 18px;
            padding: 22px;
            border-left: 6px solid {color};
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
            min-height: 155px;
        ">
            <div style="font-size: 30px;">{icon}</div>
            <div style="font-size: 13px; color: #64748B; margin-top: 8px;">
                {title}
            </div>
            <div style="font-size: 34px; font-weight: 800; margin-top: 6px; color: {color};">
                {value}
            </div>
            <div style="font-size: 13px; color: #94A3B8; margin-top: 8px;">
                {subtitle}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
