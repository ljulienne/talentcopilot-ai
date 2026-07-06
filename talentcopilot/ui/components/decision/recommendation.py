import streamlit as st

from talentcopilot.viewmodels.decision_workspace import DecisionWorkspaceViewModel


def render_recommendation_panel(view_model: DecisionWorkspaceViewModel) -> None:
    st.subheader("Recommendation")

    if view_model.reasoning_report:
        st.success(view_model.reasoning_report.recommendation)
        st.write(view_model.reasoning_report.recommendation_rationale)

    if view_model.recommendation_report:
        st.markdown("### Challenge")
        st.warning(view_model.recommendation_report.challenge)
