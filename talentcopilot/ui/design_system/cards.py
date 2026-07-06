import streamlit as st


def section_card(title: str, icon: str = "🧠", body: str = "") -> None:
    st.markdown(
        f"""
        <div style="
            background: white;
            border-radius: 20px;
            padding: 26px;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
            border: 1px solid #E5E7EB;
            margin-bottom: 18px;
        ">
            <div style="font-size: 22px; font-weight: 800; color: #0F172A; margin-bottom: 12px;">
                {icon} {title}
            </div>
            <div style="font-size: 15px; line-height: 1.7; color: #334155;">
                {body}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def info_card(title: str, body: str, icon: str = "ℹ️", color: str = "#2563EB") -> None:
    st.markdown(
        f"""
        <div style="
            background: #F8FAFC;
            border-radius: 16px;
            padding: 18px;
            border-left: 5px solid {color};
            margin-bottom: 12px;
        ">
            <div style="font-size: 16px; font-weight: 800; color: #0F172A;">
                {icon} {title}
            </div>
            <div style="font-size: 14px; color: #475569; margin-top: 8px; line-height: 1.6;">
                {body}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
