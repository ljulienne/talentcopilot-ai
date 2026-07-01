
import streamlit as st
from talentcopilot.engines.recruitment_pipeline import analyze_recruitment_batch
from talentcopilot.ui.widgets import metric_row, score_badge

MAX_CV_UPLOADS = 50

def render_dashboard():
    st.title("📊 Recruitment Dashboard")
    st.caption("Upload a job description and candidate CVs to start the analysis.")

    job_file = st.file_uploader("Upload job description PDF", type=["pdf"])

    cv_files = st.file_uploader(
        f"Upload candidate CV PDFs — max {MAX_CV_UPLOADS}",
        type=["pdf"],
        accept_multiple_files=True
    )

    analyze = st.button("🚀 Analyze candidates", use_container_width=True)

    if analyze:
        if not job_file:
            st.warning("Please upload a job description PDF.")
            st.stop()

        if not cv_files:
            st.warning("Please upload at least one candidate CV PDF.")
            st.stop()

        if len(cv_files) > MAX_CV_UPLOADS:
            st.error(f"You can upload a maximum of {MAX_CV_UPLOADS} CVs at once.")
            st.stop()

        with st.spinner("Running TalentCopilot analysis..."):
            st.session_state.analysis_batch = analyze_recruitment_batch(job_file, cv_files)

    batch = st.session_state.get("analysis_batch")

    if not batch:
        st.info("No analysis yet. Upload files above to begin.")
        return

    if not batch["success"]:
        st.error("The job description could not be processed.")
        return

    results = batch["results"]

    if not results:
        st.error("No candidate could be analyzed.")
        return

    scores = [item["match_result"].overall_score for item in results]
    avg_score = round(sum(scores) / len(scores))

    strong = sum(1 for item in results if item["match_result"].overall_score >= 85)
    interview = sum(1 for item in results if 70 <= item["match_result"].overall_score < 85)

    metric_row([
        ("CV analyzed", len(results), "Number of analyzed CVs"),
        ("Average score", f"{avg_score}%", "Average match score"),
        ("Strong shortlist", strong, "Candidates above 85%"),
        ("Interview", interview, "Candidates between 70% and 84%"),
    ])

    st.divider()
    st.subheader("🏆 Candidate Ranking")

    for index, item in enumerate(results, start=1):
        match = item["match_result"]
        candidate = item["candidate"]

        with st.container():
            col1, col2, col3, col4 = st.columns([1, 4, 2, 2])
            col1.subheader(f"#{index}")
            col2.write(f"**{candidate.name}**")
            col2.caption(item["file"])
            col3.metric("Match", f"{match.overall_score}%")
            col4.write(f"**{score_badge(match.overall_score)}**")
            st.write(match.executive_summary)
            st.divider()

    st.subheader("🔍 Candidate Detail")

    options = [f"#{i+1} - {item['candidate'].name}" for i, item in enumerate(results)]
    selected = st.selectbox("Select a candidate", options)
    selected_index = options.index(selected)

    item = results[selected_index]
    match = item["match_result"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Candidate", item["candidate"].name)
    col2.metric("Score", f"{match.overall_score}%")
    col3.metric("Confidence", f"{match.confidence_score}%")

    st.write(f"**Recommendation:** {match.recommendation}")
    st.write(match.executive_summary)

    with st.expander("Why this score?"):
        for detail in match.match_details:
            st.write(f"**{detail.requirement.name}** — {detail.score}%")
            st.caption(detail.explanation)
