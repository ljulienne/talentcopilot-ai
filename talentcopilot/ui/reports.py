
import streamlit as st

from talentcopilot.i18n import tr

from talentcopilot.services.ranking_service import rank_candidates

from talentcopilot.reports.pdf_report import generate_recruiter_report
from talentcopilot.ui.components import section_title, metric_card, assistant_panel, card
from talentcopilot.ui.design_system import render_page_header


def render_reports():
    render_page_header(
        title=tr("reports.title"),
        subtitle=tr("reports.subtitle"),
        description=tr("reports.description"),
        icon="📄",
    )

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

    scores = [item["match_result"].overall_score for item in results]
    avg_score = round(sum(scores) / len(scores)) if scores else 0
    top_candidate = results[0]["candidate"].name if results else "N/A"

    section_title(
        tr("reports.summary"),
        tr("reports.summary_subtitle")
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        metric_card("Candidates", len(results), "Analyzed profiles")

    with col2:
        metric_card("Average Match", f"{avg_score}%", "Candidate pool quality")

    with col3:
        metric_card("Top Candidate", top_candidate, "Highest ranked profile", "#10B981")

    if recruitment_context:
        card(
            "Recruitment Context",
            f"""
            Job: {recruitment_context.get("job_title", "")}

            Company: {recruitment_context.get("company", "")}

            Department: {recruitment_context.get("department", "")}

            Location: {recruitment_context.get("location", "")}

            Language: {recruitment_context.get("language", "")}
            """,
            "Context"
        )

    assistant_panel(
        "Recruiter Copilot",
        "This PDF can be shared with HR stakeholders or hiring managers to support the shortlist decision."
    )

    pdf_buffer = generate_recruiter_report(batch, recruitment_context)

    st.download_button(
        label=tr("reports.download_pdf"),
        data=pdf_buffer,
        file_name="talentcopilot_recruiter_report.pdf",
        mime="application/pdf",
        use_container_width=True
    )
