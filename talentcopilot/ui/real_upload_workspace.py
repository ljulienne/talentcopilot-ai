from talentcopilot.services.real_upload_ranking_service import RealUploadRankingService
from talentcopilot.services.upload_text_reader_service import UploadTextReaderService
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def _render_ranking(report):
    import streamlit as st

    output = report.ranking_output
    if not output:
        st.warning(report.status)
        return

    metric_grid([
        ("Status", report.status, "Upload Ranking"),
        ("Role", output.role_title, "RoleProfile"),
        ("Candidates", str(output.total_candidates), "Analyzed"),
        ("Top Candidate", output.ranked_candidates[0].candidate_name if output.ranked_candidates else "-", "Ranking"),
    ])

    rows = [
        {
            "Rank": item.rank,
            "Candidate": item.candidate_name,
            "Recommendation": item.recommendation,
            "Fit": item.fit_score,
            "Confidence": item.confidence_score,
            "Risk": item.risk_level,
            "Ranking Score": item.ranking_score,
        }
        for item in output.ranked_candidates
    ]
    st.dataframe(rows, use_container_width=True)

    if not output.ranked_candidates:
        return

    names = [item.candidate_name for item in output.ranked_candidates]
    selected = st.selectbox("Candidate detail", names)
    item = output.ranked_candidates[names.index(selected)]
    profile = item.matching_output.decision_output.profile

    insight_card(
        "Recommendation",
        item.rationale,
        item.recommendation,
    )

    tab_summary, tab_signals, tab_trace = st.tabs(["Summary", "Signals", "Decision Trace"])

    with tab_summary:
        section_title("Executive Summary")
        st.write(profile.metadata.get("executive_summary", "-"))

    with tab_signals:
        rows = [{"Signal": key, "Value": value} for key, value in profile.metadata.items()]
        st.dataframe(rows, use_container_width=True)

    with tab_trace:
        for index, step in enumerate(profile.decision_trace.steps, start=1):
            with st.expander(f"{index}. {step.engine} · {step.action}"):
                st.write(step.explanation)
                st.caption(f"Output: {step.output_ref}")


def render_real_upload_workspace():
    import streamlit as st

    apply_enterprise_theme()

    enterprise_hero(
        "Real Upload",
        "Upload a job description and candidate CV files, then rank candidates through Decision Core.",
        "Release 1.2 — Real Intelligence",
    )

    insight_card(
        "Upload workflow",
        "This workspace supports TXT, text PDF and DOCX. Scanned PDF OCR will be added in a later package.",
        "Real Documents",
    )

    reader = UploadTextReaderService()
    service = RealUploadRankingService()

    job_file = st.file_uploader("Upload job description", type=["txt", "pdf", "docx"])
    candidate_files = st.file_uploader("Upload candidate CVs", type=["txt", "pdf", "docx"], accept_multiple_files=True)

    col1, col2 = st.columns(2)
    run_upload = col1.button("Run ranking from uploads")
    run_demo = col2.button("Run upload demo")

    if run_demo:
        report = service.run_demo()
        _render_ranking(report)

    if run_upload:
        if not job_file:
            st.error("Please upload a job description.")
            return
        if not candidate_files:
            st.error("Please upload at least one candidate CV.")
            return

        job_doc = reader.read_uploaded_file(job_file)
        candidate_docs = [reader.read_uploaded_file(file) for file in candidate_files]
        report = service.run(job_doc, candidate_docs)
        _render_ranking(report)
