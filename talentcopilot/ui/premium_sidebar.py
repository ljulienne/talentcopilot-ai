from __future__ import annotations

from dataclasses import dataclass
from html import escape

from talentcopilot.services.compensation_budget_service import CompensationBudgetService
from talentcopilot.services.recruitment_workflow_state import get_workflow_context
from talentcopilot.ui.brand import brand_lockup_html
from talentcopilot.ui.navigation_actions import request_page


@dataclass(frozen=True)
class SidebarItem:
    key: str
    label: str
    page_label: str
    description: str
    glyph: str
    badge: str = ""


# Compatibility constants retained for Release 7.8.0 tests and external imports.
RECRUITMENT_MENU_KEYS = ("overview", "candidates", "interview", "decide")
RECRUITMENT_MENU_LABELS = ("Overview", "Candidates", "Interview", "Compare & decide")

# Release 7.8.1 recruiter-facing journey.
RECRUITMENT_JOURNEY_KEYS = ("overview", "candidates", "budget", "interview", "decide")
RECRUITMENT_JOURNEY_LABELS = (
    "Overview",
    "Dashboard Perspective",
    "Compensation & Budget",
    "Interview & Assessment",
    "Compare & decide",
)

_PAGE_TO_MENU_KEY = {
    "Recruitment Workspace": "overview",
    "Recruitment Overview": "overview",
    "Dashboard Perspective": "candidates",
    "Candidate Intelligence": "candidates",
    "Hiring Budget": "budget",
    "Compensation & Budget": "budget",
    "Interview Intelligence": "interview",
    "Interview Workspace": "interview",
    "Comparison": "decide",
    "Decision Board": "decide",
}


def _candidate_count(session) -> int:
    if session is None:
        return 0
    value = getattr(session, "candidate_count", None)
    if value is not None:
        return int(value or 0)
    return len(getattr(session, "ranked_analyses", ()) or ())


def _analyzed_count(session) -> int:
    if session is None:
        return 0
    value = getattr(session, "analyzed_count", None)
    if value is not None:
        return int(value or 0)
    return len(getattr(session, "ranked_analyses", ()) or ())


def resolve_recruitment_destinations(
    session,
    *,
    current_page: str = "",
    include_journey_v2: bool = False,
) -> tuple[SidebarItem, ...]:
    """Return the sidebar destinations without changing workflow data.

    The default retains the 7.8.0 four-item contract. The live sidebar opts into
    the 7.8.1 five-destination journey with Dashboard Perspective and
    Compensation & Budget.
    """

    context = get_workflow_context(session, current_page=current_page)
    total = _candidate_count(session)
    analyzed = _analyzed_count(session)
    assessed = len(context.interview_assessed_candidate_ids)
    finalists = len(context.finalist_candidate_ids or context.shortlisted_candidate_ids)
    documented = CompensationBudgetService().documented_count(session) if session is not None else 0

    decision_target = "Decision Board" if context.finalists_compared else "Comparison"

    if not include_journey_v2:
        return (
            SidebarItem("overview", "Overview", "Recruitment Overview", "Mission dashboard and recommended next action.", ":material/dashboard:", f"{analyzed}/{total}" if total else ""),
            SidebarItem("candidates", "Candidates", "Candidate Intelligence", "Review candidate fit, competencies and grounded evidence.", ":material/groups:", str(total) if total else ""),
            SidebarItem("interview", "Interview", "Interview Intelligence", "Prepare, conduct and complete structured assessments.", ":material/fact_check:", f"{assessed}/{total}" if total else ""),
            SidebarItem("decide", "Compare & decide", decision_target, "Compare finalists and record the human-owned decision.", ":material/compare_arrows:", str(finalists) if finalists else ""),
        )

    return (
        SidebarItem(
            "overview",
            "Overview",
            "Recruitment Overview",
            "Manage the mission, job inputs, candidate uploads and workflow status.",
            ":material/dashboard:",
            f"{analyzed}/{total}" if total else "",
        ),
        SidebarItem(
            "candidates",
            "Dashboard Perspective",
            "Dashboard Perspective",
            "Review the entire candidate pool before opening individual detail.",
            ":material/groups:",
            str(total) if total else "",
        ),
        SidebarItem(
            "budget",
            "Compensation & Budget",
            "Compensation & Budget",
            "Define the position budget and record candidate expectations before or after interview.",
            ":material/payments:",
            f"{documented}/{total}" if total else "",
        ),
        SidebarItem(
            "interview",
            "Interview & Assessment",
            "Interview Intelligence",
            "Prepare, conduct and complete structured assessments.",
            ":material/fact_check:",
            f"{assessed}/{total}" if total else "",
        ),
        SidebarItem(
            "decide",
            "Compare & decide",
            decision_target,
            "Compare finalists and record the human-owned decision.",
            ":material/compare_arrows:",
            "",
        ),
    )


