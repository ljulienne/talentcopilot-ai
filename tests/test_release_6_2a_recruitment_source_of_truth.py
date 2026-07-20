import copy

import pytest

from talentcopilot.models.recruitment_session import (
    CandidateAnalysisState,
    CandidateAnalysisStatus,
    RecruitmentSession,
    SessionStatus,
)
from talentcopilot.recruitment_source_of_truth import (
    RecruitmentAnalysisCache,
    RecruitmentSourceOfTruthService,
    SourceOfTruthViolation,
)
from talentcopilot.services.candidate_workspace_service import CandidateWorkspaceService
from talentcopilot.services.comparison_workspace_service import ComparisonWorkspaceService
from talentcopilot.services.recruitment_workspace_service import RecruitmentWorkspaceService


def _session():
    analyses = [
        CandidateAnalysisState(
            candidate_name="Candidate A", candidate_id="a", status=CandidateAnalysisStatus.ANALYZED,
            match_score=82, decision_score=78, rank=2, score_breakdown={"confidence": 91},
        ),
        CandidateAnalysisState(
            candidate_name="Candidate B", candidate_id="b", status=CandidateAnalysisStatus.ANALYZED,
            match_score=75, decision_score=84, rank=1, score_breakdown={"confidence": 88},
        ),
    ]
    return RecruitmentSession(
        session_id="session-62a", job={"title": "HRIS Manager"},
        candidates=[
            {"candidate_id": "a", "name": "Candidate A", "skills": ["HRIS"]},
            {"candidate_id": "b", "name": "Candidate B", "skills": ["Workday"]},
        ], status=SessionStatus.COMPLETED, analyses=analyses,
    )


def test_freeze_publishes_serializable_official_snapshot():
    session = _session()
    snapshot = RecruitmentSourceOfTruthService().freeze(session)
    assert snapshot.version == "recruitment-sot-v1.0"
    assert session.metadata["recruitment_source_of_truth"]["session_id"] == session.session_id
    assert len(snapshot.candidates) == 2


def test_mission_and_decision_ranks_are_explicit_and_separate():
    snapshot = RecruitmentSourceOfTruthService().freeze(_session())
    by_id = {item.candidate_id: item for item in snapshot.candidates}
    assert by_id["a"].mission_rank == 1
    assert by_id["a"].decision_rank == 2
    assert by_id["b"].mission_rank == 2
    assert by_id["b"].interview_priority == 1


def test_navigation_reuses_cached_analysis_without_pipeline_execution():
    session = _session()
    service = RecruitmentSourceOfTruthService()
    first = service.freeze(session)
    second = service.get(session)
    assert first is second
    assert RecruitmentAnalysisCache.get(session.session_id) is first


def test_score_or_rank_mutation_is_detected():
    session = _session()
    service = RecruitmentSourceOfTruthService()
    service.freeze(session)
    session.analyses[0].match_score = 12
    with pytest.raises(SourceOfTruthViolation):
        service.get(session)


def test_all_recruitment_views_read_the_same_official_order_and_scores():
    session = _session()
    RecruitmentSourceOfTruthService().freeze(session)
    recruitment = RecruitmentWorkspaceService().build(session)
    comparison = ComparisonWorkspaceService().build(session)
    candidates = CandidateWorkspaceService().build_all(session)

    expected = [("Candidate B", 75.0, 1), ("Candidate A", 82.0, 2)]
    assert [(x.name, x.match_score, x.rank) for x in recruitment.candidates] == expected
    assert [(x.candidate_name, x.match_score, x.rank) for x in comparison.candidates] == expected
    assert [(x.candidate_name, x.match_score, x.rank) for x in candidates] == expected


def test_snapshot_is_deterministic_for_same_session_data():
    session1 = _session()
    session2 = copy.deepcopy(session1)
    service = RecruitmentSourceOfTruthService()
    first = service.freeze(session1)
    RecruitmentAnalysisCache.invalidate(session2.session_id)
    second = service.freeze(session2)
    assert first.analysis_fingerprint == second.analysis_fingerprint
