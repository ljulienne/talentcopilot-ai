import importlib
from typing import Callable

import streamlit as st

from talentcopilot.config import APP_NAME, APP_VERSION
from talentcopilot.i18n import LANGUAGES, tr
from talentcopilot.services.import_safety_audit import ImportSafetyAudit
from talentcopilot.ui.navigation import get_navigation_sections


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


def _apply_theme():
    for module_name, function_name in [
        ("talentcopilot.ui.theme", "apply_theme"),
        ("talentcopilot.ui.premium_theme", "apply_premium_ui"),
    ]:
        try:
            module = importlib.import_module(module_name)
            getattr(module, function_name)()
        except Exception:
            pass


def _render_sidebar_brand():
    try:
        from talentcopilot.ui.sidebar import (
            render_sidebar_brand,
            render_sidebar_context,
            render_sidebar_workflow,
        )

        render_sidebar_brand(APP_VERSION)
        render_sidebar_context(st.session_state.get("recruitment_context"))
        render_sidebar_workflow()
    except Exception:
        st.sidebar.markdown("## 🧠 TalentCopilot-AI")
        st.sidebar.caption(f"AI Recruitment Intelligence · {APP_VERSION}")


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
        st.session_state.language = current

    selected_language = st.sidebar.selectbox(
        "🌍 Language",
        language_keys,
        index=language_keys.index(current),
    )
    st.session_state.language = selected_language


def _render_navigation():
    sections = get_navigation_sections()

    section_names = list(sections.keys())
    selected_section = st.sidebar.radio(
        "Navigation",
        section_names,
        format_func=lambda name: sections[name].label,
    )

    st.sidebar.caption(sections[selected_section].description)

    page_options = sections[selected_section].pages
    selected_page = st.sidebar.radio(
        "Page",
        page_options,
        format_func=lambda page: page.label,
    )

    return selected_page


def _render_import_health():
    with st.sidebar.expander("App health"):
        sections = get_navigation_sections()
        navigation = {}
        for section in sections.values():
            for page in section.pages:
                navigation[page.label] = (page.module, page.function)

        report = ImportSafetyAudit().audit_navigation(navigation)
        if report["missing"]:
            st.warning(f"{len(report['missing'])} import issue(s)")
            for item in report["missing"][:6]:
                st.caption(item)
        else:
            st.success("Imports OK")


def main():
    st.set_page_config(page_title=APP_NAME, page_icon="🧠", layout="wide")

    _initialize_state()
    _apply_theme()
    _render_sidebar_brand()
    _language_selector()

    st.sidebar.markdown("---")

    selected_page = _render_navigation()
    _render_import_health()

    renderer = _safe_call(selected_page.module, selected_page.function)
    renderer()

    try:
        from talentcopilot.ui.components import footer
        footer()
    except Exception:
        pass


if __name__ == "__main__":
    main()
