import importlib
from typing import Callable

import streamlit as st

from talentcopilot.config import APP_NAME, APP_VERSION
from talentcopilot.i18n import LANGUAGES
from talentcopilot.services.import_safety_audit import ImportSafetyAudit
from talentcopilot.ui.design_system.navigation import get_enterprise_navigation
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


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


def _render_brand():
    st.sidebar.markdown(
        f"""
        <div style="display:flex;align-items:center;margin-bottom:1rem;">
            <div class="tc-logo-mark">TC</div>
            <div>
                <div style="font-weight:800;font-size:1rem;">TalentCopilot</div>
                <div style="font-size:0.78rem;opacity:0.72;">Enterprise · {APP_VERSION}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _language_selector():
    language_keys = list(LANGUAGES.keys())
    current = st.session_state.language
    if current not in language_keys:
        current = language_keys[0]
        st.session_state.language = current

    selected_language = st.sidebar.selectbox(
        "Language",
        language_keys,
        index=language_keys.index(current),
    )
    st.session_state.language = selected_language


def _render_navigation():
    sections = get_enterprise_navigation()

    selected = None
    st.sidebar.markdown("---")

    for section_name, section in sections.items():
        st.sidebar.markdown(f"**{section.label}**")
        labels = [f"{page.icon} {page.label}" for page in section.pages]
        choice = st.sidebar.radio(
            section.label,
            labels,
            label_visibility="collapsed",
            key=f"nav_{section_name}",
        )
        selected_page = section.pages[labels.index(choice)]
        if selected is None and st.session_state.get(f"nav_{section_name}") == choice:
            selected = selected_page

    return selected or list(sections.values())[0].pages[0]


def _render_import_health():
    with st.sidebar.expander("App health"):
        navigation = {}
        for section in get_enterprise_navigation().values():
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
    st.set_page_config(page_title=APP_NAME, page_icon="TC", layout="wide")

    _initialize_state()
    apply_enterprise_theme()
    _render_brand()
    _language_selector()

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
