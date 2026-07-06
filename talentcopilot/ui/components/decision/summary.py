import streamlit as st

from talentcopilot.viewmodels.decision_workspace import DecisionWorkspaceViewModel


def render_executive_summary(view_model: DecisionWorkspaceViewModel) -> None:
    st.subheader("Executive Summary")
    st.info(view_model.executive_summary)
