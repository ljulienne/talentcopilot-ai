from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


DENSE_RADAR_THRESHOLD = 10


def _read_value(item: Any, attribute: str, default: Any = None) -> Any:
    if isinstance(item, Mapping):
        return item.get(attribute, default)
    return getattr(item, attribute, default)


def _percentage(value: Any) -> int:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0.0
    return int(round(max(0.0, min(100.0, number))))


def _level_percentage(value: Any) -> int:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0.0
    if number <= 5.0:
        number *= 20.0
    return _percentage(number)


def build_competency_star_data(
    competencies: Iterable[Any] | None,
    live_assessments: Iterable[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Prepare the role-aligned competency radar without changing scores.

    Matrix-aware inputs produce three distinct profiles:
    - role expectation from the job description;
    - immutable pre-interview AI estimate from CV evidence;
    - human post-interview assessment when evidence has been captured.

    Legacy InterviewCompetency inputs remain supported for compatibility.
    """

    selected = [
        item
        for item in list(competencies or [])
        if bool(_read_value(item, "is_active", True))
    ]

    live_lookup: dict[str, Mapping[str, Any]] = {}
    for assessment in live_assessments or []:
        name = str(assessment.get("competency", "") or "").strip()
        if name:
            live_lookup[name.casefold()] = assessment

    labels: list[str] = []
    required: list[int] = []
    pre_interview: list[int] = []
    post_interview: list[int] = []
    live_status: list[str] = []
    has_required_profile = False
    has_live_evidence = False

    for competency in selected:
        name = str(
            _read_value(
                competency,
                "competency_name",
                _read_value(
                    competency,
                    "name",
                    _read_value(competency, "competency", "Competency"),
                ),
            )
            or "Competency"
        ).strip()

        required_value = _read_value(competency, "required_level", None)
        if required_value is not None:
            has_required_profile = True
            required_score = _level_percentage(required_value)
        else:
            required_score = 0

        ai_value = _read_value(competency, "ai_estimated_level", None)
        if ai_value is not None:
            pre_score = _level_percentage(ai_value)
        else:
            pre_score = _percentage(_read_value(competency, "confidence", 0))

        labels.append(name)
        required.append(required_score)
        pre_interview.append(pre_score)

        assessment = live_lookup.get(name.casefold())
        if assessment is not None:
            answer = str(assessment.get("answer", "") or "").strip()
            notes = str(assessment.get("notes", "") or "").strip()
            confirmed = bool(assessment.get("evidence_confirmed", False))
            captured = bool(answer or notes or confirmed)
            if captured:
                has_live_evidence = True
                post_interview.append(_level_percentage(assessment.get("score", 0)))
                live_status.append("Confirmed" if confirmed else "Captured")
                continue

        interviewer_level = _read_value(competency, "interviewer_level", None)
        if interviewer_level is not None:
            has_live_evidence = True
            post_interview.append(_level_percentage(interviewer_level))
            validation_status = str(
                _read_value(competency, "validation_status", "Assessed") or "Assessed"
            )
            live_status.append(validation_status)
        else:
            post_interview.append(pre_score)
            live_status.append("Not assessed")

    return {
        "labels": labels,
        "required": required,
        "pre_interview": pre_interview,
        "post_interview": post_interview,
        # Backward-compatible keys used by the existing test suite.
        "live_interview": post_interview,
        "live_status": live_status,
        "has_required_profile": has_required_profile,
        "has_live_evidence": has_live_evidence,
        "has_post_interview": has_live_evidence,
        "displayed_count": len(labels),
        "is_dense": len(labels) > DENSE_RADAR_THRESHOLD,
        "interview_added_count": sum(
            1
            for item in selected
            if str(_read_value(item, "origin", "job_requirement")) == "interview_added"
        ),
    }


def _closed(values: list[Any]) -> list[Any]:
    return values + [values[0]] if values else []


def build_competency_star_figure(data: Mapping[str, Any]):
    import plotly.graph_objects as go

    labels = list(data.get("labels", []))
    figure = go.Figure()
    if not labels:
        return figure

    closed_labels = _closed(labels)
    required = list(data.get("required", []))
    pre_interview = list(data.get("pre_interview", []))
    post_interview = list(
        data.get("post_interview", data.get("live_interview", []))
    )
    live_status = list(data.get("live_status", []))

    if bool(data.get("has_required_profile", False)):
        figure.add_trace(
            go.Scatterpolar(
                r=_closed(required),
                theta=closed_labels,
                name="Role expectation",
                mode="lines+markers",
                fill=None,
                line={"width": 3, "dash": "dash"},
                marker={"size": 7},
                hovertemplate=(
                    "<b>%{theta}</b><br>Required level: %{r:.0f}/100<extra></extra>"
                ),
            )
        )

    figure.add_trace(
        go.Scatterpolar(
            r=_closed(pre_interview),
            theta=closed_labels,
            name="Pre-interview AI estimate",
            mode="lines+markers",
            fill="toself",
            opacity=0.50,
            line={"width": 2},
            marker={"size": 7},
            hovertemplate=(
                "<b>%{theta}</b><br>CV-based estimate: %{r:.0f}/100<extra></extra>"
            ),
        )
    )

    if bool(data.get("has_live_evidence", False)):
        figure.add_trace(
            go.Scatterpolar(
                r=_closed(post_interview),
                theta=closed_labels,
                customdata=_closed(live_status),
                name="Post-interview assessment",
                mode="lines+markers",
                fill="toself",
                opacity=0.42,
                line={"width": 3},
                marker={"size": 8},
                hovertemplate=(
                    "<b>%{theta}</b><br>Human assessment: %{r:.0f}/100"
                    "<br>Status: %{customdata}<extra></extra>"
                ),
            )
        )

    figure.update_layout(
        height=440,
        margin={"l": 55, "r": 55, "t": 75, "b": 45},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.08,
            "xanchor": "left",
            "x": 0,
        },
        polar={
            "bgcolor": "rgba(0,0,0,0)",
            "radialaxis": {
                "visible": True,
                "range": [0, 100],
                "tickvals": [0, 25, 50, 75, 100],
            },
        },
    )
    return figure


def render_competency_star(
    competencies: Iterable[Any] | None,
    *,
    live_assessments: Iterable[Mapping[str, Any]] | None = None,
    key: str | None = None,
) -> None:
    import streamlit as st

    data = build_competency_star_data(competencies, live_assessments)
    if len(data["labels"]) < 3:
        st.info("At least three competencies are required to display the Competency Radar.")
        return

    st.plotly_chart(
        build_competency_star_figure(data),
        use_container_width=True,
        config={"displayModeBar": False, "responsive": True},
        key=key,
    )

    if data["has_required_profile"] and data["has_live_evidence"]:
        st.caption(
            "Role expectations remain fixed. The CV-based estimate is preserved, "
            "while the post-interview profile reflects the evaluator's documented assessment."
        )
    elif data["has_required_profile"]:
        st.caption(
            "The role expectation comes from the job description. The candidate profile is "
            "an AI estimate based on CV evidence and must be validated during the interview."
        )
    elif data["has_live_evidence"]:
        st.caption(
            "The first profile represents pre-interview evidence confidence. The second "
            "represents recruiter ratings for captured interview evidence."
        )
    else:
        st.caption(
            "The initial profile represents pre-interview evidence confidence. A human "
            "assessment appears after interview evidence is captured."
        )

    if data.get("is_dense"):
        st.caption(
            f"This radar displays all {data['displayed_count']} active competencies, including "
            f"{data['interview_added_count']} added during the interview. Labels may be denser "
            "when the assessment contains more than ten axes."
        )

    st.caption(
        "Visual decision support only — this radar never recalculates the official fit score, "
        "official rank or canonical AI confidence."
    )
