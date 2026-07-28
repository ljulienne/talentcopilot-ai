from __future__ import annotations

from html import escape
from typing import Iterable

from talentcopilot.services.recruitment_overview_service import (
    CandidateOverview,
    RecruitmentOverview,
    RecruitmentOverviewService,
)
from talentcopilot.services.recruitment_workflow_state import (
    get_workflow_context,
    select_workflow_candidate,
)
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session
from talentcopilot.ui.design_system.components import enterprise_hero, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme
from talentcopilot.ui.navigation_actions import request_page


MODE_OFFICIAL = "Official role fit"
MODE_PRE = "Pre-interview competencies"
MODE_POST = "Post-interview competencies"


def _plotly_layout(fig, *, height: int, margin: dict | None = None):
    fig.update_layout(
        height=height,
        margin=margin or dict(l=20, r=20, t=42, b=28),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial, sans-serif", size=12, color="#334155"),
        hoverlabel=dict(bgcolor="#0F172A", font_color="#FFFFFF"),
        showlegend=False,
    )
    return fig


def _metric_for(candidate: CandidateOverview, mode: str) -> float | None:
    if mode == MODE_OFFICIAL:
        return candidate.official_match_score
    if mode == MODE_POST:
        return (
            candidate.post_interview_alignment
            if candidate.post_interview_alignment is not None
            else candidate.pre_interview_alignment
        )
    return candidate.pre_interview_alignment


def _metric_label(mode: str) -> str:
    if mode == MODE_OFFICIAL:
        return "Official role fit"
    if mode == MODE_POST:
        return "Current post-interview competency alignment"
    return "Pre-interview competency alignment"


def _ranking_chart(view: RecruitmentOverview, mode: str):
    import plotly.graph_objects as go

    values = []
    for item in view.candidates[:10]:
        metric = _metric_for(item, mode)
        if metric is not None:
            values.append((item, float(metric)))

    values.sort(key=lambda pair: (pair[1], -pair[0].official_rank), reverse=True)
    names = [f"#{item.official_rank} {item.candidate_name}" for item, _ in values][::-1]
    scores = [score for _, score in values][::-1]
    hover = []
    for item, score in values[::-1]:
        detail = [f"{_metric_label(mode)}: {score:.0f}%", f"Official fit: {item.official_match_score:.0f}%"]
        if item.confidence_score is not None:
            detail.append(f"Confidence: {item.confidence_score:.0f}%")
        detail.append(f"Interview: {item.interview_status}")
        hover.append("<br>".join(detail))

    fig = go.Figure(
        go.Bar(
            x=scores,
            y=names,
            orientation="h",
            text=[f"{score:.0f}%" for score in scores],
            textposition="outside",
            cliponaxis=False,
            marker=dict(color="#4F46E5", line=dict(width=0)),
            hovertext=hover,
            hovertemplate="%{hovertext}<extra></extra>",
        )
    )
    fig.update_xaxes(range=[0, 108], ticksuffix="%", gridcolor="#E2E8F0", zeroline=False)
    fig.update_yaxes(title=None, automargin=True)
    fig.update_layout(title=dict(text=_metric_label(mode), x=0.0, font=dict(size=15)))
    return _plotly_layout(fig, height=max(300, 54 * max(4, len(values))))


def _fit_distribution_chart(view: RecruitmentOverview):
    import plotly.graph_objects as go

    labels = ["Strong", "Potential", "Partial", "Low"]
    values = [
        view.strong_fit_count,
        view.potential_fit_count,
        view.partial_fit_count,
        view.low_fit_count,
    ]
    colors = ["#16A34A", "#4F46E5", "#F59E0B", "#DC2626"]
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.62,
            marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
            textinfo="label+value",
            hovertemplate="%{label}: %{value} candidate(s)<extra></extra>",
        )
    )
    fig.add_annotation(
        text=f"<b>{view.analyzed_count}</b><br>analysed",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=15, color="#0F172A"),
    )
    fig.update_layout(title=dict(text="Talent-pool distribution", x=0.0, font=dict(size=15)), showlegend=False)
    return _plotly_layout(fig, height=330, margin=dict(l=8, r=8, t=48, b=8))


