from typing import Any


def render_governance_card(governance_report: Any) -> None:
    """
    Streamlit rendering helper for the AI Governance / Explainable AI card.

    Usage:
        from talentcopilot.ui.governance_cards import render_governance_card
        render_governance_card(governance_report)
    """
    try:
        import streamlit as st
    except ImportError:
        return

    card = governance_report.decision_card

    st.subheader("AI Governance & Explainability")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Decision", card.decision)
    col2.metric("Confidence", f"{card.confidence_score:.0f}%")
    col3.metric("Evidence Quality", f"{card.evidence_quality_score:.0f}%")
    col4.metric("Risk", card.risk_level)

    st.info(card.executive_summary)

    with st.expander("Why this decision?"):
        for note in governance_report.explainability_notes:
            st.write(f"- {note}")

    if card.strengths:
        with st.expander("Strengths"):
            for item in card.strengths:
                st.success(item)

    if card.risks:
        with st.expander("Risks"):
            for item in card.risks:
                st.warning(item)

    if card.missing_information:
        with st.expander("Missing Information"):
            for item in card.missing_information:
                st.write(f"- {item}")

    if card.interview_focus:
        with st.expander("Interview Focus"):
            for item in card.interview_focus:
                st.write(f"- {item}")
