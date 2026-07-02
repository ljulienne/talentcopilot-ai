import streamlit as st
from datetime import datetime

from talentcopilot.storage.recruitment_store import generate_recruitment_id
from talentcopilot.ui.components import section_title, assistant_panel, card


def render_new_recruitment():
    st.markdown("""
    <div class="tc-hero">
        <h1>➕ New Recruitment</h1>
        <h3>Step 1 of 4 — Recruitment Context</h3>
        <p class="tc-muted">
        Create the recruitment context before uploading your job description and CVs.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([2, 1])

    with col_left:
        section_title(
            "Recruitment Information",
            "These details will be reused in the dashboard, comparison and recruiter report."
        )

        with st.form("new_recruitment_form"):
            job_title = st.text_input("Job Title", placeholder="HRIS Project Manager")
            company = st.text_input("Company", placeholder="Your company or organization")
            department = st.text_input("Department", placeholder="HR / HRIS / IT")
            location = st.text_input("Location", placeholder="Paris, Papeete, Remote...")

            col1, col2 = st.columns(2)

            with col1:
                recruitment_type = st.selectbox(
                    "Recruitment Type",
                    ["Permanent", "Contract", "Internship", "Consultant", "Freelancer"]
                )

            with col2:
                language = st.selectbox(
                    "Job Language",
                    ["Auto Detect", "English", "French", "Mandarin"]
                )

            max_candidates = st.selectbox(
                "Maximum CVs",
                [10, 20, 30, 40, 50],
                index=4
            )

            submitted = st.form_submit_button("Continue to Dashboard →", use_container_width=True)

        if submitted:
            if not job_title:
                st.warning("Please enter a job title.")
                return

            now = datetime.now().isoformat()
            recruitment_id = generate_recruitment_id()

            context = {
                "job_title": job_title,
                "company": company,
                "department": department,
                "location": location,
                "recruitment_type": recruitment_type,
                "language": language,
                "max_candidates": max_candidates,
                "created_at": now,
            }

            st.session_state.recruitment_context = context

            st.session_state.current_recruitment = {
                "id": recruitment_id,
                "title": job_title,
                "context": context,
                "language": language,
                "job_description": None,
                "analysis_batch": None,
                "created_at": now,
                "updated_at": now,
                "status": "created",
            }

            if "analysis_batch" in st.session_state:
                del st.session_state.analysis_batch

            st.success("Recruitment created. Go to Dashboard to upload files.")

    with col_right:
        assistant_panel(
            "Recruiter Copilot",
            "Start by defining the recruitment context. It helps TalentCopilot produce clearer reports and better summaries."
        )

        card(
            "Workflow",
            "1. Create recruitment\n2. Upload job description\n3. Upload CVs\n4. Analyze and compare",
            "Guided"
        )

        card(
            "Languages",
            "TalentCopilot supports English, French and Mandarin for CV and job description analysis.",
            "FR / EN / ZH"
        )
