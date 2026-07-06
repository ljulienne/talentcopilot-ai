import html
import streamlit as st


def evidence_card(
    text: str,
    interpretation: str = "",
    strength: str = "unknown",
    confidence_score: float | None = None,
) -> None:
    strength_label = strength.title()
    color_map = {
        "strong": "#16A34A",
        "moderate": "#2563EB",
        "weak": "#F59E0B",
        "unknown": "#64748B",
    }
    color = color_map.get(strength, "#64748B")

    confidence_html = ""
    if confidence_score is not None:
        confidence_html = f"""
        <div class="tc-evidence-confidence">
            Confidence: {int(confidence_score * 100)}%
        </div>
        """

    st.markdown(
        f"""
<style>
.tc-evidence-card {{
    background: white;
    border-radius: 18px;
    padding: 20px;
    border: 1px solid #E5E7EB;
    box-shadow: 0 8px 22px rgba(15, 23, 42, 0.07);
    margin-bottom: 14px;
}}

.tc-evidence-top {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 12px;
}}

.tc-evidence-badge {{
    display: inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    background: {color}1A;
    color: {color};
    font-size: 12px;
    font-weight: 800;
}}

.tc-evidence-text {{
    font-size: 15px;
    font-weight: 700;
    color: #0F172A;
    line-height: 1.55;
}}

.tc-evidence-interpretation {{
    margin-top: 12px;
    font-size: 13px;
    color: #475569;
    line-height: 1.6;
    background: #F8FAFC;
    border-radius: 12px;
    padding: 12px;
}}

.tc-evidence-confidence {{
    font-size: 12px;
    font-weight: 800;
    color: #64748B;
}}
</style>

<div class="tc-evidence-card">
    <div class="tc-evidence-top">
        <div class="tc-evidence-badge">{html.escape(strength_label)} evidence</div>
        {confidence_html}
    </div>
    <div class="tc-evidence-text">“{html.escape(text)}”</div>
    <div class="tc-evidence-interpretation">
        <strong>Interpretation:</strong> {html.escape(interpretation)}
    </div>
</div>
""",
        unsafe_allow_html=True,
    )
