from __future__ import annotations

from pathlib import Path

import pytest

from talentcopilot.models.recruitment_session import (
    CandidateAnalysisState,
    CandidateAnalysisStatus,
    RecruitmentSession,
    SessionStatus,
)
from talentcopilot.models.recruitment_workflow import RecruitmentWorkflowContext
from talentcopilot.recruitment_source_of_truth import RecruitmentSourceOfTruthService
from talentcopilot.services.recruitment_project_persistence import load_project, save_project
from talentcopilot.services.recruitment_project_portfolio import (
    LIFECYCLE_ANALYZING,
    LIFECYCLE_ARCHIVED,
    LIFECYCLE_DECIDED,
    LIFECYCLE_DECISION_READY,
    LIFECYCLE_INTERVIEW,
    LIFECYCLE_REVIEW,
    archive_project,
    build_project_summaries,
    derive_lifecycle,
    filter_project_summaries,
    portfolio_metrics,
    reopen_project,
    update_project_details,
)
from talentcopilot.storage import recruitment_store


@pytest.fixture()
def isolated_project_storage(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    recruitments_dir = data_dir / "recruitments"
    monkeypatch.setattr(recruitment_store, "DATA_DIR", data_dir)
    monkeypatch.setattr(recruitment_store, "RECRUITMENTS_DIR", recruitments_dir)
    return recruitments_dir


def _session(session_id: str = "portfolio-project") -> RecruitmentSession:
    session = RecruitmentSession(
        session_id=session_id,
        job={
            "title": "Global Operations Director",
            "location": "Singapore",
            "required_skills": ["Operations Strategy", "Team Leadership"],
        },
        candidates=[
            {"candidate_id": "candidate-a", "name": "Alice Martin"},
            {"candidate_id": "candidate-b", "name": "Bob Lee"},
        ],
        status=SessionStatus.COMPLETED,
        analyses=[
            CandidateAnalysisState(
                candidate_name="Alice Martin",
                candidate_id="candidate-a",
                status=CandidateAnalysisStatus.ANALYZED,
                match_score=86.0,
                decision_score=81.0,
                rank=1,
                score_breakdown={"mission_fit_rank": 1, "decision_rank": 1},
            ),
            CandidateAnalysisState(
                candidate_name="Bob Lee",
                candidate_id="candidate-b",
                status=CandidateAnalysisStatus.ANALYZED,
                match_score=64.0,
                decision_score=60.0,
                rank=2,
                score_breakdown={"mission_fit_rank": 2, "decision_rank": 2},
            ),
        ],
        metadata={"source": "real_upload"},
    )
    RecruitmentSourceOfTruthService().freeze(session, replace=True)
    return session


def _workflow(**updates) -> RecruitmentWorkflowContext:
    values = {
        "session_id": "portfolio-project",
        "role_title": "Global Operations Director",
        "completed_steps": ["setup", "review"],
    }
    values.update(updates)
    return RecruitmentWorkflowContext(**values)


def test_lifecycle_is_derived_from_real_workflow_state():
    assert derive_lifecycle(candidate_count=3, analyzed_count=1) == LIFECYCLE_ANALYZING
    assert derive_lifecycle(candidate_count=3, analyzed_count=3) == LIFECYCLE_REVIEW
    assert derive_lifecycle(
        candidate_count=3,
        analyzed_count=3,
        workflow_context=_workflow(interview_assessed_candidate_ids=["candidate-a"]),
    ) == LIFECYCLE_INTERVIEW
    assert derive_lifecycle(
        candidate_count=3,
        analyzed_count=3,
        workflow_context=_workflow(finalists_compared=True),
    ) == LIFECYCLE_DECISION_READY
    assert derive_lifecycle(
        candidate_count=3,
        analyzed_count=3,
        workflow_context=_workflow(decision_recorded=True),
    ) == LIFECYCLE_DECIDED
    assert derive_lifecycle(
        candidate_count=3,
        analyzed_count=3,
        workflow_context=_workflow(decision_recorded=True),
        management={"archived": True},
    ) == LIFECYCLE_ARCHIVED


def test_portfolio_search_filter_sort_and_metrics_are_domain_agnostic():
    projects = build_project_summaries(
        None,
        [
            {
                "id": "REC-SALES",
                "title": "Senior Sales Manager",
                "candidate_count": 4,
                "analyzed_count": 4,
                "updated_at": "2026-07-30T10:00:00+00:00",
                "job": {"location": "Singapore"},
                "metadata": {"project_management": {"owner": "Jane", "priority": "High"}},
                "workflow_context": {"finalists_compared": True},
            },
            {
                "id": "REC-ENGINEERING",
                "title": "Platform Engineer",
                "candidate_count": 5,
                "analyzed_count": 2,
                "updated_at": "2026-07-29T10:00:00+00:00",
                "job": {"location": "Paris"},
                "metadata": {"project_management": {"owner": "Louis", "priority": "Critical"}},
            },
            {
                "id": "REC-FINANCE",
                "title": "Finance Director",
                "candidate_count": 3,
                "analyzed_count": 3,
                "updated_at": "2026-07-28T10:00:00+00:00",
                "metadata": {"project_management": {"archived": True}},
            },
        ],
    )

    assert [item.project_id for item in filter_project_summaries(projects, query="Paris")] == [
        "REC-ENGINEERING"
    ]
    assert [
        item.project_id
        for item in filter_project_summaries(projects, lifecycle=LIFECYCLE_DECISION_READY)
    ] == ["REC-SALES"]
    assert [
        item.project_id
        for item in filter_project_summaries(projects, include_archived=True, sort_by="priority")
    ][:2] == ["REC-ENGINEERING", "REC-SALES"]

    metrics = portfolio_metrics(projects)
    assert metrics == {
        "projects": 2,
        "candidates": 9,
        "decision_ready": 1,
        "archived": 1,
    }


def test_project_management_changes_preserve_official_scores_and_ranks(isolated_project_storage):
    session = _session()
    workflow = _workflow(
        finalists_compared=True,
        finalist_candidate_ids=["candidate-a", "candidate-b"],
    )
    save_project(session, workflow)

    update_project_details(
        session.session_id,
        display_name="APAC Operations Leadership",
        owner="Recruiter A",
        priority="Critical",
    )
    restored, restored_workflow, data = load_project(session.session_id)

    assert data["metadata"]["project_management"]["display_name"] == "APAC Operations Leadership"
    assert data["metadata"]["project_management"]["owner"] == "Recruiter A"
    assert data["metadata"]["project_management"]["priority"] == "Critical"
    assert restored_workflow.finalists_compared is True
    assert [(item.candidate_id, item.match_score, item.rank) for item in restored.ranked_analyses] == [
        ("candidate-a", 86.0, 1),
        ("candidate-b", 64.0, 2),
    ]
    snapshot = RecruitmentSourceOfTruthService().get(restored)
    assert [(item.candidate_id, item.mission_fit_score, item.mission_rank) for item in snapshot.candidates] == [
        ("candidate-a", 86.0, 1),
        ("candidate-b", 64.0, 2),
    ]


def test_archive_and_reopen_keep_decision_evidence_loadable(isolated_project_storage):
    session = _session()
    workflow = _workflow(
        decision_recorded=True,
        final_decision_candidate_id="candidate-a",
        final_decision_recommendation="Hire",
        final_decision_rationale="Strongest evidence across critical requirements.",
        decision_history=[{"candidate_id": "candidate-a", "recommendation": "Hire"}],
    )
    save_project(session, workflow)

    archived = archive_project(session.session_id)
    assert archived["metadata"]["project_management"]["archived"] is True
    restored, restored_workflow, _ = load_project(session.session_id)
    assert restored_workflow.final_decision_recommendation == "Hire"
    assert restored.ranked_analyses[0].match_score == 86.0

    reopened = reopen_project(session.session_id)
    assert reopened["metadata"]["project_management"]["archived"] is False
    restored_again, _, _ = load_project(session.session_id)
    assert restored_again.ranked_analyses[0].rank == 1


def test_storage_listing_exposes_portfolio_context(isolated_project_storage):
    session = _session()
    save_project(
        session,
        _workflow(interview_assessed_candidate_ids=["candidate-a"]),
    )
    update_project_details(session.session_id, owner="Recruiter A", priority="High")

    listed = recruitment_store.list_recruitments()
    assert len(listed) == 1
    assert listed[0]["job"]["location"] == "Singapore"
    assert listed[0]["metadata"]["project_management"]["owner"] == "Recruiter A"
    assert listed[0]["workflow_context"]["interview_assessed_candidate_ids"] == ["candidate-a"]


def test_project_hub_exposes_portfolio_controls_and_no_score_mutation():
    source = Path("talentcopilot/ui/project_hub.py").read_text(encoding="utf-8")
    assert "Recruitment portfolio" in source
    assert "Role, project name, location or owner" in source
    assert "Save project details" in source
    assert "Archive project" in source
    assert "Reopen project" in source
    assert "match_score" not in source
    assert "decision_score" not in source


def test_visible_version_is_release_8_5_0_or_later():
    from talentcopilot.config import APP_VERSION

    version = tuple(int(part) for part in APP_VERSION.lstrip("v").split("."))
    assert version >= (8, 5, 0)
