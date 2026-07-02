
import streamlit as st
from talentcopilot.engines.recruitment_pipeline import analyze_recruitment_batch
from talentcopilot.ui.widgets import score_badge
from talentcopilot.ui.components import (
    section_title,
    metric_card,
    assistant_panel,
    candidate_card,
)

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

    section_title(
        "Recruitment Summary",
        "AI-powered overview of your candidate pool"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card("CV analyzed", len(results), "Candidate files processed")

    with col2:
        metric_card("Average Match", f"{avg_score}%", "Overall candidate pool")

    with col3:
        metric_card("Strong shortlist", strong, "Candidates above 85%", "#10B981")

    with col4:
        metric_card("Interview", interview, "Candidates between 70% and 84%", "#F59E0B")

    assistant_panel(
        "Recruiter Copilot",
        f"I analyzed {len(results)} candidates. The average match score is {avg_score}%. Start by reviewing the strongest profiles, then use Candidate Comparison to compare your shortlist."
    )

    st.divider()
    st.subheader("🏆 Candidate Ranking")

    for index, item in enumerate(results, start=1):
        match = item["match_result"]
        candidate = item["candidate"]

        with st.container():
            col1, col2, col3, col4 = st.columns([1, 4, 2, 2])
            col1.subheader(f"#{index}")
            with col2:
                candidate_card(candidate.name, match.overall_score, match.recommendation)
                st.caption(item["file"])
            col3.metric("Confidence", f"{match.confidence_score}%")
            col4.write(f"**{score_badge(match.overall_score)}**")
            st.write(match.executive_summary)
            st.divider()

    st.subheader("🔍 Candidate Detail")

    options = [f"#{i+1} - {item['candidate'].name}" for i, item in enumerate(results)]
    selected = st.selectbox("Select a candidate", options)
    selected_index = options.index(selected)

    item = results[selected_index]
    match = item["match_result"]

    section_title(
        "Candidate Insight",
        "Detailed recommendation, score and confidence for the selected candidate."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        metric_card("Candidate", item["candidate"].name, "Selected profile")

    with col2:
        metric_card("Score", f"{match.overall_score}%", "TalentCopilot match")

    with col3:
        metric_card("Confidence", f"{match.confidence_score}%", "AI confidence", "#10B981")

    assistant_panel(
        "Hiring Recommendation",
        f"{match.recommendation}. {match.executive_summary}"
    )

    with st.expander("Why this score?"):
        for detail in match.match_details:
            st.write(f"**{detail.requirement.name}** — {detail.score}%")
            st.caption(detail.explanation)