def _heatmap(view: RecruitmentOverview, mode: str):
    import plotly.graph_objects as go

    candidates = list(view.candidates[:6])
    competency_names: list[str] = []
    for candidate in candidates:
        source = candidate.competency_scores_post if mode == MODE_POST and candidate.competency_scores_post else candidate.competency_scores_pre
        for name, _ in source:
            if name not in competency_names:
                competency_names.append(name)
    competency_names = competency_names[:9]

    z = []
    hover = []
    for candidate in candidates:
        pre = dict(candidate.competency_scores_pre)
        post = dict(candidate.competency_scores_post)
        row = []
        row_hover = []
        for competency in competency_names:
            value = post.get(competency) if mode == MODE_POST and post else pre.get(competency)
            if value is None:
                value = pre.get(competency)
            row.append(value if value is not None else 0)
            row_hover.append(
                f"{candidate.candidate_name}<br>{competency}<br>Alignment: {float(value or 0):.0f}%"
            )
        z.append(row)
        hover.append(row_hover)

    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=competency_names,
            y=[candidate.candidate_name for candidate in candidates],
            zmin=0,
            zmax=100,
            colorscale=[
                [0.0, "#FEE2E2"],
                [0.45, "#FEF3C7"],
                [0.72, "#DBEAFE"],
                [1.0, "#DCFCE7"],
            ],
            colorbar=dict(title="Alignment", ticksuffix="%", thickness=12),
            text=[[f"{float(value):.0f}%" for value in row] for row in z],
            texttemplate="%{text}",
            hovertext=hover,
            hovertemplate="%{hovertext}<extra></extra>",
        )
    )
    fig.update_xaxes(side="top", tickangle=-25, automargin=True)
    fig.update_yaxes(autorange="reversed", automargin=True)
    title = "Competency coverage — post-interview" if mode == MODE_POST else "Competency coverage — pre-interview"
    fig.update_layout(title=dict(text=title, x=0.0, font=dict(size=15)))
    return _plotly_layout(fig, height=max(340, 62 * max(4, len(candidates))), margin=dict(l=20, r=20, t=105, b=25))


def _competency_coverage_chart(view: RecruitmentOverview, mode: str):
    import plotly.graph_objects as go

    items = list(view.competency_coverage[:8])
    labels = [item.competency for item in items][::-1]
    if mode == MODE_POST:
        values = [
            item.post_interview_coverage
            if item.post_interview_coverage is not None
            else item.pre_interview_coverage
            for item in items
        ][::-1]
    else:
        values = [item.pre_interview_coverage for item in items][::-1]

    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            text=[f"{value}%" for value in values],
            textposition="outside",
            cliponaxis=False,
            marker=dict(color="#0EA5E9"),
            hovertemplate="%{y}: %{x}% of candidates meet the expected level<extra></extra>",
        )
    )
    fig.update_xaxes(range=[0, 108], ticksuffix="%", gridcolor="#E2E8F0", zeroline=False)
    fig.update_yaxes(automargin=True)
    fig.update_layout(title=dict(text="Role requirements covered by the pool", x=0.0, font=dict(size=15)))
    return _plotly_layout(fig, height=max(320, 48 * max(5, len(items))))


def _interview_progress_chart(view: RecruitmentOverview):
    import plotly.graph_objects as go

    candidates = list(view.candidates[:8])[::-1]
    values = [candidate.interview_progress for candidate in candidates]
    colors = [
        "#16A34A" if candidate.interview_status == "Completed" else "#F59E0B" if candidate.interview_status == "In progress" else "#CBD5E1"
        for candidate in candidates
    ]
    fig = go.Figure(
        go.Bar(
            x=values,
            y=[candidate.candidate_name for candidate in candidates],
            orientation="h",
            text=[f"{value}%" for value in values],
            textposition="outside",
            cliponaxis=False,
            marker=dict(color=colors),
            customdata=[candidate.interview_status for candidate in candidates],
            hovertemplate="%{y}<br>Assessment completion: %{x}%<br>Status: %{customdata}<extra></extra>",
        )
    )
    fig.update_xaxes(range=[0, 108], ticksuffix="%", gridcolor="#E2E8F0", zeroline=False)
    fig.update_yaxes(automargin=True)
    fig.update_layout(title=dict(text="Interview assessment progress", x=0.0, font=dict(size=15)))
    return _plotly_layout(fig, height=max(320, 48 * max(5, len(candidates))))


