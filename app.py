import importlib
from typing import Callable

import streamlit as st

from talentcopilot.config import APP_NAME, APP_VERSION
from talentcopilot.i18n import LANGUAGES
from talentcopilot.services.import_safety_audit import ImportSafetyAudit
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session
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


def main():
    st.set_page_config(page_title=APP_NAME, page_icon="TC", layout="wide")
    _initialize_state()
    apply_enterprise_theme()
    render_enterprise_brand(APP_VERSION)
    _language_selector()
    st.sidebar.markdown("---")
    selected_page = _select_page()
    render_current_recruitment(get_streamlit_session())
    _render_import_health()
    _safe_call(selected_page.module, selected_page.function)()


if __name__ == "__main__":
    main()
