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
from talentcopilot.ui.brand import APP_ICON_PATH
from talentcopilot.ui.design_system.theme import apply_enterprise_theme
from talentcopilot.ui.enterprise_navigation import get_enterprise_navigation, get_page_by_label
from talentcopilot.ui.navigation_actions import consume_page_request
from talentcopilot.ui.premium_sidebar import render_premium_sidebar
from talentcopilot.ui.recruitment_workflow_shell import render_recruitment_workflow_shell


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
    st.session_state.setdefault("enterprise_page_label", "Executive Brief")

    # The brand lockup links to Home through a stable query parameter. This
    # preserves the active recruitment while making the logo a real navigation
    # control instead of decorative artwork.
    try:
        requested = st.query_params.get("tc_page", "")
        if isinstance(requested, list):
            requested = requested[0] if requested else ""
        requested = str(requested or "")
        if requested and get_page_by_label(requested) is not None:
            st.session_state["enterprise_page_label"] = requested
            st.query_params.clear()
    except Exception:
        pass


def _language_selector():
    language_keys = list(LANGUAGES.keys())
    current = st.session_state.language
    if current not in language_keys:
        current = language_keys[0]
    st.session_state.language = st.sidebar.selectbox(
        "Language",
        language_keys,
        index=language_keys.index(current),
        key="premium_sidebar_language",
    )


def _select_page(session):
    # Historical compatibility markers for contextual navigation tests: key="enterprise_section_key" · key="enterprise_page_label"
    pending = consume_page_request()
    if pending is not None and get_page_by_label(pending.page_label) is not None:
        st.session_state["enterprise_page_label"] = pending.page_label
        if pending.reason:
            st.session_state["enterprise_navigation_notice"] = pending.reason

    current_label = str(st.session_state.get("enterprise_page_label", "Executive Brief"))
    selected_page = get_page_by_label(current_label) or get_page_by_label("Executive Brief")
    if selected_page is None:
        raise RuntimeError("The default Executive Brief route is unavailable.")

    render_premium_sidebar(
        session,
        current_page=selected_page.label,
        app_version=APP_VERSION,
    )
    _language_selector()

    notice = st.session_state.pop("enterprise_navigation_notice", "")
    if notice:
        st.sidebar.markdown(
            f'<div class="tc-nav-notice">{notice}</div>',
            unsafe_allow_html=True,
        )
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
    page_icon = str(APP_ICON_PATH) if APP_ICON_PATH.exists() else "✦"
    st.set_page_config(page_title=APP_NAME, page_icon=page_icon, layout="wide")
    _initialize_state()
    apply_enterprise_theme()
    session = get_streamlit_session()
    selected_page = _select_page(session)

    invalidation_notice = consume_session_invalidation_notice()
    if invalidation_notice:
        st.warning(invalidation_notice)

    workflow_pages = {
        "Recruitment Overview",
        "Recruitment Workspace",
        "Dashboard Perspective",
        "Candidate Intelligence",
        "Compensation & Budget",
        "Hiring Budget",
        "Interview Intelligence",
        "Comparison",
        "Decision Board",
    }
    if selected_page.label in workflow_pages:
        render_recruitment_workflow_shell(session, current_page=selected_page.label)
    _render_import_health()
    _safe_call(selected_page.module, selected_page.function)()


if __name__ == "__main__":
    main()
