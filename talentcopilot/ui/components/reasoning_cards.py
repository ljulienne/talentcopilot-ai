import streamlit as st

from talentcopilot.ai.reasoning_engine import CandidateReasoningReport


def render_reasoning_report(report: CandidateReasoningReport) -> None:
    st.subheader("AI Excellence Analysis")

    st.info(report.executive_summary)

    st.markdown("### Recommendation")
    st.success(report.recommendation)
    st.write(report.recommendation_rationale)

    st.markdown("### Strengths")
    for item in report.strengths:
        with st.expander(item.title, expanded=True):
            st.write(item.explanation)
            if item.evidence:
                st.markdown("**Evidence**")
                for evidence in item.evidence:
                    st.write(f"- {evidence}")
            st.caption(f"Confidence: {item.confidence}")

    st.markdown("### Risks")
    for item in report.risks:
        with st.expander(item.title, expanded=False):
            st.write(item.explanation)
            if item.evidence:
                st.markdown("**Evidence / missing elements**")
                for evidence in item.evidence:
                    st.write(f"- {evidence}")
            st.caption(f"Confidence: {item.confidence}")

    st.markdown("### Transferable Skills")
    for item in report.transferable_skills:
        with st.expander(item.title, expanded=False):
            st.write(item.explanation)
            if item.evidence:
                for evidence in item.evidence:
                    st.write(f"- {evidence}")
            st.caption(f"Confidence: {item.confidence}")

    st.markdown("### Uncertainties")
    for item in report.uncertainties:
        with st.expander(item.title, expanded=False):
            st.write(item.explanation)
            st.caption(f"Confidence: {item.confidence}")

    st.markdown("### Challenge the Recommendation")
    st.warning(report.challenge)
