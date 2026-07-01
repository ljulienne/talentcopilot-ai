
import streamlit as st
from talentcopilot.reports.pdf_report import generate_recruiter_report


def render_reports():
    st.title("📄 Recruiter Reports")
    st.caption("Generate a professional PDF report from the current recruitment analysis.")

    batch = st.session_state.get("analysis_batch")
    recruitment_context = st.session_state.get("recruitment_context")

    if not batch:
        st.info("Run an analysis first from the Dashboard.")
        return

    if not batch.get("success"):
        st.warning("The current analysis is not valid.")
        return

    results = batch.get("results", [])

    if not results:
        st.warning("No candidates available for report generation.")
        return

    st.write(f"Candidates analyzed: **{len(results)}**")

    pdf_buffer = generate_recruiter_report(batch, recruitment_context)

    st.download_button(
        label="📄 Download Recruiter Report PDF",
        data=pdf_buffer,
        file_name="talentcopilot_recruiter_report.pdf",
        mime="application/pdf",
        use_container_width=True
    )
