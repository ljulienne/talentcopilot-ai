
from typing import Any


def render_governance_card(governance_report: Any) -> None:
    try:
        import streamlit as st
    except ImportError:
        return

    st.subheader("AI Governance")

    if governance_report is None:
        st.info("No governance report available yet.")
        return

    card = getattr(governance_report, "decision_card", None)

    if card:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Decision", getattr(card, "decision", "-"))
        col2.metric("Confidence", f"{getattr(card, 'confidence_score', 0):.0f}%")
        col3.metric("Evidence Quality", f"{getattr(card, 'evidence_quality_score', 0):.0f}%")
        col4.metric("Risk", getattr(card, "risk_level", "-"))

        st.info(getattr(card, "executive_summary", ""))
    else:
        st.write("Governance report available, but no decision card found.")

    notes = getattr(governance_report, "explainability_notes", [])
    if notes:
        with st.expander("Explainability notes"):
            for note in notes:
                st.write(f"- {note}")

    risk = getattr(governance_report, "risk", None)
    risks = getattr(risk, "risks", []) if risk else []
    if risks:
        with st.expander("Risks"):
            for item in risks:
                st.warning(getattr(item, "reason", str(item)))

    uncertainty = getattr(governance_report, "uncertainty", None)
    uncertainties = getattr(uncertainty, "uncertainties", []) if uncertainty else []
    if uncertainties:
        with st.expander("Uncertainty"):
            for item in uncertainties:
                st.write(f"- {getattr(item, 'reason', str(item))}")
