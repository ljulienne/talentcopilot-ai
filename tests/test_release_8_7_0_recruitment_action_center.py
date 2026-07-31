from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from talentcopilot.models.recruitment_action_center import (
    ACTION_STATUS_DONE,
    ACTION_STATUS_IN_PROGRESS,
    ACTION_STATUS_OPEN,
)
from talentcopilot.models.recruitment_session import (
    CandidateAnalysisState,
    CandidateAnalysisStatus,
    RecruitmentSession,
    SessionStatus,
)
from talentcopilot.models.recruitment_workflow import RecruitmentWorkflowContext
from talentcopilot.recruitment_source_of_truth import RecruitmentSourceOfTruthService
from talentcopilot.services.recruitment_action_center import (
    ACTION_CENTER_KEY,
    RecruitmentActionCenterService,
    action_states_from_payload,
    stable_action_id,
    update_saved_action_status,
)
from talentcopilot.services.recruitment_project_persistence import load_project, save_project
from talentcopilot.services.recruitment_project_portfolio import (
    LIFECYCLE_ARCHIVED,
    LIFECYCLE_DECISION_READY,
    LIFECYCLE_REVIEW,
    ProjectPortfolioSummary,
)
from talentcopilot.storage import recruitment_store


NOW = datetime(2026, 7, 31, 0, 0, tzinfo=timezone.utc)


def _project(
    project_id: str,
    title: str,
    *,
    lifecycle: str = LIFECYCLE_REVIEW,
    priority: str = "Normal",
    owner: str = "Recruiter A",
    updated_at: str = "2026-07-30T20:00:00+00:00",
    source: str = "storage",
    is_active: bool = False,
) -> ProjectPortfolioSummary:
    return ProjectPortfolioSummary(
        project_id=project_id,
        title=title,
        role_title=title,
        project_type="Recruitment",
        lifecycle=lifecycle,
        priority=priority,
        owner=owner,
        location="Remote",
        candidate_count=3,
        analyzed_count=3,
        interview_count=0,
        finalist_count=2 if lifecycle == LIFECYCLE_DECISION_READY else 0,
        decision_recorded=False,
        updated_at=updated_at,
        source=source,
        is_active=is_active,
    )


def test_action_center_builds_exactly_one_domain_agnostic_action_per_open_project():
    projects = (
        _project("hris", "HRIS Manager"),
        _project(
            "sales",
            "Senior Sales Manager",
            lifecycle=LIFECYCLE_DECISION_READY,
            updated_at="2026-07-20T00:00:00+00:00",
        ),
        _project("software", "Software Engineer"),
        _project("finance", "Finance Director", lifecycle=LIFECYCLE_ARCHIVED),
    )

    report = RecruitmentActionCenterService().build(projects, now=NOW)

    assert report.total_actions == 3
    assert len({item.project_id for item in report.actions}) == 3
    assert {item.project_title for item in report.actions} == {
        "HRIS Manager",
        "Senior Sales Manager",
        "Software Engineer",
    }
    decision_action = next(item for item in report.actions if item.project_id == "sales")
    assert decision_action.category == "Decision"
    assert decision_action.severity == "High"
    assert decision_action.recommended_action == "Review finalists and record the human-owned decision."


def test_action_id_is_stable_and_status_is_applied_without_suppressing_source_signal():
    project = _project("project-a", "Operations Director")
    action_id = stable_action_id("project-a", "Workflow", "Review candidate evidence")
    assert action_id == stable_action_id("project-a", "Workflow", "  Review   candidate evidence ")

    report = RecruitmentActionCenterService().build(
        (project,),
        states_by_project={
            "project-a": {
                action_id: {
                    "status": ACTION_STATUS_IN_PROGRESS,
                    "updated_at": "2026-07-30T22:00:00+00:00",
                    "actor": "Recruiter A",
                }
            }
        },
        now=NOW,
    )

    action = report.actions[0]
    assert action.status == ACTION_STATUS_IN_PROGRESS
    assert action.summary
    assert action.recommended_action == "Review candidate evidence"
    assert action.status_actor == "Recruiter A"
    assert report.in_progress_actions == 1
    assert report.open_actions == 0


