from __future__ import annotations

import json
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
from talentcopilot.services.recruitment_project_persistence import (
    PROJECT_SCHEMA_VERSION,
    PERSISTENCE_FLAG,
    load_project,
    persist_project_best_effort,
    save_project,
)
from talentcopilot.storage import recruitment_store


@pytest.fixture()
def isolated_project_storage(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    recruitments_dir = data_dir / "recruitments"
    monkeypatch.setattr(recruitment_store, "DATA_DIR", data_dir)
    monkeypatch.setattr(recruitment_store, "RECRUITMENTS_DIR", recruitments_dir)
    return recruitments_dir


def _session() -> RecruitmentSession:
    session = RecruitmentSession(
        session_id="upload-persistence-test",
        job={
            "title": "Global Sales Director",
            "location": "Singapore",
            "required_skills": ["Enterprise Sales", "Team Leadership"],
        },
        candidates=[
            {
                "candidate_id": "candidate-alice",
                "name": "Alice Martin",
                "skills": ["Enterprise Sales", "Team Leadership"],
                "achievements": ["Led a 25-person APAC sales team and grew revenue by 18%."],
                "raw_text": "Alice Martin CV evidence",
            },
            {
                "candidate_id": "candidate-bob",
                "name": "Bob Lee",
                "skills": ["Account Management"],
                "achievements": ["Managed strategic accounts in one country."],
                "raw_text": "Bob Lee CV evidence",
            },
        ],
        status=SessionStatus.COMPLETED,
        analyses=[
            CandidateAnalysisState(
                candidate_name="Alice Martin",
                candidate_id="candidate-alice",
                status=CandidateAnalysisStatus.ANALYZED,
                match_score=84.0,
                decision_score=79.5,
                rank=1,
                score_breakdown={
                    "mission_fit_rank": 1,
                    "decision_rank": 1,
                    "confidence": 88.0,
                },
                notes=["Evidence grounded."],
            ),
            CandidateAnalysisState(
                candidate_name="Bob Lee",
                candidate_id="candidate-bob",
                status=CandidateAnalysisStatus.ANALYZED,
                match_score=61.0,
                decision_score=58.0,
                rank=2,
                score_breakdown={
                    "mission_fit_rank": 2,
                    "decision_rank": 2,
                    "confidence": 64.0,
                },
                notes=["Leadership depth requires validation."],
            ),
        ],
        metadata={
            "source": "real_upload",
            "compensation_budget": {
                "currency": "SGD",
                "minimum_salary": 150000,
                "target_salary": 180000,
                "maximum_salary": 210000,
            },
            "candidate_compensation": {
                "candidate-alice": {
                    "candidate_id": "candidate-alice",
                    "candidate_name": "Alice Martin",
                    "currency": "SGD",
                    "expected_salary": 190000,
                    "availability_date": "2026-10-01",
                }
            },
        },
    )
    RecruitmentSourceOfTruthService().freeze(session)
    return session


def _workflow() -> RecruitmentWorkflowContext:
    return RecruitmentWorkflowContext(
        session_id="upload-persistence-test",
        role_title="Global Sales Director",
        selected_candidate_id="candidate-alice",
        selected_candidate_name="Alice Martin",
        completed_steps=["setup", "review", "assess", "compare", "decide"],
        shortlisted_candidate_ids=["candidate-alice", "candidate-bob"],
        interview_assessed_candidate_ids=["candidate-alice"],
        interview_evaluations={
            "candidate-alice": {
                "recommendation": "Advance",
                "evidence_coverage": 82,
                "competency_scores": {"Enterprise Sales": 4.4},
            }
        },
        finalist_candidate_ids=["candidate-alice", "candidate-bob"],
        finalists_compared=True,
        decision_recorded=True,
        final_decision_candidate_id="candidate-alice",
        final_decision_recommendation="Hire",
        final_decision_rationale="Strongest evidence across the critical requirements.",
        final_decision_actor="Recruiter A",
        final_decision_timestamp="2026-07-30T20:00:00+00:00",
        final_decision_evidence=["APAC revenue growth", "25-person team leadership"],
        final_decision_accepted_risks=["Notice period requires planning"],
        decision_history=[
            {
                "timestamp": "2026-07-30T20:00:00+00:00",
                "actor": "Recruiter A",
                "candidate_id": "candidate-alice",
                "recommendation": "Hire",
                "rationale": "Strongest evidence across the critical requirements.",
            }
        ],
    )


def test_versioned_project_round_trip_preserves_canonical_decision_state(isolated_project_storage):
    session = _session()
    workflow = _workflow()

    saved = save_project(session, workflow)
    restored, restored_workflow, payload = load_project(session.session_id)

    assert saved["schema_version"] == PROJECT_SCHEMA_VERSION
    assert restored.metadata[PERSISTENCE_FLAG] is True
    assert restored.role_title == session.role_title
    assert restored.job["location"] == "Singapore"
    assert [item.candidate_id for item in restored.ranked_analyses] == [
        "candidate-alice",
        "candidate-bob",
    ]
    assert [item.match_score for item in restored.ranked_analyses] == [84.0, 61.0]
    assert [item.decision_score for item in restored.ranked_analyses] == [79.5, 58.0]
    assert [item.rank for item in restored.ranked_analyses] == [1, 2]
    assert restored.metadata["compensation_budget"]["currency"] == "SGD"
    assert restored.metadata["candidate_compensation"]["candidate-alice"]["expected_salary"] == 190000
    assert restored_workflow.interview_evaluations["candidate-alice"]["recommendation"] == "Advance"
    assert restored_workflow.final_decision_recommendation == "Hire"
    assert restored_workflow.decision_history[0]["actor"] == "Recruiter A"
    assert payload["candidate_count"] == 2
    assert payload["analyzed_count"] == 2

    snapshot = RecruitmentSourceOfTruthService().get(restored)
    assert [(item.candidate_id, item.mission_fit_score, item.mission_rank) for item in snapshot.candidates] == [
        ("candidate-alice", 84.0, 1),
        ("candidate-bob", 61.0, 2),
    ]


def test_project_updates_are_automatic_only_after_explicit_save(isolated_project_storage):
    session = _session()
    workflow = _workflow()

    assert persist_project_best_effort(session, workflow) is False
    assert not isolated_project_storage.exists()

    save_project(session, workflow)
    assert session.metadata[PERSISTENCE_FLAG] is True

    workflow.final_decision_rationale = "Updated rationale after references were checked."
    assert persist_project_best_effort(session, workflow) is True

    _, restored_workflow, _ = load_project(session.session_id)
    assert restored_workflow.final_decision_rationale == "Updated rationale after references were checked."


def test_project_store_uses_atomic_json_and_lists_canonical_counts(isolated_project_storage):
    session = _session()
    save_project(session, _workflow())

    project_path = isolated_project_storage / f"{session.session_id}.json"
    temporary_path = project_path.with_suffix(".json.tmp")
    assert project_path.exists()
    assert not temporary_path.exists()

    raw = json.loads(project_path.read_text(encoding="utf-8"))
    assert raw["schema_version"] == PROJECT_SCHEMA_VERSION

    projects = recruitment_store.list_recruitments()
    assert len(projects) == 1
    assert projects[0]["candidate_count"] == 2
    assert projects[0]["analyzed_count"] == 2
    assert projects[0]["schema_version"] == PROJECT_SCHEMA_VERSION


def test_tampered_official_score_is_rejected_on_restore(isolated_project_storage):
    session = _session()
    save_project(session, _workflow())

    project_path = isolated_project_storage / f"{session.session_id}.json"
    data = json.loads(project_path.read_text(encoding="utf-8"))
    data["analyses"][0]["match_score"] = 12.0
    project_path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(Exception):
        load_project(session.session_id)


def test_project_hub_exposes_explicit_save_and_continuity_copy():
    source = Path("talentcopilot/ui/project_hub.py").read_text(encoding="utf-8")
    assert "Save project" in source
    assert "Project continuity" in source
    assert "official candidate IDs, scores, ranks" in source
