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


def page_for_engine(source_engine: str) -> str:
    """Return the most relevant visible workspace for an intelligence source."""
    return ENGINE_PAGE_MAP.get(source_engine, "Organization Intelligence")


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
