"""Real upload entry point embedded in the active Recruitment workflow."""

import os
from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.analysis_provenance import (
    ANALYSIS_SCHEMA_VERSION,
    MATCHING_ENGINE_VERSION,
    OFFICIAL_PIPELINE,
    hash_bytes,
)
from talentcopilot.services.isolated_recruitment_upload_service import IsolatedRecruitmentUploadService
from talentcopilot.services.recruitment_upload_session_service import RecruitmentUploadSessionService
from talentcopilot.services.streamlit_session_bridge import set_streamlit_session
from talentcopilot.services.upload_text_reader_service import UploadTextReaderService
import time


# Increment whenever the canonical score/session contract changes.
OFFICIAL_SCORE_CACHE_SCHEMA = "isolated-fit-session-v3.4"


def _uploaded_bytes(uploaded_file) -> bytes:
    return bytes(uploaded_file.getvalue())


def _analysis_request_key(job_file, candidate_files) -> str:
    components = [
        OFFICIAL_SCORE_CACHE_SCHEMA,
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

    parity = st.session_state.get(
        "talentcopilot_runtime_scoring_parity"
    )

    # Temporary environment fingerprint.
    import hashlib
    import importlib
    import importlib.metadata
    import json
    import platform
    import sys
    from pathlib import Path

    def _distribution_version(name):
        try:
            return importlib.metadata.version(name)
        except Exception:
            return "not-installed"

    def _module_fingerprint(module_name):
        try:
            module = importlib.import_module(module_name)
            module_path = getattr(module, "__file__", None)

            if not module_path:
                return {
                    "module": module_name,
                    "path": None,
                    "sha256": None,
                }

            path = Path(module_path).resolve()
            content = path.read_bytes()

            return {
                "module": module_name,
                "path": str(path),
                "sha256": hashlib.sha256(
                    content
                ).hexdigest()[:20],
            }
        except Exception as exc:
            return {
                "module": module_name,
                "error": type(exc).__name__,
            }

    environment_fingerprint = {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "executable": sys.executable,
        "cwd": str(Path.cwd()),
        "packages": {
            name: _distribution_version(name)
            for name in [
                "streamlit",
                "pypdf",
                "pydantic",
                "openai",
                "numpy",
                "pandas",
                "scikit-learn",
                "python-dotenv",
            ]
        },
        "modules": [
            _module_fingerprint(name)
            for name in [
                "talentcopilot.real_ranking.pipeline",
                "talentcopilot.decision_core.fit_intelligence_engine",
                "talentcopilot.services.real_upload_ranking_service",
                "talentcopilot.services.recruitment_upload_session_service",
                "talentcopilot.services.upload_text_reader_service",
                "talentcopilot.llm_extraction.provider",
            ]
        ],
        "configuration_names": sorted(
            name
            for name in os.environ
            if any(
                marker in name.upper()
                for marker in [
                    "TALENTCOPILOT",
                    "OPENAI",
                    "LLM",
                    "CACHE",
                    "PYTHON",
                    "STREAMLIT",
                ]
            )
            and not any(
                secret in name.upper()
                for secret in [
                    "KEY",
                    "TOKEN",
                    "SECRET",
                    "PASSWORD",
                ]
            )
        ),
        "sys_path": list(sys.path),
    }

    with st.expander(
        "Runtime environment fingerprint",
        expanded=True,
    ):
        st.json(environment_fingerprint)

    if parity:
        with st.expander(
            "Runtime parity check",
            expanded=True,
        ):
            st.write(
                {
                    "python": parity.get("python"),
                    "pypdf": parity.get("pypdf"),
                    "job_characters": parity.get(
                        "job_characters"
                    ),
                    "candidate_characters": parity.get(
                        "candidate_characters"
                    ),
                }
            )

            st.dataframe(
                parity.get("rows", []),
                use_container_width=True,
                hide_index=True,
            )

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

            cached_session_schema = (
                getattr(cached_session, "metadata", {}) or {}
            ).get("official_score_cache_schema")

            if (
                cached_key == request_key
                and cached_session is not None
                and cached_session_schema == OFFICIAL_SCORE_CACHE_SCHEMA
            ):
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
                    # Run both paths with the exact same extracted documents.
                    # This is diagnostic only; the isolated result remains
                    # the session used by the product.
                    direct_session = (
                        RecruitmentUploadSessionService().run(
                            job_document,
                            candidate_documents,
                        )
                    )

                    session = IsolatedRecruitmentUploadService().run(
                        job_document,
                        candidate_documents,
                    )

                    import platform

                    try:
                        import pypdf
                        pypdf_version = getattr(
                            pypdf,
                            "__version__",
                            "unknown",
                        )
                    except Exception:
                        pypdf_version = "unavailable"

                    direct_by_name = {
                        item.candidate_name: item
                        for item in direct_session.ranked_analyses
                    }

                    isolated_by_name = {
                        item.candidate_name: item
                        for item in session.ranked_analyses
                    }

                    candidate_names = sorted(
                        set(direct_by_name)
                        | set(isolated_by_name)
                    )

                    parity_rows = []

                    for candidate_name in candidate_names:
                        direct_item = direct_by_name.get(
                            candidate_name
                        )
                        isolated_item = isolated_by_name.get(
                            candidate_name
                        )

                        parity_rows.append(
                            {
                                "candidate": candidate_name,
                                "direct_match": (
                                    getattr(
                                        direct_item,
                                        "match_score",
                                        None,
                                    )
                                    if direct_item
                                    else None
                                ),
                                "isolated_match": (
                                    getattr(
                                        isolated_item,
                                        "match_score",
                                        None,
                                    )
                                    if isolated_item
                                    else None
                                ),
                                "direct_confidence": (
                                    getattr(
                                        direct_item,
                                        "official_confidence_score",
                                        None,
                                    )
                                    if direct_item
                                    else None
                                ),
                                "isolated_confidence": (
                                    getattr(
                                        isolated_item,
                                        "official_confidence_score",
                                        None,
                                    )
                                    if isolated_item
                                    else None
                                ),
                            }
                        )

                    parity_payload = {
                        "python": platform.python_version(),
                        "pypdf": pypdf_version,
                        "job_characters": len(
                            str(job_document.text or "")
                        ),
                        "candidate_characters": {
                            document.filename: len(
                                str(document.text or "")
                            )
                            for document in candidate_documents
                        },
                        "rows": parity_rows,
                    }

                    session_metadata = dict(
                        getattr(session, "metadata", {}) or {}
                    )
                    session_metadata[
                        "runtime_scoring_parity"
                    ] = parity_payload
                    session.metadata = session_metadata

                    st.session_state[
                        "talentcopilot_runtime_scoring_parity"
                    ] = parity_payload
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
