import importlib
from typing import Callable, Dict, Tuple

import streamlit as st

from talentcopilot.config import APP_NAME, APP_VERSION
from talentcopilot.i18n import LANGUAGES, tr
from talentcopilot.services.import_safety_audit import ImportSafetyAudit


PageSpec = Tuple[str, str]


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
    try:
        from talentcopilot.ui.theme import apply_theme
        apply_theme()
    except Exception:
        pass

    try:
        from talentcopilot.ui.premium_theme import apply_premium_ui
        apply_premium_ui()
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
        context = st.session_state.get("recruitment_context")
        render_sidebar_context(context)
        render_sidebar_workflow()
    except Exception:
        st.sidebar.markdown("## 🧠 TalentCopilot-AI")
        st.sidebar.caption(f"AI Recruitment Intelligence · {APP_VERSION}")


def navigation_registry() -> Dict[str, PageSpec]:
    return {
        "Home": ("talentcopilot.ui.home_v2", "render_home_v2"),
        "Decision Center": ("talentcopilot.ui.dashboard_v2", "render_dashboard_v2"),
        tr("menu.new_recruitment"): ("talentcopilot.ui.recruitment_wizard", "render_new_recruitment"),
        tr("menu.open_recruitment"): ("talentcopilot.ui.open_recruitment", "render_open_recruitment"),
        tr("menu.dashboard"): ("talentcopilot.ui.dashboard", "render_dashboard"),
        "Decision Workspace": ("talentcopilot.ui.decision_workspace", "render_decision_workspace"),
        "Candidates": ("talentcopilot.ui.candidates_v2", "render_candidates_v2"),
        "Talent Pool": ("talentcopilot.ui.talent_pool_v2", "render_talent_pool_v2"),
        "Recruiter Copilot": ("talentcopilot.ui.recruiter_copilot_v2", "render_recruiter_copilot_v2"),
        "Comparison": ("talentcopilot.ui.comparison_v2", "render_comparison_v2"),
        "Reports": ("talentcopilot.ui.reports_v2", "render_reports_v2"),
        tr("menu.settings"): ("talentcopilot.ui.settings", "render_settings"),
        "Session Health": ("talentcopilot.ui.session_health", "render_session_health"),
    }


def _initialize_state():
    if "language" not in st.session_state:
        st.session_state.language = "English"

    if "analysis_batch" not in st.session_state:
        st.session_state.analysis_batch = None

    if "recruitment_context" not in st.session_state:
        st.session_state.recruitment_context = None

    if "current_recruitment" not in st.session_state:
        st.session_state.current_recruitment = None


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


def _render_import_health():
    with st.sidebar.expander("App health"):
        report = ImportSafetyAudit().audit_navigation(navigation_registry())
        if report["missing"]:
            st.warning(f"{len(report['missing'])} import issue(s)")
            for item in report["missing"][:5]:
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

    pages = navigation_registry()
    page_label = st.sidebar.radio(tr("navigation"), list(pages.keys()))

    _render_import_health()

    module_name, function_name = pages[page_label]
    renderer = _safe_call(module_name, function_name)
    renderer()

    try:
        from talentcopilot.ui.components import footer
        footer()
    except Exception:
        pass


if __name__ == "__main__":
    main()
