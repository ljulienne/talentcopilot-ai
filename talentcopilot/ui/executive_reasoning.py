from __future__ import annotations

import streamlit as st

from talentcopilot.executive_reasoning import ExecutiveAnswer


def render_executive_answer(answer: ExecutiveAnswer) -> None:
    st.markdown("---")
    st.markdown("### Executive reasoning")
    st.write(answer.summary)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Priority", answer.priority.value)
    c2.metric("Confidence", f"{answer.confidence_percent}%")
    c3.metric("Engine coverage", f"{answer.coverage_percent}%")
    c4.metric("Evidence quality", answer.evidence_quality)

    if answer.actions:
        st.markdown("#### Recommended decisions")
        for index, action in enumerate(answer.actions, start=1):
            st.write(f"{index}. {action}")

    with st.expander("Why TalentCopilot reached this conclusion"):
        for step in answer.decision_trace:
            st.markdown(f"**{step.order}. {step.source_engine}**")
            st.write(step.contribution)
            if step.evidence_ids:
                st.caption(f"Evidence references: {', '.join(step.evidence_ids)}")

    if answer.missing_data:
        st.caption("Additional coverage available from: " + ", ".join(answer.missing_data))
