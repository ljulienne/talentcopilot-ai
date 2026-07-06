import streamlit as st

from talentcopilot.viewmodels.decision_workspace import DecisionWorkspaceViewModel


def render_decision_header(view_model: DecisionWorkspaceViewModel) -> None:
    st.markdown(f"# 👤 {view_model.candidate_name}")
    st.caption(view_model.role_title)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Decision Confidence", f"{view_model.decision_confidence}%")

    with col2:
        st.metric("Decision Readiness", f"{view_model.decision_readiness}%")

    with col3:
        st.info(view_model.recommendation)
