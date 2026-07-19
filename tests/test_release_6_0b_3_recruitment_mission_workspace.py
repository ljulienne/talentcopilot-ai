from __future__ import annotations

from dataclasses import dataclass

from talentcopilot.recruitment.mission.enterprise_adapter import (
    build_enterprise_workspace_model,
)
from talentcopilot.recruitment.mission.state import (
    CandidateMissionView,
    RecruitmentMissionState,
)


@dataclass(frozen=True)
class SectionDefinition:
    key: str
    label: str
    question: str


def _state() -> RecruitmentMissionState:
    return RecruitmentMissionState(
        session_id="session-123",
        role_title="Senior Sales Manager APAC",
        status="active",
        candidate_count=2,
        analyzed_count=2,
        progress_percent=80,
        stage="Decision preparation",
        candidates=(
            CandidateMissionView(
                candidate_id="candidate-a",
                name="Candidate A",
                rank=1,
                match_score=86.0,
                decision_score=82.0,
                confidence_score=90.0,
                recommendation="Proceed to structured interview",
                rationale="Strong APAC sales leadership evidence.",
                strengths=("APAC leadership", "Textile sector"),
                risks=("Validate Vietnam market depth",),
            ),
            CandidateMissionView(
                candidate_id="candidate-b",
                name="Candidate B",
                rank=2,
                match_score=74.0,
                decision_score=70.0,
                confidence_score=84.0,
                recommendation="Keep as alternative",
                rationale="Solid regional commercial background.",
                strengths=("Regional sales",),
                risks=(),
            ),
        ),
        recommended_candidate="Candidate A",
        recommended_score=86.0,
        average_confidence=87.0,
        summary="Candidate A leads with an official match of 86%.",
    )


def test_adapter_preserves_official_scores_and_ranking() -> None:
    state = _state()
    calls = []

    def render_ranking(received_state):
        calls.append(received_state)

    model = build_enterprise_workspace_model(
        state,
        section_definitions=(
            SectionDefinition("ranking", "Ranking", "Who leads?"),
        ),
        renderers={"ranking": render_ranking},
    )

    assert model.title == state.role_title
    assert model.readiness == state.progress_percent
    assert model.metrics[1].value == state.recommended_candidate
    assert model.metrics[1].detail == "86% official match"
    assert model.insights[0].title == "#1 Candidate A"
    assert model.insights[0].footer == "86% official match"

    model.sections[0].renderer()
    assert calls == [state]


def test_adapter_builds_all_sections_without_late_binding_bug() -> None:
    state = _state()
    calls = []

    definitions = (
        SectionDefinition("overview", "Overview", "What is the status?"),
        SectionDefinition("ranking", "Ranking", "Who leads?"),
    )

    renderers = {
        "overview": lambda received: calls.append(("overview", received)),
        "ranking": lambda received: calls.append(("ranking", received)),
    }

    model = build_enterprise_workspace_model(
        state,
        section_definitions=definitions,
        renderers=renderers,
    )

    assert [section.key for section in model.sections] == ["overview", "ranking"]
    assert model.sections[0].expanded is False
    assert model.sections[1].expanded is True

    model.sections[0].renderer()
    model.sections[1].renderer()

    assert calls == [("overview", state), ("ranking", state)]


def test_adapter_does_not_mutate_recruitment_state() -> None:
    state = _state()
    before = state

    build_enterprise_workspace_model(
        state,
        section_definitions=(
            SectionDefinition("ranking", "Ranking", "Who leads?"),
        ),
        renderers={"ranking": lambda received: None},
    )

    assert state == before
    assert state.candidates[0].rank == 1
    assert state.candidates[0].match_score == 86.0


def test_empty_mission_has_safe_enterprise_state() -> None:
    empty = RecruitmentMissionState(
        session_id="session-empty",
        role_title="New role",
        status="draft",
        candidate_count=0,
        analyzed_count=0,
        progress_percent=10,
        stage="Mission setup",
        candidates=(),
        recommended_candidate="Not available",
        recommended_score=0.0,
        average_confidence=None,
        summary="Upload candidate documents.",
    )

    model = build_enterprise_workspace_model(
        empty,
        section_definitions=(),
        renderers={},
    )

    assert model.metrics[1].value == "Not available"
    assert model.metrics[1].detail == "Awaiting analysis"
    assert model.metrics[2].value == "—"
    assert model.sections == ()
