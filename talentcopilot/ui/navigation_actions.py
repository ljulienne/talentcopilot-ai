from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NavigationRequest:
    page_label: str
    reason: str = ""


ENGINE_PAGE_MAP: dict[str, str] = {
    "Knowledge": "Organization Intelligence",
    "Organization Graph": "Organization Intelligence",
    "Collaboration": "Organization Intelligence",
    "Skills": "Organization Intelligence",
    "Workforce": "Organization Intelligence",
    "Recruitment": "Recruitment Workspace",
    "Hiring": "Recruitment Workspace",
    "Interview": "Interview Workspace",
    "Decision": "Decision Board",
    "Reporting": "Executive Reporting",
}


def page_for_engine(engine: str) -> str:
    """Return the workspace associated with an intelligence engine."""
    normalized = (engine or '').strip().lower()

    mappings = {
        "skills": "Organization Intelligence",
        "skills intelligence": "Organization Intelligence",
        "workforce": "Organization Intelligence",
        "workforce intelligence": "Organization Intelligence",
        "collaboration": "Organization Intelligence",
        "collaboration intelligence": "Organization Intelligence",
        "knowledge": "Organization Intelligence",
        "knowledge concentration": "Organization Intelligence",
        "organization graph": "Organization Intelligence",
        "matching": "Recruitment Workspace",
        "recruitment": "Recruitment Workspace",
        "candidate": "Candidate Workspace",
        "decision": "Decision Board",
        "decision queue": "Decision Board",
        "executive reasoning": "Executive Reporting",
        "executive": "Executive Reporting",
    }

    return mappings.get(normalized, "Organization Intelligence")
def request_page(page_label: str, *, reason: str = "") -> None:
    """Queue a page change for the Streamlit shell on the next rerun."""
    import streamlit as st

    st.session_state["enterprise_navigation_request"] = NavigationRequest(
        page_label=page_label,
        reason=reason,
    )


def consume_page_request() -> NavigationRequest | None:
    """Consume a pending page request from Streamlit state."""
    import streamlit as st

    request = st.session_state.pop("enterprise_navigation_request", None)
    if isinstance(request, NavigationRequest):
        return request
    if isinstance(request, dict) and request.get("page_label"):
        return NavigationRequest(
            page_label=str(request["page_label"]),
            reason=str(request.get("reason", "")),
        )
    return None