def _next_action(view: RecruitmentOverview) -> None:
    import streamlit as st

    st.markdown(
        f"""
        <div style="border:1px solid #C7D2FE;background:#EEF2FF;border-radius:18px;padding:1rem 1.1rem;margin:.75rem 0 1rem">
          <div style="font-size:.72rem;font-weight:850;letter-spacing:.08em;text-transform:uppercase;color:#4338CA">Recommended next action</div>
          <div style="font-size:1.05rem;font-weight:820;color:#0F172A;margin:.24rem 0">{escape(view.next_action_title)}</div>
          <div style="font-size:.86rem;color:#475569;line-height:1.45">{escape(view.next_action_detail)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button(
        view.next_action_button + " →",
        type="primary",
        key="recruitment_overview_next_action",
        use_container_width=True,
        help="TalentCopilot recommends this action from the current workflow state.",
    ):
        request_page(view.next_action_page, reason=view.next_action_title)
        st.rerun()


def _candidate_shortcut(view: RecruitmentOverview) -> None:
    import streamlit as st

    if not view.candidates:
        return
    options = {candidate.candidate_id: candidate for candidate in view.candidates}
    candidate_id = st.selectbox(
        "Open a candidate",
        list(options),
        format_func=lambda key: (
            f"#{options[key].official_rank} · {options[key].candidate_name} · "
            f"{options[key].official_match_score:.0f}% official fit"
        ),
        key="recruitment_overview_candidate",
        help="The selected candidate will remain active across Candidate and Interview Intelligence.",
    )
    if st.button(
        "Open Candidate Intelligence",
        key="recruitment_overview_open_candidate",
        use_container_width=True,
    ):
        candidate = options[candidate_id]
        select_workflow_candidate(candidate.candidate_id, candidate.candidate_name)
        request_page("Candidate Intelligence", reason=f"Reviewing {candidate.candidate_name} from the visual overview.")
        st.rerun()


def render_recruitment_overview() -> None:
    import streamlit as st

    apply_enterprise_theme()
    session = get_streamlit_session()

    enterprise_hero(
        "Recruitment Overview",
        "See the candidate pool, competency coverage and interview progress before opening the detailed evidence.",
        "Visual Recruitment Command Center",
    )

    if session is None:
        st.info("Create or reopen a recruitment mission before opening the visual overview.")
        if st.button("Open Recruitment Workspace", type="primary", key="overview_empty_open_workspace"):
            request_page("Recruitment Workspace", reason="Create or reopen a recruitment mission.")
            st.rerun()
        return

    workflow_context = get_workflow_context(session, current_page="Recruitment Overview")
    view = RecruitmentOverviewService().build(session, workflow_context)

    if not view.has_analysis:
        st.info("The visual dashboard becomes available after candidate analysis.")
        if st.button("Continue candidate analysis", type="primary", key="overview_continue_analysis"):
            request_page("Recruitment Workspace", reason="Complete the candidate analysis first.")
            st.rerun()
        return

    metric_grid([
        ("Candidates analysed", str(view.analyzed_count), f"{view.candidate_count} in the mission"),
        ("Strong / potential fit", str(view.strong_fit_count + view.potential_fit_count), "Official role-fit bands"),
        ("Interviews completed", str(view.interview_completed_count), f"{view.interview_in_progress_count} in progress"),
        ("Ready for comparison", str(view.ready_for_decision_count), "At least 80% of role competencies assessed"),
    ])

    available_modes = [MODE_OFFICIAL, MODE_PRE]
    if view.has_post_interview_data:
        available_modes.append(MODE_POST)
    mode = st.radio(
        "Dashboard perspective",
        available_modes,
        horizontal=True,
        key="recruitment_overview_mode",
        help=(
            "Official role fit is the immutable CV-to-role score. Competency alignment is a separate "
            "visual indicator based on role-required levels and does not replace the official ranking."
        ),
    )

    if mode != MODE_OFFICIAL:
        st.caption(
            "Competency alignment is an advisory visual indicator. It does not recalculate the official match score or rank."
        )
    if mode == MODE_POST:
        st.info(
            "Post-interview visuals use saved interviewer levels where available and retain the pre-interview estimate for competencies not yet assessed."
        )

    rank_col, distribution_col = st.columns([1.7, 1])
    with rank_col:
        st.plotly_chart(_ranking_chart(view, mode), use_container_width=True, config={"displayModeBar": False})
    with distribution_col:
        st.plotly_chart(_fit_distribution_chart(view), use_container_width=True, config={"displayModeBar": False})

    competency_mode = MODE_POST if mode == MODE_POST else MODE_PRE
    st.plotly_chart(_heatmap(view, competency_mode), use_container_width=True, config={"displayModeBar": False})

    coverage_col, interview_col = st.columns(2)
    with coverage_col:
        st.plotly_chart(
            _competency_coverage_chart(view, competency_mode),
            use_container_width=True,
            config={"displayModeBar": False},
        )
    with interview_col:
        st.plotly_chart(_interview_progress_chart(view), use_container_width=True, config={"displayModeBar": False})

    guidance_col, shortcut_col = st.columns([1.25, 0.75])
    with guidance_col:
        _next_action(view)
    with shortcut_col:
        section_title("Open the detail", "Keep the dashboard compact and drill down only when needed.")
        _candidate_shortcut(view)

    with st.expander("How to read these indicators", expanded=False):
        st.markdown(
            "- **Official role fit** is the canonical score and ranking already stored in the recruitment session.\n"
            "- **Competency alignment** compares estimated or assessed levels with the levels expected in the job description.\n"
            "- **Pool coverage** shows the share of candidates meeting each role requirement.\n"
            "- **Interview progress** shows how much of the role-aligned competency assessment has been completed."
        )


__all__ = ["render_recruitment_overview"]