def test_action_order_prioritises_execution_status_then_severity():
    critical = _project(
        "critical",
        "Plant Director",
        priority="Critical",
        owner="Unassigned",
        updated_at="2026-07-10T00:00:00+00:00",
    )
    normal = _project("normal", "Data Analyst")
    critical_id = stable_action_id("critical", "Ownership", "Assign an owner before the next project update.")
    normal_id = stable_action_id("normal", "Workflow", "Review candidate evidence")

    report = RecruitmentActionCenterService().build(
        (normal, critical),
        states_by_project={
            "normal": {normal_id: {"status": ACTION_STATUS_DONE}},
            "critical": {critical_id: {"status": ACTION_STATUS_OPEN}},
        },
        now=NOW,
    )

    assert report.actions[0].project_id == "critical"
    assert report.actions[-1].project_id == "normal"
    assert report.critical_or_high_open_actions == 1
    assert report.unassigned_open_actions == 1


@pytest.fixture()
def isolated_storage(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    recruitments_dir = data_dir / "recruitments"
    monkeypatch.setattr(recruitment_store, "DATA_DIR", data_dir)
    monkeypatch.setattr(recruitment_store, "RECRUITMENTS_DIR", recruitments_dir)
    return recruitments_dir


def _session() -> RecruitmentSession:
    session = RecruitmentSession(
        session_id="action-persistence-test",
        job={"title": "Supply Chain Director", "location": "Singapore"},
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
                match_score=82.0,
                decision_score=78.0,
                rank=1,
                score_breakdown={"mission_fit_rank": 1, "decision_rank": 1},
            ),
            CandidateAnalysisState(
                candidate_name="Bob Lee",
                candidate_id="candidate-b",
                status=CandidateAnalysisStatus.ANALYZED,
                match_score=64.0,
                decision_score=61.0,
                rank=2,
                score_breakdown={"mission_fit_rank": 2, "decision_rank": 2},
            ),
        ],
        metadata={"source": "real_upload"},
    )
    RecruitmentSourceOfTruthService().freeze(session)
    return session


def test_persisted_action_status_preserves_canonical_candidate_state(isolated_storage):
    session = _session()
    workflow = RecruitmentWorkflowContext(
        session_id=session.session_id,
        role_title=session.role_title,
    )
    save_project(session, workflow)

    action_id = stable_action_id(
        session.session_id,
        "Workflow",
        "Review candidate evidence",
    )
    update_saved_action_status(
        session.session_id,
        action_id,
        ACTION_STATUS_DONE,
        actor="Recruiter A",
        now=NOW,
    )

    restored, _, payload = load_project(session.session_id)
    snapshot = RecruitmentSourceOfTruthService().get(restored, validate=True)
    assert [(item.candidate_id, item.mission_fit_score, item.mission_rank) for item in snapshot.candidates] == [
        ("candidate-a", 82.0, 1),
        ("candidate-b", 64.0, 2),
    ]
    states = action_states_from_payload(payload)
    assert states[action_id]["status"] == ACTION_STATUS_DONE
    assert states[action_id]["actor"] == "Recruiter A"
    assert payload["metadata"]["project_management"][ACTION_CENTER_KEY]["version"]


def test_action_center_ui_and_navigation_are_integrated_without_score_mutation():
    ui_source = Path("talentcopilot/ui/recruitment_action_center.py").read_text(encoding="utf-8")
    nav_source = Path("talentcopilot/ui/enterprise_navigation.py").read_text(encoding="utf-8")
    sidebar_source = Path("talentcopilot/ui/premium_sidebar.py").read_text(encoding="utf-8")
    analytics_source = Path("talentcopilot/ui/analytics_dashboard.py").read_text(encoding="utf-8")

    assert "Recruitment Action Center" in ui_source
    assert "Start action" in ui_source
    assert "Mark done" in ui_source
    assert '"Action Center"' in nav_source
    assert '"Action Center"' in sidebar_source
    assert "Open Action Center" in analytics_source
    assert "match_score" not in ui_source
    assert "decision_score" not in ui_source


def test_action_center_service_never_reads_candidate_score_or_rank_fields():
    source = Path("talentcopilot/services/recruitment_action_center.py").read_text(encoding="utf-8")
    forbidden = ("match_score", "decision_score", "mission_rank", "decision_rank")
    assert not any(item in source for item in forbidden)


def test_visible_version_is_release_8_7_0():
    from talentcopilot.config import APP_VERSION

    assert APP_VERSION == "v8.7.0"
