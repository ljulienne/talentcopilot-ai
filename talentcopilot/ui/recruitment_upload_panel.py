"""Real upload entry point embedded in the active Recruitment workflow."""

from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.recruitment_upload_session_service import RecruitmentUploadSessionService
from talentcopilot.services.streamlit_session_bridge import set_streamlit_session
from talentcopilot.services.upload_text_reader_service import UploadTextReaderService


def render_recruitment_upload_panel(current_session=None):
    import streamlit as st

    with st.expander(
        "Start or replace a recruitment",
        expanded=current_session is None,
    ):
        st.write(
            "Upload one job description and one or more candidate CVs. "
            "The resulting analysis becomes the official session used by every recruitment module."
        )

        job_file = st.file_uploader(
            "Job description",
            type=["txt", "pdf", "docx"],
            key="recruitment_job_upload",
        )
        candidate_files = st.file_uploader(
            "Candidate CVs",
            type=["txt", "pdf", "docx"],
            accept_multiple_files=True,
            key="recruitment_candidate_uploads",
        )

        primary, secondary = st.columns([1.5, 1])
        run_upload = primary.button(
            "Analyze uploaded candidates",
            type="primary",
            use_container_width=True,
            key="recruitment_run_upload",
        )
        load_sample = secondary.button(
            "Load sample data",
            use_container_width=True,
            key="recruitment_load_sample",
        )

        if load_sample:
            session = set_streamlit_session(create_demo_recruitment_session())
            st.success("Sample recruitment loaded. All modules now use this session.")
            st.rerun()

        if run_upload:
            if job_file is None:
                st.error("Upload a job description before starting the analysis.")
                return current_session
            if not candidate_files:
                st.error("Upload at least one candidate CV before starting the analysis.")
                return current_session

            reader = UploadTextReaderService()
            with st.spinner("Reading documents and analysing candidates..."):
                job_document = reader.read_uploaded_file(job_file)
                candidate_documents = [reader.read_uploaded_file(item) for item in candidate_files]

                failed = [doc.filename for doc in candidate_documents if doc.status != "OK" or not doc.text.strip()]
                if job_document.status != "OK" or not job_document.text.strip():
                    st.error(f"The job description could not be read: {job_document.status}")
                    return current_session
                if failed:
                    st.error("These CVs could not be read: " + ", ".join(failed))
                    return current_session

                try:
                    session = RecruitmentUploadSessionService().run(job_document, candidate_documents)
                except Exception as exc:
                    st.error(f"The analysis could not be completed: {exc}")
                    return current_session

                set_streamlit_session(session)

            st.success(
                f"Recruitment created for {session.role_title}: "
                f"{session.candidate_count} candidates analysed."
            )
            st.rerun()

    return current_session
