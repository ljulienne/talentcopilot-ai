import streamlit as st

from talentcopilot.viewmodels.decision_workspace import DecisionWorkspaceViewModel


def render_decision_metrics(view_model: DecisionWorkspaceViewModel) -> None:
    st.subheader("Decision Metrics")

    cols = st.columns(2)

    for index, metric in enumerate(view_model.metrics):
        with cols[index % 2]:
            st.metric(metric.label, metric.value)
            st.caption(metric.explanation)
