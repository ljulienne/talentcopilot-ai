import streamlit as st


def horizontal_timeline(steps) -> None:
    html_steps = ""

    for step in steps:
        icon = "✅" if step.status == "completed" else "⚠️"
        html_steps += f"""
        <div style="
            flex: 1;
            background: white;
            border-radius: 16px;
            padding: 16px;
            min-width: 130px;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.07);
            border: 1px solid #E5E7EB;
        ">
            <div style="font-size: 24px;">{icon}</div>
            <div style="font-weight: 800; color: #0F172A; margin-top: 8px;">
                {step.name}
            </div>
            <div style="font-size: 12px; color: #64748B; margin-top: 6px; line-height: 1.4;">
                {step.description}
            </div>
        </div>
        """

    st.markdown(
        f"""
        <div style="
            display: flex;
            gap: 14px;
            overflow-x: auto;
            padding-bottom: 8px;
            margin-bottom: 20px;
        ">
            {html_steps}
        </div>
        """,
        unsafe_allow_html=True,
    )
