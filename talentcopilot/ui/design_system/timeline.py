import html
import streamlit as st


def horizontal_timeline(steps) -> None:
    items = []

    for index, step in enumerate(steps, start=1):
        icon = "✓" if step.status == "completed" else "!"
        color = "#16A34A" if step.status == "completed" else "#F59E0B"

        items.append(
            f'<div class="tc-timeline-step">'
            f'<div class="tc-timeline-number" style="background:{color};">{icon}</div>'
            f'<div class="tc-timeline-index">Step {index}</div>'
            f'<div class="tc-timeline-title">{html.escape(step.name)}</div>'
            f'<div class="tc-timeline-desc">{html.escape(step.description)}</div>'
            f'</div>'
        )

    html_content = f"""
<style>
.tc-timeline {{
    display: flex;
    gap: 14px;
    overflow-x: auto;
    padding: 8px 4px 20px 4px;
    margin-bottom: 20px;
}}

.tc-timeline-step {{
    min-width: 185px;
    background: white;
    border-radius: 18px;
    padding: 18px;
    border: 1px solid #E5E7EB;
    box-shadow: 0 8px 22px rgba(15, 23, 42, 0.07);
}}

.tc-timeline-number {{
    width: 32px;
    height: 32px;
    border-radius: 999px;
    color: white;
    font-weight: 900;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 14px;
}}

.tc-timeline-index {{
    font-size: 11px;
    font-weight: 700;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: .06em;
}}

.tc-timeline-title {{
    font-size: 15px;
    font-weight: 850;
    color: #0F172A;
    margin-top: 4px;
}}

.tc-timeline-desc {{
    font-size: 12px;
    color: #64748B;
    line-height: 1.5;
    margin-top: 8px;
}}
</style>
<div class="tc-timeline">{''.join(items)}</div>
"""

    st.markdown(html_content, unsafe_allow_html=True)
