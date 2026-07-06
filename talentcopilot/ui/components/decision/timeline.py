import streamlit as st

from talentcopilot.viewmodels.decision_workspace import DecisionWorkspaceViewModel


def render_decision_timeline(view_model: DecisionWorkspaceViewModel) -> None:
    st.subheader("Decision Framework")

    for step in view_model.timeline:
        icon = "✅" if step.status == "completed" else "⚠️"
        with st.expander(f"{icon} {step.name}", expanded=False):
            st.write(step.description)
