from __future__ import annotations

import sys
import types
from dataclasses import dataclass
from pathlib import Path

from talentcopilot.models.recruitment_workflow import (
    RecruitmentWorkflowContext,
)
from talentcopilot.services.candidate_ordering import (
    order_candidate_ids,
    sort_by_official_rank,
)
from talentcopilot.services.recruitment_workflow_state import (
    WORKFLOW_CONTEXT_KEY,
    select_workflow_candidate,
)


@dataclass
class Candidate:
    candidate_id: str
    candidate_name: str
    mission_rank: int
    match_score: float
    interview_priority: int


def candidates():
    return [
        Candidate(
            candidate_id="vincent",
            candidate_name="Vincent Blakoe",
            mission_rank=2,
            match_score=80,
            interview_priority=1,
        ),
        Candidate(
            candidate_id="louis",
            candidate_name="Louis Julienne",
            mission_rank=1,
            match_score=84,
            interview_priority=2,
        ),
    ]


def test_official_sort_ignores_interview_priority():
    ordered = sort_by_official_rank(
        candidates()
    )

    assert [
        item.candidate_id
        for item in ordered
    ] == [
        "louis",
        "vincent",
    ]

    assert [
        item.match_score
        for item in ordered
    ] == [
        84,
        80,
    ]


def test_selected_finalists_follow_official_order():
    ordered = order_candidate_ids(
        ["vincent", "louis"],
        ["louis", "vincent"],
    )

    assert ordered == [
        "louis",
        "vincent",
    ]


class GuardedSessionState(dict):
    def __setitem__(
        self,
        key,
        value,
    ):
        if (
            key
            == "candidate_intelligence_candidate_id"
        ):
            raise RuntimeError(
                "Widget already instantiated"
            )

        super().__setitem__(
            key,
            value,
        )


def test_widget_failure_does_not_block_sync(
    monkeypatch,
):
    context = RecruitmentWorkflowContext()

    state = GuardedSessionState(
        {
            WORKFLOW_CONTEXT_KEY: context,
        }
    )

    fake_streamlit = (
        types.SimpleNamespace(
            session_state=state
        )
    )

    monkeypatch.setitem(
        sys.modules,
        "streamlit",
        fake_streamlit,
    )

    select_workflow_candidate(
        "louis",
        "Louis Julienne",
    )

    assert (
        state[
            WORKFLOW_CONTEXT_KEY
        ].selected_candidate_id
        == "louis"
    )

    assert (
        state[
            "interview_intelligence_candidate_id"
        ]
        == "louis"
    )


def test_comparison_service_uses_official_order():
    source = Path(
        "talentcopilot/services/"
        "comparison_workspace_service.py"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        "sort_by_official_rank"
        "(source.candidates)"
    ) in source

    assert (
        "key=lambda item: "
        "item.interview_priority"
    ) not in source


def test_comparison_ui_orders_selected_candidates():
    source = Path(
        "talentcopilot/ui/"
        "comparison_workspace.py"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        "ordered_candidates = "
        "sort_by_official_rank"
    ) in source

    assert (
        "selected_ids = "
        "order_candidate_ids"
    ) in source


def test_decision_board_uses_candidate_id_widget():
    source = Path(
        "talentcopilot/ui/"
        "decision_board.py"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        '"decision_candidate_id"'
    ) in source

    assert (
        "candidates = "
        "sort_by_official_rank"
    ) in source

    assert (
        "source_widget_key="
        "selection_key"
    ) in source


def test_interview_context_includes_active_candidate():
    source = Path(
        "talentcopilot/ui/"
        "interview_intelligence.py"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        "preferred_option,"
    ) in source

    assert (
        "resolved_report_id "
        "!= selected_id"
    ) in source

    assert (
        "source_widget_key="
        "selection_key"
    ) in source
