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

    rows = [
        {
            "Rank": item.rank,
            "Candidate": item.candidate_name,
            "Decision Fit": item.fit_score,
            "Semantic": item.semantic_score,
            "Career": item.career_score,
            "Hybrid": item.hybrid_score,
            "Ranking Score": item.ranking_score,
            "Recommendation": item.recommendation,
            "Risk": item.risk_level,
        }
        for item in output.ranked_candidates
    ]
    st.dataframe(rows, use_container_width=True)

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
    hybrid = match.hybrid_report

    tab_candidate, tab_role, tab_decision, tab_hybrid, tab_explain, tab_trace = st.tabs([
        "Candidate Facts",
        "Role Facts",
        "Decision",
        "Hybrid",
        "Explainability",
        "Trace",
    ])

    with tab_candidate:
        section_title("LLM Candidate Extraction")
        st.json(match.candidate_extraction.model_dump())

    with tab_role:
        section_title("LLM Role Extraction")
        st.json(match.role_extraction.model_dump())

    with tab_decision:
        section_title("Decision Signals")
        st.json(profile.metadata)

    with tab_hybrid:
        section_title("Hybrid Matching")
        if hybrid:
            st.json({
                "semantic_score": hybrid.semantic_score,
                "career_score": hybrid.career_score,
                "hybrid_score": hybrid.hybrid_score,
                "summary": hybrid.summary,
                "missing_skills": hybrid.semantic_skill_report.missing_skills,
            })
        else:
            st.info("No hybrid report available.")

    with tab_explain:
        section_title("Explainable Hybrid Matching")
        if hybrid and hybrid.explanation_report:
            st.write(hybrid.explanation_report.recruiter_summary)
            st.json(hybrid.explanation_report.breakdown.__dict__)
            st.dataframe(
                [
                    {
                        "Category": c.category,
                        "Label": c.label,
                        "Points": c.points,
                        "Evidence": " | ".join(c.evidence),
                    }
                    for c in hybrid.explanation_report.positive_contributions
                ],
                use_container_width=True,
            )
            st.dataframe(
                [
                    {
                        "Category": c.category,
                        "Label": c.label,
                        "Points": c.points,
                        "Evidence": " | ".join(c.evidence),
                    }
                    for c in hybrid.explanation_report.penalties
                ],
                use_container_width=True,
            )
        else:
            st.info("No explainability report available.")

    with tab_trace:
        section_title("Decision Trace")
        for index, step in enumerate(profile.decision_trace.steps, start=1):
            with st.expander(f"{index}. {step.engine} · {step.action}"):
                st.write(step.explanation)
                st.caption(f"Output: {step.output_ref}")


def render_llm_real_upload():
    import streamlit as st

    apply_enterprise_theme()

    enterprise_hero(
        "LLM Real Upload",
        "Upload real CVs and job descriptions, then analyze them with LLM extraction, Decision Core and Hybrid Matching.",
        "Release 2.0",
    )

    insight_card(
        "Hybrid integration",
        "This workflow combines Decision Core with semantic skills, career intelligence and explainable hybrid scores.",
        "Hybrid Talent Intelligence",
    )

    reader = UploadTextReaderService()
    service = LLMRealUploadService()

    job_file = st.file_uploader("Upload job description", type=["txt", "pdf", "docx"])
    candidate_files = st.file_uploader("Upload candidate CVs", type=["txt", "pdf", "docx"], accept_multiple_files=True)

    col1, col2 = st.columns(2)
    run_upload = col1.button("Run hybrid LLM ranking from uploads")
    run_demo = col2.button("Run hybrid LLM upload demo")

    if run_demo:
        with st.spinner("Running hybrid LLM demo..."):
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

        with st.spinner("Running LLM extraction, Decision Core and Hybrid Matching..."):
            _render_report(service.run(job_doc, candidate_docs))
