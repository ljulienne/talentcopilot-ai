
import streamlit as st
from datetime import datetime

def render_new_recruitment():
    st.title("🧠 New Recruitment")
    st.caption("Create a recruitment context before uploading the job description and CVs.")

    with st.form("new_recruitment_form"):
        job_title = st.text_input("Job Title", placeholder="HRIS Project Manager")
        company = st.text_input("Company", placeholder="Your company or organization")
        department = st.text_input("Department", placeholder="HR / HRIS / IT")
        location = st.text_input("Location", placeholder="Paris, Papeete, Remote...")

        recruitment_type = st.selectbox(
            "Recruitment Type",
            ["Permanent", "Contract", "Internship", "Consultant", "Freelancer"]
        )

        language = st.selectbox(
            "Job Language",
            ["Auto Detect", "English", "French", "Mandarin"]
        )

        max_candidates = st.selectbox(
            "Maximum CVs",
            [10, 20, 30, 40, 50],
            index=4
        )

        submitted = st.form_submit_button("Continue →", use_container_width=True)

    if submitted:
        if not job_title:
            st.warning("Please enter a job title.")
            return

        st.session_state.recruitment_context = {
            "job_title": job_title,
            "company": company,
            "department": department,
            "location": location,
            "recruitment_type": recruitment_type,
            "language": language,
            "max_candidates": max_candidates,
            "created_at": datetime.now().isoformat()
        }

        st.success("Recruitment created. Go to Dashboard to upload files.")
