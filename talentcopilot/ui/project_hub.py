from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from html import escape
from typing import Any, Iterable, Mapping, Sequence

from talentcopilot.models.recruitment_session import (
    CandidateAnalysisState,
    CandidateAnalysisStatus,
    RecruitmentSession,
    SessionStatus,
)
from talentcopilot.services.streamlit_session_bridge import (
    get_streamlit_session,
    set_streamlit_session,
)
from talentcopilot.storage.recruitment_store import list_recruitments, load_recruitment
from talentcopilot.ui.navigation_actions import request_page


@dataclass(frozen=True)
class ProjectSummary:
    project_id: str
    title: str
    project_type: str
    status: str
    candidate_count: int
    analyzed_count: int
    updated_at: str
    source: str
    is_active: bool = False

    @property
    def progress_percent(self) -> int:
        if self.candidate_count <= 0:
            return 0
        return max(0, min(100, round(self.analyzed_count / self.candidate_count * 100)))

    @property
    def next_action(self) -> str:
        if self.candidate_count <= 0:
            return "Add candidates"
        if self.analyzed_count < self.candidate_count:
            return "Continue analysis"
        return "Review decision"


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _display_date(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return "Not dated"
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return parsed.strftime("%d %b %Y · %H:%M")
    except ValueError:
        return text


def summary_from_session(session: Any | None) -> ProjectSummary | None:
    if session is None:
        return None
    candidate_count = _safe_int(getattr(session, "candidate_count", 0))
    analyzed_count = _safe_int(getattr(session, "analyzed_count", 0))
    status_value = getattr(session, "status", "Active")
    status = getattr(status_value, "value", status_value)
    return ProjectSummary(
        project_id=str(getattr(session, "session_id", "active-recruitment")),
        title=str(getattr(session, "role_title", "Active recruitment")),
        project_type="Recruitment",
        status=str(status or "Active"),
        candidate_count=candidate_count,
        analyzed_count=analyzed_count,
        updated_at=str(getattr(session, "updated_at", "")),
        source="session",
        is_active=True,
    )


def summary_from_stored(item: Mapping[str, Any]) -> ProjectSummary:
    candidate_count = _safe_int(item.get("candidate_count"))
    analyzed_count = _safe_int(item.get("analyzed_count"), candidate_count)
    status = str(item.get("status") or ("Decision ready" if candidate_count and analyzed_count >= candidate_count else "In progress"))
    return ProjectSummary(
        project_id=str(item.get("id") or "saved-recruitment"),
        title=str(item.get("title") or "Untitled recruitment"),
        project_type="Recruitment",
        status=status,
        candidate_count=candidate_count,
        analyzed_count=analyzed_count,
        updated_at=str(item.get("updated_at") or item.get("created_at") or ""),
        source="storage",
        is_active=False,
    )


def build_project_summaries(
    active_session: Any | None,
    stored_recruitments: Sequence[Mapping[str, Any]] | None,
) -> tuple[ProjectSummary, ...]:
    projects: list[ProjectSummary] = []
    active = summary_from_session(active_session)
    if active is not None:
        projects.append(active)

    active_id = active.project_id if active else None
    for item in stored_recruitments or ():
        saved = summary_from_stored(item)
        if active_id and saved.project_id == active_id:
            continue
        projects.append(saved)

    return tuple(
        sorted(
            projects,
            key=lambda project: (not project.is_active, project.updated_at),
            reverse=False,
        )
    )


def _candidate_name(result: Mapping[str, Any], index: int) -> str:
    candidate = result.get("candidate") or result.get("candidate_data") or result.get("profile") or {}
    if isinstance(candidate, Mapping):
        return str(candidate.get("name") or candidate.get("full_name") or result.get("candidate_name") or f"Candidate {index}")
    return str(result.get("candidate_name") or result.get("name") or f"Candidate {index}")


def _candidate_score(result: Mapping[str, Any]) -> float:
    match_result = result.get("match_result") or {}
    match_score = match_result.get("overall_score") if isinstance(match_result, Mapping) else None
    value = result.get("match_score") or result.get("score") or result.get("overall_score") or match_score or 0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def session_from_recruitment_data(data: Mapping[str, Any]) -> RecruitmentSession:
    context = data.get("recruitment_context") if isinstance(data.get("recruitment_context"), Mapping) else {}
    title = str(data.get("title") or context.get("title") or context.get("job_title") or "Untitled recruitment")
    job = dict(data.get("job") or {}) if isinstance(data.get("job"), Mapping) else {}
    job.setdefault("title", title)
    for key in ("company", "department", "location", "language"):
        if key not in job and context.get(key) is not None:
            job[key] = context.get(key)

    batch = data.get("analysis_batch") if isinstance(data.get("analysis_batch"), Mapping) else {}
    raw_results = batch.get("results") if isinstance(batch.get("results"), list) else []
    candidates: list[dict[str, Any]] = []
    analyses: list[CandidateAnalysisState] = []
    for index, raw_result in enumerate(raw_results, start=1):
        result = raw_result if isinstance(raw_result, Mapping) else {}
        candidate = result.get("candidate") or result.get("candidate_data") or result.get("profile") or {}
        candidate_dict = dict(candidate) if isinstance(candidate, Mapping) else {"name": _candidate_name(result, index)}
        candidate_dict.setdefault("name", _candidate_name(result, index))
        candidates.append(candidate_dict)
        analyses.append(
            CandidateAnalysisState(
                candidate_name=str(candidate_dict["name"]),
                status=CandidateAnalysisStatus.ANALYZED,
                match_score=_candidate_score(result),
                rank=_safe_int(result.get("rank"), index),
                notes=[str(result.get("recommendation"))] if result.get("recommendation") else [],
            )
        )

    status = SessionStatus.COMPLETED if candidates and len(analyses) == len(candidates) else SessionStatus.READY
    return RecruitmentSession(
        session_id=str(data.get("id") or "saved-recruitment"),
        job=job,
        candidates=candidates,
        status=status,
        analyses=analyses,
        created_at=str(data.get("created_at") or datetime.utcnow().isoformat()),
        updated_at=str(data.get("updated_at") or datetime.utcnow().isoformat()),
        metadata={"source": "project_hub", "stored_recruitment": dict(data)},
    )


def activate_recruitment_project(data: Mapping[str, Any]) -> RecruitmentSession:
    session = session_from_recruitment_data(data)
    set_streamlit_session(session)
    try:
        import streamlit as st

        st.session_state["recruitment_context"] = {
            "session_id": session.session_id,
            "title": session.role_title,
            "job_title": session.role_title,
            "candidate_count": session.candidate_count,
            "analyzed_count": session.analyzed_count,
            **{key: value for key, value in session.job.items() if key != "title"},
        }
        st.session_state["analysis_batch"] = data.get("analysis_batch") or {"success": True, "results": []}
        st.session_state["current_recruitment"] = session
    except Exception:
        pass
    return session


def _styles() -> None:
    import streamlit as st

    st.markdown(
        """
        <style>
        .tc-project-hero{padding:1.8rem 2rem;border-radius:24px;background:linear-gradient(135deg,#111827,#1e3a8a);color:#fff;margin-bottom:1.25rem}
        .tc-project-hero h1{margin:0 0 .45rem;font-size:2.35rem;letter-spacing:-.04em}.tc-project-hero p{margin:0;color:#dbeafe}
        .tc-project-card{padding:1.15rem 1.2rem;border:1px solid #e2e8f0;border-radius:18px;background:#fff;min-height:205px;box-shadow:0 8px 24px rgba(15,23,42,.05)}
        .tc-project-card h3{margin:.45rem 0 .35rem;color:#0f172a}.tc-project-card p{color:#64748b;font-size:.9rem;margin:.2rem 0}
        .tc-project-badge{display:inline-block;padding:.22rem .55rem;border-radius:999px;background:#dbeafe;color:#1d4ed8;font-size:.72rem;font-weight:800}
        .tc-project-active{background:#dcfce7;color:#166534}.tc-project-meta{margin-top:.75rem;padding-top:.65rem;border-top:1px solid #f1f5f9;color:#64748b;font-size:.8rem}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_project_card(project: ProjectSummary, index: int) -> None:
    import streamlit as st

    active_class = " tc-project-active" if project.is_active else ""
    badge = "Active" if project.is_active else project.status
    st.markdown(
        f"""
        <div class="tc-project-card">
          <span class="tc-project-badge{active_class}">{escape(badge)}</span>
          <h3>{escape(project.title)}</h3>
          <p>{escape(project.project_type)} project</p>
          <p><strong>{project.analyzed_count}/{project.candidate_count}</strong> candidates analysed · {project.progress_percent}% complete</p>
          <div class="tc-project-meta">Updated {escape(_display_date(project.updated_at))} · Next: {escape(project.next_action)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    label = "Continue project" if project.is_active else "Open project"
    if st.button(label, key=f"project_hub_open_{project.project_id}_{index}", use_container_width=True):
        if project.source == "storage":
            try:
                activate_recruitment_project(load_recruitment(project.project_id))
                st.success(f"{project.title} is now the active recruitment.")
            except Exception as exc:
                st.error("This saved project could not be opened.")
                st.caption(str(exc))
                return
        request_page("Recruitment Workspace", reason=f"Opened project: {project.title}")
        st.rerun()


def render_project_hub() -> None:
    import streamlit as st

    _styles()
    active_session = get_streamlit_session()
    try:
        stored = list_recruitments()
    except Exception as exc:
        stored = []
        st.warning("Saved projects could not be loaded.")
        st.caption(str(exc))

    projects = build_project_summaries(active_session, stored)
    st.markdown(
        """
        <div class="tc-project-hero">
          <h1>Projects</h1>
          <p>Resume active recruitments, reopen saved work and move directly to the next decision.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    total_candidates = sum(project.candidate_count for project in projects)
    decision_ready = sum(1 for project in projects if project.candidate_count > 0 and project.analyzed_count >= project.candidate_count)
    c1, c2, c3 = st.columns(3)
    c1.metric("Projects", len(projects), "Active and saved")
    c2.metric("Candidates", total_candidates, "Across recruitments")
    c3.metric("Decision ready", decision_ready, "Analysis completed")

    if not projects:
        st.info("No project is available yet. Start a recruitment from the Executive Brief.")
        if st.button("Return to Executive Brief", use_container_width=False):
            request_page("Executive Brief", reason="Start a new HR diagnostic.")
            st.rerun()
        return

    active_projects = [project for project in projects if project.is_active]
    saved_projects = [project for project in projects if not project.is_active]

    if active_projects:
        st.subheader("Active project")
        for index, project in enumerate(active_projects):
            _render_project_card(project, index)

    if saved_projects:
        st.subheader("Saved projects")
        for row_start in range(0, len(saved_projects), 3):
            row = saved_projects[row_start:row_start + 3]
            columns = st.columns(3)
            for offset, (column, project) in enumerate(zip(columns, row)):
                with column:
                    _render_project_card(project, row_start + offset + len(active_projects))


def render_projects() -> None:
    render_project_hub()
