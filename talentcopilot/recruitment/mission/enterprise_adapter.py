"""Adapter from RecruitmentMissionState to the generic Enterprise Workspace model.

Release 6.0B.3 keeps official recruitment data untouched. This module only
transforms presentation state into reusable workspace presentation objects.
"""

from __future__ import annotations

from typing import Callable, Mapping, Sequence

from talentcopilot.ui.design_system.v2.workspace import (
    EnterpriseWorkspaceModel,
    WorkspaceCard,
    WorkspaceMetric,
    WorkspaceSection,
    WorkspaceStatusStep,
)

from .state import RecruitmentMissionState


def _metric_value(value: object) -> str:
    return str(value if value is not None else "—")


def _confidence_value(state: RecruitmentMissionState) -> str:
    if state.average_confidence is None:
        return "—"
    return f"{state.average_confidence:.0f}%"


def _recommended_value(state: RecruitmentMissionState) -> str:
    return state.recommended_candidate if state.has_analysis else "Not available"


def _recommended_detail(state: RecruitmentMissionState) -> str:
    if not state.has_analysis:
        return "Awaiting analysis"
    return f"{state.recommended_score:.0f}% official match"


def _status_steps(state: RecruitmentMissionState) -> tuple[WorkspaceStatusStep, ...]:
    stages = (
        ("Mission setup", 10),
        ("Candidate intake", 30),
        ("Analysis in progress", 50),
        ("Analysis complete", 65),
        ("Decision preparation", 80),
    )
    current_index = 0
    for index, (_, threshold) in enumerate(stages):
        if state.progress_percent >= threshold:
            current_index = index

    return tuple(
        WorkspaceStatusStep(
            label=label,
            complete=index < current_index,
            current=index == current_index,
        )
        for index, (label, _) in enumerate(stages)
    )


def _insights(state: RecruitmentMissionState) -> tuple[WorkspaceCard, ...]:
    if not state.candidates:
        return (
            WorkspaceCard(
                eyebrow="Mission readiness",
                title="Candidate analysis not started",
                body=(
                    "Upload the job description and candidate documents to build "
                    "the official ranking and decision evidence."
                ),
                tone="info",
            ),
        )

    lead = state.candidates[0]
    cards = [
        WorkspaceCard(
            eyebrow="Leading candidate",
            title=f"#{lead.rank} {lead.name}",
            body=lead.rationale or lead.recommendation,
            footer=f"{lead.match_score:.0f}% official match",
            tone="positive",
        )
    ]

    if len(state.candidates) > 1:
        alternative = state.candidates[1]
        cards.append(
            WorkspaceCard(
                eyebrow="Closest alternative",
                title=f"#{alternative.rank} {alternative.name}",
                body=alternative.rationale or alternative.recommendation,
                footer=f"{alternative.match_score:.0f}% official match",
                tone="info",
            )
        )

    return tuple(cards)


def _recommendations(state: RecruitmentMissionState) -> tuple[WorkspaceCard, ...]:
    if not state.candidates:
        return ()

    lead = state.candidates[0]
    return (
        WorkspaceCard(
            eyebrow="Next decision step",
            title=lead.recommendation or "Review required",
            body=(
                "Review the ranking evidence, candidate reasoning and interview "
                "plan before recording the hiring decision."
            ),
            footer=f"Based on the official rank #{lead.rank}",
            tone="warning",
        ),
    )


def _evidence(state: RecruitmentMissionState) -> tuple[WorkspaceCard, ...]:
    if not state.candidates:
        return ()

    lead = state.candidates[0]
    evidence = []

    if lead.strengths:
        evidence.append(
            WorkspaceCard(
                eyebrow="Strength evidence",
                title="Lead candidate strengths",
                body=" · ".join(lead.strengths),
                tone="positive",
            )
        )

    if lead.risks:
        evidence.append(
            WorkspaceCard(
                eyebrow="Risk evidence",
                title="Items requiring validation",
                body=" · ".join(lead.risks),
                tone="risk",
            )
        )

    if not evidence:
        evidence.append(
            WorkspaceCard(
                eyebrow="Evidence status",
                title="Detailed evidence available in the mission sections",
                body=(
                    "Open Ranking, Reasoning, Comparison or Interview to inspect "
                    "the official supporting information."
                ),
                tone="neutral",
            )
        )

    return tuple(evidence)


def build_enterprise_workspace_model(
    state: RecruitmentMissionState,
    *,
    section_definitions: Sequence[object],
    renderers: Mapping[str, Callable[[RecruitmentMissionState], None]],
) -> EnterpriseWorkspaceModel:
    """Convert recruitment presentation state without recalculating official data."""
    if state is None:
        raise ValueError("A RecruitmentMissionState is required.")

    sections = []
    for definition in section_definitions:
        key = str(getattr(definition, "key"))
        renderer = renderers[key]

        def render_section(
            renderer: Callable[[RecruitmentMissionState], None] = renderer,
            state: RecruitmentMissionState = state,
        ) -> None:
            renderer(state)

        sections.append(
            WorkspaceSection(
                key=key,
                title=str(getattr(definition, "label")),
                question=str(getattr(definition, "question", "") or ""),
                description=(
                    "Official scores, ranks and evidence are read directly from "
                    "the active RecruitmentSession."
                ),
                expanded=key == "ranking",
                renderer=render_section,
            )
        )

    return EnterpriseWorkspaceModel(
        title=state.role_title,
        eyebrow="Recruitment mission",
        subtitle=(
            f"{state.stage} · {state.candidate_count} candidates · "
            f"Session {state.session_id}"
        ),
        status=state.status,
        readiness=state.progress_percent,
        summary=state.summary,
        metrics=(
            WorkspaceMetric(
                "Candidates",
                _metric_value(state.candidate_count),
                f"{state.analyzed_count} analysed",
            ),
            WorkspaceMetric(
                "Recommended",
                _recommended_value(state),
                _recommended_detail(state),
            ),
            WorkspaceMetric(
                "AI confidence",
                _confidence_value(state),
                "Official confidence",
            ),
            WorkspaceMetric(
                "Mission status",
                state.status,
                state.stage,
            ),
        ),
        steps=_status_steps(state),
        insights=_insights(state),
        recommendations=_recommendations(state),
        evidence=_evidence(state),
        sections=tuple(sections),
    )


__all__ = ["build_enterprise_workspace_model"]
