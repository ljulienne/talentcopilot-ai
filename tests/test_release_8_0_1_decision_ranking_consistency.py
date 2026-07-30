from types import SimpleNamespace

from talentcopilot.recruitment_source_of_truth import RecruitmentSourceOfTruthService
from talentcopilot.services.candidate_workspace_service import CandidateWorkspaceService
from talentcopilot.services.comparison_workspace_service import ComparisonWorkspaceService
from talentcopilot.services.decision_board_service import DecisionBoardService


def _analysis(name, candidate_id, mission_rank, decision_rank, score):
    return SimpleNamespace(
        candidate_name=name,
        candidate_id=candidate_id,
        rank=mission_rank,
        official_rank=mission_rank,
        match_score=score,
        official_match_score=score,
        decision_score=score - 2,
        official_confidence_score=92,
        score_breakdown={
            "mission_fit_rank": mission_rank,
            "decision_rank": decision_rank,
            "interview_priority": decision_rank,
        },
        decision_report=None,
    )


def _session():
    analyses = [
        _analysis("Louis Julienne", "candidate-louis", 1, 2, 85),
        _analysis("Vincent Blakoe", "candidate-vincent", 2, 1, 81),
    ]
    candidates = [
        {
            "candidate_id": item.candidate_id,
            "name": item.candidate_name,
            "skills": ["HRIS"],
            "achievements": [f"Delivered an HRIS programme for {item.candidate_name}."],
        }
        for item in analyses
    ]
    return SimpleNamespace(
        session_id="release-8-0-1-ranking",
        role_title="HRIS Manager",
        job={"required_skills": ["HRIS"]},
        analyses=analyses,
        ranked_analyses=analyses,
        candidates=candidates,
        metadata={},
    )


def test_decision_board_displays_canonical_mission_rank_not_decision_priority():
    session = _session()
    source = RecruitmentSourceOfTruthService()
    source.freeze(session, replace=True)

    records = {item.candidate_id: item for item in source.get(session).candidates}
    assert records["candidate-louis"].mission_rank == 1
    assert records["candidate-louis"].decision_rank == 2

    report = DecisionBoardService().build(session)
    louis = next(item for item in report.candidates if item.candidate_id == "candidate-louis")

    assert louis.rank == 1
    assert louis.match_score == 85


def test_decision_board_rank_matches_candidate_and_comparison_workspaces():
    session = _session()
    RecruitmentSourceOfTruthService().freeze(session, replace=True)

    candidate_reports = {item.candidate_id: item for item in CandidateWorkspaceService().build_all(session)}
    comparison_reports = {item.candidate_name: item for item in ComparisonWorkspaceService().build(session).candidates}
    decision_reports = {item.candidate_id: item for item in DecisionBoardService().build(session).candidates}

    assert candidate_reports["candidate-louis"].rank == 1
    assert comparison_reports["Louis Julienne"].rank == 1
    assert decision_reports["candidate-louis"].rank == 1


def test_decision_board_keeps_candidate_identity_when_names_are_not_used_as_keys():
    session = _session()
    RecruitmentSourceOfTruthService().freeze(session, replace=True)

    report = DecisionBoardService().build(session)

    assert [item.candidate_id for item in report.candidates] == [
        "candidate-louis",
        "candidate-vincent",
    ]


def test_decision_board_ui_uses_candidate_ids_directly():
    from pathlib import Path

    source = Path("talentcopilot/ui/decision_board.py").read_text(encoding="utf-8")

    assert "_candidate_id_by_name" not in source
    assert "candidate.candidate_id" in source
    assert "Official rank #{candidate.rank}" in source
