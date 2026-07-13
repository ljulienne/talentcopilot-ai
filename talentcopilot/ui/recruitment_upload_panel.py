"""Real upload entry point embedded in the active Recruitment workflow."""

from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.analysis_provenance import (
    ANALYSIS_SCHEMA_VERSION,
    MATCHING_ENGINE_VERSION,
    OFFICIAL_PIPELINE,
    hash_bytes,
)
from talentcopilot.services.recruitment_upload_session_service import RecruitmentUploadSessionService
from talentcopilot.services.streamlit_session_bridge import set_streamlit_session
from talentcopilot.services.upload_text_reader_service import UploadTextReaderService
import time


def _uploaded_bytes(uploaded_file) -> bytes:
    return bytes(uploaded_file.getvalue())


def _analysis_request_key(job_file, candidate_files) -> str:
    components = [
        ANALYSIS_SCHEMA_VERSION,
        MATCHING_ENGINE_VERSION,
        OFFICIAL_PIPELINE,
        hash_bytes(_uploaded_bytes(job_file)),
    ]
    components.extend(
        hash_bytes(_uploaded_bytes(item))
        for item in candidate_files
    )
    return "::".join(components)


def render_recruitment_upload_panel(current_session=None):
    import streamlit as st

    with st.expander(
        "Start or replace a recruitment",
        expanded=current_session is None,
    ):
        st.write(
            "Upload one job description and one or more candidate CVs. "
            "The resulting analysis becomes the official session used by "
            "every recruitment module."
        )

        # A form prevents Streamlit from rerunning the full application while
        # users are still selecting multiple files.
        with st.form(
            "recruitment_upload_form",
            clear_on_submit=False,
        ):
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
            run_upload = primary.form_submit_button(
                "Analyze uploaded candidates",
                type="primary",
                use_container_width=True,
            )
            load_sample = secondary.form_submit_button(
                "Load sample data",
                use_container_width=True,
            )

        if load_sample:
            session = set_streamlit_session(
                create_demo_recruitment_session()
            )
            st.success(
                "Sample recruitment loaded. "
                "All modules now use this session."
            )
            st.rerun()

        if run_upload:
            if job_file is None:
                st.error(
                    "Upload a job description before starting the analysis."
                )
                return current_session

            if not candidate_files:
                st.error(
                    "Upload at least one candidate CV before starting "
                    "the analysis."
                )
                return current_session

            request_key = _analysis_request_key(
                job_file,
                candidate_files,
            )

            cached_key = st.session_state.get(
                "talentcopilot_last_analysis_request_key"
            )
            cached_session = st.session_state.get(
                "talentcopilot_last_analysis_session"
            )

            if cached_key == request_key and cached_session is not None:
                set_streamlit_session(cached_session)
                st.info(
                    "The identical documents were already analysed in this "
                    "browser session. The official result has been restored "
                    "without rerunning extraction or matching."
                )
                st.rerun()

            reader = UploadTextReaderService()

            started_total = time.perf_counter()
            started_extraction = time.perf_counter()

            with st.spinner(
                "Reading documents and analysing candidates..."
            ):
                job_document = reader.read_uploaded_file(job_file)
                candidate_documents = [
                    reader.read_uploaded_file(item)
                    for item in candidate_files
                ]

                extraction_seconds = (
                    time.perf_counter() - started_extraction
                )

                failed = [
                    doc.filename
                    for doc in candidate_documents
                    if doc.status != "OK" or not doc.text.strip()
                ]

                if (
                    job_document.status != "OK"
                    or not job_document.text.strip()
                ):
                    st.error(
                        "The job description could not be read: "
                        f"{job_document.status}"
                    )
                    return current_session

                if failed:
                    st.error(
                        "These CVs could not be read: "
                        + ", ".join(failed)
                    )
                    return current_session

                started_analysis = time.perf_counter()

                try:
                    session = RecruitmentUploadSessionService().run(
                        job_document,
                        candidate_documents,
                    )
                except Exception as exc:
                    st.error(
                        f"The analysis could not be completed: {exc}"
                    )
                    return current_session

                analysis_seconds = (
                    time.perf_counter() - started_analysis
                )
                total_seconds = time.perf_counter() - started_total

                session.metadata.update(
                    {
                        "extraction_seconds": round(
                            extraction_seconds,
                            4,
                        ),
                        "ranking_and_session_seconds": round(
                            analysis_seconds,
                            4,
                        ),
                        "total_analysis_seconds": round(
                            total_seconds,
                            4,
                        ),
                    }
                )

                set_streamlit_session(session)

                # Session-local only: CV data is never placed in a global
                # Streamlit cache shared across users.
                st.session_state[
                    "talentcopilot_last_analysis_request_key"
                ] = request_key
                st.session_state[
                    "talentcopilot_last_analysis_session"
                ] = session

            st.success(
                f"Recruitment created for {session.role_title}: "
                f"{session.candidate_count} candidates analysed in "
                f"{session.metadata['total_analysis_seconds']:.2f}s."
            )
            st.caption(
                f"Pipeline: {session.metadata.get('pipeline')} · "
                f"Analysis: {session.metadata.get('analysis_version')} · "
                f"Extraction: "
                f"{session.metadata.get('extraction_seconds', 0):.2f}s · "
                f"Ranking/session: "
                f"{session.metadata.get('ranking_and_session_seconds', 0):.2f}s"
            )
            st.rerun()

    return current_session
