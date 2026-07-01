
import streamlit as st

from talentcopilot.config import APP_NAME, APP_VERSION
from talentcopilot.engines.recruitment_pipeline import analyze_recruitment_batch

MAX_CV_UPLOADS = 50

st.set_page_config(page_title=APP_NAME, page_icon="🧠", layout="wide")

if "analysis_batch" not in st.session_state:
    st.session_state.analysis_batch = None

def score_badge(score):
    if score >= 85:
        return "🟢"
    elif score >= 70:
        return "🟡"
    elif score >= 50:
        return "🟠"
    return "🔴"

def progress(label, score):
    st.write(f"**{label}** — {score_badge(score)} {score}%")
    st.progress(score / 100)

def display_kpis(results):
    scores = [item["match_result"].overall_score for item in results]
    avg_score = round(sum(scores) / len(scores)) if scores else 0
    strong = sum(1 for item in results if item["match_result"].overall_score >= 85)
    interview = sum(1 for item in results if 70 <= item["match_result"].overall_score < 85)
    weak = sum(1 for item in results if item["match_result"].overall_score < 50)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("CV analyzed", len(results))
    col2.metric("Average score", f"{avg_score}%")
    col3.metric("Strong shortlist", strong)
    col4.metric("Weak fit", weak)

def display_ranking(results):
    st.header("🏆 Candidate Ranking")

    for index, item in enumerate(results, start=1):
        match = item["match_result"]
        candidate = item["candidate"]

        col1, col2, col3, col4 = st.columns([1, 4, 2, 2])
        col1.subheader(f"#{index}")
        col2.write(f"**{candidate.name}**")
        col2.caption(candidate.current_role or item["file"])
        col3.metric("Match", f"{match.overall_score}%")
        col4.metric("Confidence", f"{match.confidence_score}%")
        st.write(match.executive_summary)
        st.divider()

def display_candidate_detail(item):
    match = item["match_result"]
    candidate = item["candidate"]

    st.header("🔍 Candidate Detail")

    col1, col2, col3 = st.columns(3)
    col1.metric("Candidate", candidate.name)
    col2.metric("TalentCopilot Score", f"{match.overall_score}%")
    col3.metric("Confidence", f"{match.confidence_score}%")

    st.subheader("Recommendation")
    st.write(f"**{match.recommendation}**")
    st.write(match.executive_summary)

    st.divider()
    st.subheader("Why this score?")

    for detail in match.match_details:
        requirement = detail.requirement
        capability = detail.capability

        with st.expander(f"{score_badge(detail.score)} {requirement.name} — {detail.score}%"):
            progress("Match", detail.score)
            st.write(f"**Importance:** {requirement.importance}")
            st.write(f"**Expected level:** {requirement.expected_level}")

            if capability:
                st.write(f"**Detected level:** {capability.detected_level}")
                st.write(f"**Confidence:** {capability.confidence}%")
                st.write("**Evidence:**")
                for evidence in capability.evidence:
                    st.write(f"- {evidence.text}")
            else:
                st.write("**Detected level:** Not detected")
                st.write("**Evidence:** No evidence found")

            st.write(f"**Explanation:** {detail.explanation}")

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Gaps to Explore")
        if match.gaps:
            for gap in match.gaps:
                st.write(f"⚠️ **{gap.competency}** — {gap.severity}")
                st.caption(gap.explanation)
                st.write(gap.recommendation)
        else:
            st.write("No major gap detected.")

    with col_b:
        st.subheader("Interview Questions")
        for q in match.interview_questions:
            st.write(f"**{q.priority} — {q.linked_competency}**")
            st.write(q.question)
            st.caption(q.purpose)

st.title("🧠 TalentCopilot AI")
st.caption(f"Version {APP_VERSION} — Understand every candidate. Explain every decision.")

st.sidebar.header("Recruitment Analysis")

job_file = st.sidebar.file_uploader("Upload job description PDF", type=["pdf"])

cv_files = st.sidebar.file_uploader(
    f"Upload candidate CV PDFs — max {MAX_CV_UPLOADS}",
    type=["pdf"],
    accept_multiple_files=True
)

analyze = st.sidebar.button("Analyze candidates")
reset = st.sidebar.button("Reset analysis")

if reset:
    st.session_state.analysis_batch = None
    st.rerun()

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

batch = st.session_state.analysis_batch

if batch is None:
    st.info("Upload one job description PDF and up to 50 candidate CV PDFs to start.")
    st.stop()

if not batch["success"]:
    st.error("The job description could not be processed.")
    for error in batch["errors"]:
        st.write(f"- {error['file']}: {error['error']}")
    st.stop()

results = batch["results"]

if not results:
    st.error("No candidate could be analyzed.")
    st.stop()

st.success(f"{len(results)} candidate(s) analyzed successfully.")

st.subheader("Job analyzed")
st.write(f"**{batch['job'].title}**")

display_kpis(results)
st.divider()

display_ranking(results)

options = [f"#{i+1} - {item['candidate'].name}" for i, item in enumerate(results)]

selected = st.selectbox("Select a candidate for detailed analysis", options)
selected_index = options.index(selected)

display_candidate_detail(results[selected_index])
