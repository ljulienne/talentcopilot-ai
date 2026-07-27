from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


MAX_COMPETENCIES = 7


def _read_value(
    item: Any,
    attribute: str,
    default: Any = None,
) -> Any:
    if isinstance(item, Mapping):
        return item.get(attribute, default)

    return getattr(item, attribute, default)


def _percentage(value: Any) -> int:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0.0

    return int(
        round(
            max(
                0.0,
                min(100.0, number),
            )
        )
    )


def build_competency_star_data(
    competencies: Iterable[Any] | None,
    live_assessments: Iterable[
        Mapping[str, Any]
    ] | None = None,
) -> dict[str, Any]:
    """
    Prepare visual-only competency data.

    This component does not calculate or modify:
    - official candidate match score;
    - official candidate rank;
    - canonical AI confidence;
    - hiring recommendation.
    """

    selected = list(
        competencies or []
    )[:MAX_COMPETENCIES]

    live_lookup = {}

    for assessment in live_assessments or []:
        name = str(
            assessment.get(
                "competency",
                "",
            )
            or ""
        ).strip()

        if name:
            live_lookup[
                name.casefold()
            ] = assessment

    labels = []
    pre_interview = []
    live_interview = []
    live_status = []

    has_live_evidence = False

    for competency in selected:
        name = str(
            _read_value(
                competency,
                "name",
                _read_value(
                    competency,
                    "competency",
                    "Competency",
                ),
            )
            or "Competency"
        ).strip()

        confidence = _percentage(
            _read_value(
                competency,
                "confidence",
                0,
            )
        )

        labels.append(name)
        pre_interview.append(confidence)

        assessment = live_lookup.get(
            name.casefold()
        )

        if assessment is None:
            live_interview.append(confidence)
            live_status.append("Not assessed")
            continue

        answer = str(
            assessment.get(
                "answer",
                "",
            )
            or ""
        ).strip()

        notes = str(
            assessment.get(
                "notes",
                "",
            )
            or ""
        ).strip()

        confirmed = bool(
            assessment.get(
                "evidence_confirmed",
                False,
            )
        )

        evidence_captured = bool(
            answer
            or notes
            or confirmed
        )

        if not evidence_captured:
            live_interview.append(confidence)
            live_status.append("Not assessed")
            continue

        has_live_evidence = True

        try:
            recruiter_score = float(
                assessment.get(
                    "score",
                    0,
                )
                or 0
            )
        except (TypeError, ValueError):
            recruiter_score = 0.0

        live_interview.append(
            _percentage(
                recruiter_score * 20
            )
        )

        live_status.append(
            "Confirmed"
            if confirmed
            else "Captured"
        )

    return {
        "labels": labels,
        "pre_interview": pre_interview,
        "live_interview": live_interview,
        "live_status": live_status,
        "has_live_evidence": has_live_evidence,
    }


def build_competency_star_figure(
    data: Mapping[str, Any],
):
    import plotly.graph_objects as go

    labels = list(
        data.get("labels", [])
    )

    pre_interview = list(
        data.get(
            "pre_interview",
            [],
        )
    )

    live_interview = list(
        data.get(
            "live_interview",
            [],
        )
    )

    live_status = list(
        data.get(
            "live_status",
            [],
        )
    )

    has_live_evidence = bool(
        data.get(
            "has_live_evidence",
            False,
        )
    )

    figure = go.Figure()

    if not labels:
        return figure

    closed_labels = labels + [labels[0]]
    closed_pre = (
        pre_interview
        + [pre_interview[0]]
    )

    figure.add_trace(
        go.Scatterpolar(
            r=closed_pre,
            theta=closed_labels,
            name="Pre-interview evidence",
            mode="lines+markers",
            fill="toself",
            opacity=0.55,
            line={"width": 2},
            marker={"size": 7},
            hovertemplate=(
                "<b>%{theta}</b>"
                "<br>Evidence confidence: "
                "%{r:.0f}/100"
                "<extra></extra>"
            ),
        )
    )

    if has_live_evidence:
        closed_live = (
            live_interview
            + [live_interview[0]]
        )

        closed_status = (
            live_status
            + [live_status[0]]
        )

        figure.add_trace(
            go.Scatterpolar(
                r=closed_live,
                theta=closed_labels,
                customdata=closed_status,
                name="Live recruiter assessment",
                mode="lines+markers",
                fill="toself",
                opacity=0.45,
                line={"width": 3},
                marker={"size": 8},
                hovertemplate=(
                    "<b>%{theta}</b>"
                    "<br>Recruiter assessment: "
                    "%{r:.0f}/100"
                    "<br>Evidence: %{customdata}"
                    "<extra></extra>"
                ),
            )
        )

    figure.update_layout(
        height=440,
        margin={
            "l": 55,
            "r": 55,
            "t": 75,
            "b": 45,
        },
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
                "tickvals": [
                    0,
                    25,
                    50,
                    75,
                    100,
                ],
            },
        },
    )

    return figure


def render_competency_star(
    competencies: Iterable[Any] | None,
    *,
    live_assessments: Iterable[
        Mapping[str, Any]
    ] | None = None,
    key: str | None = None,
) -> None:
    import streamlit as st

    data = build_competency_star_data(
        competencies,
        live_assessments,
    )

    if len(data["labels"]) < 3:
        st.info(
            "At least three competencies are "
            "required to display the Competency Star."
        )
        return

    figure = build_competency_star_figure(
        data
    )

    st.plotly_chart(
        figure,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "responsive": True,
        },
        key=key,
    )

    if data["has_live_evidence"]:
        st.caption(
            "The first profile represents "
            "pre-interview evidence confidence. "
            "The second represents recruiter ratings "
            "for captured interview evidence."
        )
    else:
        st.caption(
            "The initial star represents "
            "pre-interview evidence confidence. "
            "A live recruiter profile appears after "
            "an answer, note or evidence confirmation "
            "is captured."
        )

    st.caption(
        "Visual decision support only — "
        "this chart does not recalculate the "
        "official fit score, official rank "
        "or canonical AI confidence."
    )
