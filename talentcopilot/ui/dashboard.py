import streamlit as st
from datetime import datetime

from talentcopilot.engines.recruitment_pipeline import analyze_recruitment_batch
from talentcopilot.storage.recruitment_store import save_recruitment
from talentcopilot.ui.widgets import score_badge
from talentcopilot.ui.components import (
    section_title,
    metric_card,
    assistant_panel,
    candidate_card,
)

MAX_CV_UPLOADS = 50


def _get_recruitment_title():
    context = st.session_state.get("recruitment_context")
    if not context:
        return "Recruitment Dashboard"
    return context.get("job_title") or "Recruitment Dashboard"


def _ensure_current_recruitment():
    context = st.session_state.get("recruitment_context")

    if "current_recruitment" not in st.session_state and context:
        now = datetime.now().isoformat()
        st.session_state.current_recruitment = {
            "title": context.get("job_title", "Untitled Recruitment"),
            "context": context,
            "language": context.get("language", "Auto Detect"),
            "job_description": None,
            "analysis_batch": st.session_state.get("analysis_batch"),
            "created_at": context.get("created_at", now),
            "updated_at": now,
            "status": "created",
        }


def _render_recruitment_context():
    context = st.session_state.get("recruitment_context")

    if not context:
        st.info("Tip: create a recruitment context first from **New Recruitment** for a richer report.")
        return

    st.markdown(f"""
    <div class="tc-hero">
        <h1>📊 {_get_recruitment_title()}</h1>
        <h3>{context.get("company", "")} · {context.get("department", "")}</h3>
        <p class="tc-muted">
        {context.get("location", "")} · {context.get("recruitment_type", "")} · Language: {context.get("language", "Auto Detect")}
        </p>
    </div>
    """, unsafe_allow_html=True)


def _save_current_recruitment(job_file_name=None, cv_file_names=None):
    _ensure_current_recruitment()

    current = st.session_state.get("current_recruitment")

    if not current:
        st.warning("Create a recruitment context first before saving.")
        return None

    current["analysis_batch"] = st.session_state.get("analysis_batch")
    current["job_file_name"] = job_file_name
    current["cv_file_names"] = cv_file_names or []
    current["updated_at"] = datetime.now().isoformat()
    current["status"] = "analyzed" if current.get("analysis_batch") else "created"

    saved = save_recruitment(current)
    st.session_state.current_recruitment = saved

    return saved


def render_dashboard():
    _ensure_current_recruitment()
    _render_recruitment_context()

    section_title(
        "Upload Files",
        "Upload one job description and up to 50 candidate CVs."
    )

    job_file = st.file_uploader("Upload job description PDF", type=["pdf"])

    cv_files = st.file_uploader(
        f"Upload candidate CV PDFs — max {MAX_CV_UPLOADS}",
        type=["pdf"],
        accept_multiple_files=True
    )

    col_analyze, col_save = st.columns([2, 1])

    with col_analyze:
        analyze = st.button("🚀 Analyze candidates", use_container_width=True)

    with col_save:
        manual_save = st.button("💾 Save Recruitment", use_container_width=True)

    if manual_save:
        saved = _save_current_recruitment(
            job_file_name=job_file.name if job_file else None,
            cv_file_names=[file.name for file in cv_files] if cv_files else [],
        )

        if saved:
            st.success(f"Recruitment saved: {saved['id']}")

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

        saved = _save_current_recruitment(
            job_file_name=job_file.name,
            cv_file_names=[file.name for file in cv_files],
        )

        if saved:
            st.success(f"Analysis completed and recruitment saved: {saved['id']}")

    batch = st.session_state.get("analysis_batch")

    if not batch:
        assistant_panel(
            "Recruiter Copilot",
            "Upload a job description and candidate CVs to start. Once the analysis is complete, I will summarize the candidate pool and recommend where to focus first."
        )
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
        "AI-powered overview of your candidate pool."
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
    section_title("Candidate Ranking", "Ranked by TalentCopilot match score.")

    for index, item in enumerate(results, start=1):
        match = item["match_result"]
        candidate = item["candidate"]

        col_rank, col_card, col_conf, col_status = st.columns([1, 4, 2, 2])

        with col_rank:
            st.subheader(f"#{index}")

        with col_card:
            candidate_card(candidate.name, match.overall_score, match.recommendation)
            st.caption(item["file"])

        with col_conf:
            metric_card("Confidence", f"{match.confidence_score}%", "AI confidence")

        with col_status:
            st.write(f"**{score_badge(match.overall_score)}**")

        st.write(match.executive_summary)
        st.divider()

    section_title(
        "Candidate Insight",
        "Detailed recommendation, score and confidence for the selected candidate."
    )

    options = [f"#{i+1} - {item['candidate'].name}" for i, item in enumerate(results)]
    selected = st.selectbox("Select a candidate", options)
    selected_index = options.index(selected)

    item = results[selected_index]
    match = item["match_result"]

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
