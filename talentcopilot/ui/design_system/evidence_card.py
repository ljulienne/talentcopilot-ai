import streamlit as st

from talentcopilot.i18n import tr


def _status_icon(status: str) -> str:
    status = (status or "").lower()

    if status == "supported":
        return "✅"
    if status == "partial":
        return "⚠️"
    return "❌"


def render_evidence_card(evidences, limit: int = 5):
    """
    Displays structured evidence supporting the candidate decision.
    Pure UI component.
    """

    st.subheader(f"📌 {tr('decision.evidence')}")

    if not evidences:
        st.info("No evidence available.")
        return

    for evidence in evidences[:limit]:
        icon = _status_icon(evidence.get("status", ""))

        st.markdown(
            f"""
<div style="
background:white;
border:1px solid #e5e7eb;
border-radius:12px;
padding:18px;
margin-bottom:12px;
">
<strong>{icon} {evidence.get("competency", "Unknown")}</strong><br>
<span style="color:#64748b;">
Score: {evidence.get("score", 0)}% · Confidence: {evidence.get("confidence", 0)}%
</span>
</div>
""",
            unsafe_allow_html=True,
        )

        for excerpt in evidence.get("excerpts", [])[:2]:
            st.caption(f"Evidence: {excerpt}")

        recommendation = evidence.get("recommendation", "")
        if recommendation:
            st.caption(f"Recommendation: {recommendation}")
