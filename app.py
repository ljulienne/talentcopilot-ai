import importlib
from typing import Callable

import streamlit as st

from talentcopilot.config import APP_NAME, APP_VERSION
from talentcopilot.i18n import LANGUAGES
from talentcopilot.services.import_safety_audit import ImportSafetyAudit
from talentcopilot.services.streamlit_session_bridge import (
    consume_session_invalidation_notice,
    get_streamlit_session,
)
from talentcopilot.ui.design_system.theme import apply_enterprise_theme
from talentcopilot.ui.enterprise_navigation import get_enterprise_navigation
from talentcopilot.ui.navigation_actions import consume_page_request
from talentcopilot.ui.enterprise_shell import render_current_recruitment, render_enterprise_brand


def _safe_call(module_name: str, function_name: str) -> Callable:
    def _renderer():
        try:
            module = importlib.import_module(module_name)
            function = getattr(module, function_name)
            function()
        except Exception as exc:
            st.error("This page could not render completely.")
            st.caption(f"{module_name}.{function_name}")
            st.exception(exc)
    return _renderer


def _initialize_state():
    st.session_state.setdefault("language", "English")
    st.session_state.setdefault("analysis_batch", None)
    st.session_state.setdefault("recruitment_context", None)
    st.session_state.setdefault("current_recruitment", None)


def _language_selector():
    language_keys = list(LANGUAGES.keys())
    current = st.session_state.language
    if current not in language_keys:
        current = language_keys[0]
    st.session_state.language = st.sidebar.selectbox("Language", language_keys, index=language_keys.index(current))


def _select_page():
    sections = get_enterprise_navigation()
    section_keys = list(sections.keys())

    pending = consume_page_request()
    if pending is not None:
        for section_key, candidate_section in sections.items():
            if any(page.label == pending.page_label for page in candidate_section.pages):
                st.session_state["enterprise_section_key"] = section_key
                st.session_state["enterprise_page_label"] = pending.page_label
                if pending.reason:
                    st.session_state["enterprise_navigation_notice"] = pending.reason
                break

    selected_section_key = st.sidebar.radio(
        "Workspace",
        section_keys,
        format_func=lambda key: sections[key].title,
        key="enterprise_section_key",
    )
    section = sections[selected_section_key]
    st.sidebar.caption(section.description)

    page_labels = [page.label for page in section.pages]
    selected_label = st.session_state.get("enterprise_page_label")
    if selected_label not in page_labels:
        st.session_state["enterprise_page_label"] = page_labels[0]

    selected_page_label = st.sidebar.radio(
        "Page",
        page_labels,
        key="enterprise_page_label",
    )
    selected_page = next(page for page in section.pages if page.label == selected_page_label)
    if selected_page.description:
        st.sidebar.caption(selected_page.description)

    notice = st.session_state.pop("enterprise_navigation_notice", "")
    if notice:
        st.sidebar.success(notice)
    return selected_page


def _render_import_health():
    with st.sidebar.expander("App health"):
        navigation = {}
        for section in get_enterprise_navigation().values():
            for page in section.pages:
                navigation[page.label] = (page.module, page.function)

        report = ImportSafetyAudit().audit_navigation(navigation)
        if report["missing"]:
            st.warning(f"{len(report['missing'])} import issue(s)")
            for item in report["missing"][:5]:
                st.caption(item)
        else:
            st.success("Imports OK")



def _render_runtime_score_diagnostic(session):
    import streamlit as st

    with st.expander("Runtime diagnostic — temporary", expanded=True):
        st.code(
            "Build commit: 5d8ff1ebe6f35592e064f0b389b51fe0c9a0e09d\n"
            "Expected analysis version: 3.2.1A.2.2\n"
            "Expected pipeline: real-upload-ranking"
        )

        if session is None:
            st.warning("No active RecruitmentSession.")
            return

        metadata = dict(getattr(session, "metadata", {}) or {})

        st.write("Session ID:", getattr(session, "session_id", "-"))
        st.write("Session source:", metadata.get("source"))
        st.write("Analysis version:", metadata.get("analysis_version"))
        st.write("Pipeline:", metadata.get("pipeline"))
        st.write(
            "Matching engine version:",
            metadata.get("matching_engine_version"),
        )
        st.write(
            "Normalization version:",
            metadata.get("normalization_version"),
        )
        st.write(
            "Total analysis time:",
            metadata.get("total_analysis_seconds"),
        )

        rows = []
        for analysis in getattr(
            session,
            "ranked_analyses",
            [],
        ) or []:
            rows.append(
                {
                    "rank": getattr(analysis, "rank", None),
                    "candidate": getattr(
                        analysis,
                        "candidate_name",
                        None,
                    ),
                    "official_match": getattr(
                        analysis,
                        "match_score",
                        None,
                    ),
                }
            )

        st.write("Official session rows:")
        st.dataframe(rows, use_container_width=True)


def main():
    st.set_page_config(page_title=APP_NAME, page_icon="TC", layout="wide")
    _initialize_state()
    apply_enterprise_theme()
    render_enterprise_brand(APP_VERSION)
    _language_selector()
    st.sidebar.markdown("---")
    selected_page = _select_page()
    session = get_streamlit_session()
    invalidation_notice = consume_session_invalidation_notice()
    if invalidation_notice:
        st.warning(invalidation_notice)

    render_current_recruitment(session)
    _render_runtime_score_diagnostic(session)
    _render_import_health()
    _safe_call(selected_page.module, selected_page.function)()


if __name__ == "__main__":
    main()
