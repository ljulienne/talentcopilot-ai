from __future__ import annotations

from dataclasses import dataclass
from html import escape
from typing import Any

from talentcopilot.services.recruitment_workflow_state import select_workflow_candidate
from talentcopilot.ui.enterprise_navigation import get_enterprise_navigation
from talentcopilot.ui.navigation_actions import request_page


@dataclass(frozen=True)
class ShellSearchResult:
    label: str
    detail: str
    page_label: str
    candidate_id: str = ""
    candidate_name: str = ""


def _candidate_rows(session: Any) -> tuple[tuple[str, str, float, int], ...]:
    if session is None:
        return ()

    rows: list[tuple[str, str, float, int]] = []
    analyses = list(getattr(session, "ranked_analyses", ()) or ())
    for item in analyses:
        candidate_id = str(getattr(item, "candidate_id", "") or "")
        candidate_name = str(
            getattr(item, "candidate_name", "")
            or getattr(item, "name", "")
            or candidate_id
            or "Candidate"
        )
        score = float(
            getattr(item, "official_score", None)
            or getattr(item, "match_score", None)
            or getattr(item, "score", 0.0)
            or 0.0
        )
        rank = int(
            getattr(item, "official_rank", None)
            or getattr(item, "mission_rank", None)
            or getattr(item, "rank", 0)
            or 0
        )
        rows.append((candidate_id or candidate_name, candidate_name, score, rank))
    return tuple(rows)


def build_shell_search_results(
    session: Any,
    query: str,
    *,
    limit: int = 8,
) -> tuple[ShellSearchResult, ...]:
    normalized = " ".join(str(query or "").casefold().split())
    if len(normalized) < 2:
        return ()

    results: list[ShellSearchResult] = []
    seen_pages: set[str] = set()

    for section in get_enterprise_navigation().values():
        for page in section.pages:
            haystack = f"{page.label} {section.label}".casefold()
            if normalized in haystack and page.label not in seen_pages:
                results.append(
                    ShellSearchResult(
                        label=page.label,
                        detail=f"Open {section.label}",
                        page_label=page.label,
                    )
                )
                seen_pages.add(page.label)

    for candidate_id, name, score, rank in _candidate_rows(session):
        if normalized not in name.casefold():
            continue
        rank_label = f"Official rank #{rank}" if rank else "Candidate profile"
        results.append(
            ShellSearchResult(
                label=name,
                detail=f"{rank_label} · {score:.0f}% Talent Fit",
                page_label="Candidate Intelligence",
                candidate_id=candidate_id,
                candidate_name=name,
            )
        )

    return tuple(results[: max(1, int(limit))])


def _mission_summary(session: Any) -> tuple[str, str, str]:
    if session is None:
        return "No active mission", "Start with a recruitment diagnostic", "idle"

    role = str(getattr(session, "role_title", "") or "Active recruitment")
    total = int(getattr(session, "candidate_count", 0) or 0)
    analyzed = int(getattr(session, "analyzed_count", 0) or 0)
    if total and analyzed >= total:
        return role, f"{analyzed}/{total} candidates analysed", "ready"
    if total:
        return role, f"{analyzed}/{total} candidates analysed", "progress"
    return role, "Add candidate CVs to continue", "idle"


def render_product_topbar(session: Any, *, current_page: str) -> None:
    """Render the shared product top bar with functional search and help.

    The component remains presentation-only. Search navigates to existing pages
    and candidate detail while preserving the canonical workflow candidate.
    """

    import streamlit as st

    role, mission_meta, tone = _mission_summary(session)

    with st.container(border=True):
        st.markdown('<span class="tc-product-topbar-marker"></span>', unsafe_allow_html=True)
        title_col, search_col, context_col = st.columns([1.35, 1.15, 1.0], vertical_alignment="center")

        with title_col:
            st.markdown(
                f'<div class="tc-topbar-breadcrumb">TalentCopilot <span>›</span> {escape(current_page)}</div>'
                f'<div class="tc-topbar-page">{escape(current_page)}</div>',
                unsafe_allow_html=True,
            )

        with search_col:
            with st.popover("Search", icon=":material/search:", use_container_width=True):
                query = st.text_input(
                    "Search pages or candidates",
                    placeholder="Search candidates, missions or pages…",
                    key="tc_global_search_query",
                )
                results = build_shell_search_results(session, query)
                if query and not results:
                    st.caption("No matching page or candidate.")
                for index, result in enumerate(results):
                    if st.button(
                        result.label,
                        key=f"tc_global_search_result_{index}_{result.page_label}",
                        help=result.detail,
                        use_container_width=True,
                    ):
                        if result.candidate_id:
                            select_workflow_candidate(
                                result.candidate_id,
                                result.candidate_name,
                            )
                        request_page(
                            result.page_label,
                            reason=f"Opened {result.label} from global search.",
                        )
                        st.rerun()
                    st.caption(result.detail)

        with context_col:
            st.markdown(
                f'<div class="tc-topbar-mission tc-topbar-{escape(tone)}">'
                f'<span class="tc-topbar-status-dot"></span>'
                f'<div><div class="tc-topbar-mission-title">{escape(role)}</div>'
                f'<div class="tc-topbar-mission-meta">{escape(mission_meta)}</div></div></div>',
                unsafe_allow_html=True,
            )
            if st.button(
                "AI Copilot",
                icon=":material/auto_awesome:",
                key="tc_topbar_copilot",
                help="Open the evidence-grounded Executive Copilot.",
                use_container_width=True,
            ):
                request_page("Executive Copilot", reason="Opened Executive Copilot from the product shell.")
                st.rerun()


__all__ = [
    "ShellSearchResult",
    "build_shell_search_results",
    "render_product_topbar",
]
