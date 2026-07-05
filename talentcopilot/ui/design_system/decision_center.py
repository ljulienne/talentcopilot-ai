import streamlit as st

from talentcopilot.i18n import tr

from talentcopilot.ui.cards import render_decision_header
from talentcopilot.ui.design_system import (
    render_decision_drivers,
    render_evidence_card,
    render_interview_focus_card,
    render_risk_card,
)


def render_decision_center(item):
    """
    Candidate Decision Center v1.

    Assembles all decision-related components for one candidate.
    """

    match = item.get("match_result")
    decision = item.get("candidate_decision")
    evidence = item.get("evidence", [])
    intelligence = item.get("candidate_intelligence", {}) or {}

    st.markdown(f"## 🧠 {tr('decision.center')}")

    render_decision_header(
        candidate_decision=decision,
        match_result=match,
        rank=item.get("rank"),
    )

    st.divider()

    render_decision_drivers(getattr(match, "match_details", []))

    st.divider()

    render_evidence_card(evidence)

    st.divider()

    if decision:
        render_risk_card(decision.risks)
        st.divider()
        render_interview_focus_card(decision.interview_plan)
    else:
        render_risk_card(intelligence.get("risk_factors", []))
