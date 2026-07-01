
import streamlit as st

from talentcopilot.config import APP_NAME, APP_VERSION
from talentcopilot.engines.recruitment_pipeline import analyze_recruitment_batch


st.set_page_config(
    page_title=APP_NAME,
    page_icon="🧠",
    layout="wide"
)


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


def display_ranking(results):
    st.header("🏆 Candidate Ranking")

    for index, item in enumerate(results, start=1):
        match = item["match_result"]
        candidate = item["candidate"]

        with st.container():
            col1, col2, col3, col4 = st.columns([1, 4, 2, 2])

            with col1:
                st.subheader(f"#{index}")

            with col2:
                st.write(f"**{candidate.name}**")
                st.caption(candidate.current_role or item["file"])

            with col3:
                st.metric("Match", f"{match.overall_score}%")

            with col4:
                st.metric("Confidence", f"{match.confidence_score}%")

            st.write(match.executive_summary)
            st.divider()


def display_candidate_detail(item):
    match = item["match_result"]
    candidate = item["candidate"]
    job = match.job

    st.header("🔍 Candidate Detail")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Candidate", candidate.name)

    with col2:
        st.metric("TalentCopilot Score", f"{match.overall_score}%")

    with col3:
        st.metric("Confidence", f"{match.confidence_score}%")

    st.subheader("Recommendation")
    st.write(f"**{match.recommendation}**")
    st.write(match.executive_summary)

    st.divider()

    st.subheader("Why this score?")

    for detail in match.match_details:
        requirement = detail.requirement
        capability = detail.capability

        with st.expander(
            f"{score_badge(detail.score)} {requirement.name} — {detail.score}%"
        ):
            progress("Match", detail.score)

            st.write(f"**Importance:** {requirement.importance}")
            st.write(f"**Expected level:** {requirement.expected_level}")

            if capability:
                st.write(f"**Detected level:** {capability.detected_level}")
                st.write(f"**Confidence:** {capability.confidence}%")

                st.write("**Evidence:**")
                if capability.evidence:
                    for evidence in capability.evidence:
                        st.write(f"- {evidence.text}")
                else:
                    st.write("- No explicit evidence found")
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

    st.divider()

    st.subheader("Detected Candidate Capabilities")
    for capability in candidate.capabilities:
        with st.expander(f"{capability.name} — {capability.detected_level}"):
            st.write(f"**Category:** {capability.category}")
            st.write(f"**Confidence:** {capability.confidence}%")
            st.write("**Evidence:**")
            for evidence in capability.evidence:
                st.write(f"- {evidence.text}")


st.title("🧠 TalentCopilot AI")
st.caption(f"Version {APP_VERSION} — Understand every candidate. Explain every decision.")

st.sidebar.header("Recruitment Analysis")

job_file = st.sidebar.file_uploader(
    "Upload job description PDF",
    type=["pdf"]
)

cv_files = st.sidebar.file_uploader(
    "Upload candidate CV PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

analyze = st.sidebar.button("Analyze candidates")

if analyze:
    if not job_file:
        st.warning("Please upload a job description PDF.")
        st.stop()

    if not cv_files:
        st.warning("Please upload at least one candidate CV PDF.")
        st.stop()

    with st.spinner("Running TalentCopilot analysis..."):
        batch = analyze_recruitment_batch(job_file, cv_files)

    if not batch["success"]:
        st.error("The job description could not be processed.")
        for error in batch["errors"]:
            st.write(f"- {error['file']}: {error['error']}")
        st.stop()

    if batch["errors"]:
        st.warning("Some files could not be processed:")
        for error in batch["errors"]:
            st.write(f"- {error['file']}: {error['error']}")

    results = batch["results"]

    if not results:
        st.error("No candidate could be analyzed.")
        st.stop()

    st.success(f"{len(results)} candidate(s) analyzed successfully.")

    st.subheader("Job analyzed")
    st.write(f"**{batch['job'].title}**")

    display_ranking(results)

    options = [
        f"#{i+1} - {item['candidate'].name}"
        for i, item in enumerate(results)
    ]

    selected = st.selectbox("Select a candidate for detailed analysis", options)
    selected_index = options.index(selected)

    display_candidate_detail(results[selected_index])

else:
    st.info("Upload one job description PDF and one or more candidate CV PDFs to start.")
