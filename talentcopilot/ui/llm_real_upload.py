from talentcopilot.services.llm_real_upload_service import LLMRealUploadService
from talentcopilot.services.upload_text_reader_service import UploadTextReaderService
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme

def _render_report(report):
    import streamlit as st
    output = report.ranking_output
    if not output:
        st.warning(report.status)
        return
    perf = output.performance_report
    metric_grid([
        ("Status", report.status, "LLM Upload"),
        ("Role", output.role_title, "Structured Role"),
        ("Candidates", str(output.total_candidates), "Analyzed"),
        ("Cache Hit Rate", f"{int(perf.cache_hit_rate * 100)}%", f"{perf.cache_hits}/{perf.calls}"),
    ])
    st.dataframe([{
        "Rank": item.rank, "Candidate": item.candidate_name, "Recommendation": item.recommendation,
        "Fit": item.fit_score, "Confidence": item.confidence_score, "Risk": item.risk_level,
        "Ranking Score": item.ranking_score,
    } for item in output.ranked_candidates], use_container_width=True)
    with st.expander("LLM performance details"):
        st.json({
            "calls": perf.calls,
            "cache_hits": perf.cache_hits,
            "cache_misses": perf.cache_misses,
            "cache_hit_rate": perf.cache_hit_rate,
            "total_duration_ms": perf.total_duration_ms,
            "metrics": [metric.__dict__ for metric in perf.metrics],
        })
    if not output.ranked_candidates:
        return
    names = [item.candidate_name for item in output.ranked_candidates]
    selected = st.selectbox("Candidate detail", names)
    item = output.ranked_candidates[names.index(selected)]
    match = item.matching_output
    profile = match.decision_output.profile
    tab_candidate, tab_role, tab_decision, tab_trace = st.tabs(["Candidate Facts", "Role Facts", "Decision", "Trace"])
    with tab_candidate:
        section_title("LLM Candidate Extraction")
        st.json(match.candidate_extraction.model_dump())
    with tab_role:
        section_title("LLM Role Extraction")
        st.json(match.role_extraction.model_dump())
    with tab_decision:
        section_title("Decision Signals")
        st.json(profile.metadata)
    with tab_trace:
        section_title("Decision Trace")
        for index, step in enumerate(profile.decision_trace.steps, start=1):
            with st.expander(f"{index}. {step.engine} · {step.action}"):
                st.write(step.explanation)
                st.caption(f"Output: {step.output_ref}")

def render_llm_real_upload():
    import streamlit as st
    apply_enterprise_theme()
    enterprise_hero("LLM Real Upload", "Upload real CVs and job descriptions, then analyze them through cached structured LLM extraction and Decision Core.", "Release 2.0")
    insight_card("Performance upgrade", "The job description is extracted once per batch. Candidate and role extractions are cached by document hash.", "Cached Structured Extraction")
    reader = UploadTextReaderService()
    service = LLMRealUploadService()
    job_file = st.file_uploader("Upload job description", type=["txt", "pdf", "docx"])
    candidate_files = st.file_uploader("Upload candidate CVs", type=["txt", "pdf", "docx"], accept_multiple_files=True)
    col1, col2 = st.columns(2)
    run_upload = col1.button("Run LLM ranking from uploads")
    run_demo = col2.button("Run LLM upload demo")
    if run_demo:
        with st.spinner("Running cached LLM demo..."):
            _render_report(service.run_demo())
    if run_upload:
        if not job_file:
            st.error("Please upload a job description.")
            return
        if not candidate_files:
            st.error("Please upload at least one candidate CV.")
            return
        with st.spinner("Reading uploaded documents..."):
            job_doc = reader.read_uploaded_file(job_file)
            candidate_docs = [reader.read_uploaded_file(file) for file in candidate_files]
        with st.spinner("Running cached LLM extraction and ranking..."):
            _render_report(service.run(job_doc, candidate_docs))