def active_menu_key(page_label: str) -> str:
    return _PAGE_TO_MENU_KEY.get(page_label, "")


def _section_label(label: str) -> None:
    import streamlit as st

    st.sidebar.markdown(
        f'<div class="tc-sidebar-section">{escape(label)}</div>',
        unsafe_allow_html=True,
    )


def _nav_button(item: SidebarItem, *, active: bool) -> None:
    import streamlit as st

    # Compatibility marker retained for previous release contracts.
    label = f"{item.glyph}  {item.label}"
    display_label = item.label
    icon = item.glyph if item.glyph.startswith(":material/") else None
    if st.sidebar.button(
        display_label,
        icon=icon,
        key=f"premium_sidebar_{item.key}_{item.page_label}",
        type="primary" if active else "secondary",
        use_container_width=True,
        help=item.description,
    ):
        request_page(item.page_label, reason=f"Opened {item.label}.")
        st.rerun()


def render_premium_sidebar(session, *, current_page: str, app_version: str = "") -> None:
    import streamlit as st

    st.sidebar.markdown(
        brand_lockup_html(version="", compact=True),
        unsafe_allow_html=True,
    )

    home_item = SidebarItem(
        "home",
        "Home",
        "Executive Brief",
        "Return to the TalentCopilot home without clearing the active recruitment.",
        ":material/home:",
    )
    _nav_button(home_item, active=current_page == "Executive Brief")

    role = str(getattr(session, "role_title", "") or "No active recruitment")
    total = _candidate_count(session)
    analyzed = _analyzed_count(session)
    mission_status = (
        "Analysis complete"
        if total and analyzed >= total
        else "Analysis in progress"
        if total
        else "Start a recruitment mission"
    )
    meta = f" · {analyzed}/{total} candidates" if total else ""
    st.sidebar.markdown(
        f'''<div class="tc-mission-card">
        <div class="tc-mission-kicker">Active mission</div>
        <div class="tc-mission-role">{escape(role)}</div>
        <div class="tc-mission-meta">{escape(mission_status)}{escape(meta)}</div>
        </div>''',
        unsafe_allow_html=True,
    )

    _section_label("Recruitment")
    active_key = active_menu_key(current_page)
    for item in resolve_recruitment_destinations(
        session,
        current_page=current_page,
        include_journey_v2=True,
    ):
        _nav_button(item, active=item.key == active_key)

    _section_label("Other diagnostics")
    secondary = (
        SidebarItem("organization", "Organization", "Organization Intelligence", "Explore organizational and collaboration signals.", ":material/hub:"),
        SidebarItem("analytics", "Analytics", "Analytics Dashboard", "Open cross-recruitment analytics.", ":material/insights:"),
        SidebarItem("actions", "Action Center", "Action Center", "Track accountable follow-up across recruitment projects.", ":material/task_alt:"),
    )
    for item in secondary:
        _nav_button(item, active=item.page_label == current_page)

    with st.sidebar.expander("More", expanded=False):
        more = (
            SidebarItem("projects", "Projects", "Projects", "Open active and saved projects.", ":material/folder_open:"),
            SidebarItem("copilot", "Executive Copilot", "Executive Copilot", "Ask evidence-grounded executive questions.", ":material/auto_awesome:"),
        )
        for item in more:
            if st.button(
                item.label,
                icon=item.glyph if item.glyph.startswith(":material/") else None,
                key=f"premium_more_{item.key}",
                use_container_width=True,
                help=item.description,
            ):
                request_page(item.page_label, reason=f"Opened {item.label}.")
                st.rerun()

    # The historical "Next up" recommendation was removed from the sidebar.
    # Each page now exposes one contextual next action in the main workspace,
    # preventing competing recommendations across the shell and page content.
