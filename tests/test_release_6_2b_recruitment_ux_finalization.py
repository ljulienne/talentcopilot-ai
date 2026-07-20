from talentcopilot.models.recruitment_session import (
    CandidateAnalysisState,
    CandidateAnalysisStatus,
    RecruitmentSession,
    SessionStatus,
)
from talentcopilot.recruitment_source_of_truth import RecruitmentSourceOfTruthService
from talentcopilot.services.comparison_workspace_service import ComparisonWorkspaceService
from talentcopilot.services.recruitment_workspace_service import RecruitmentWorkspaceService


class _Signals:
    confidence = 80.0
    recommendation = "Interview"
    key_strength = "Relevant evidence"
    key_risk = "Validate scope"


class _SignalService:
    def build(self, analysis, session):
        return _Signals()


def _session():
    # Objective Mission Fit puts Loretta third, while Career Intelligence
    # recommends Zelma before Loretta for interview priority.
    rows = [
        ("vincent", "Vincent", 88, 1, 1, 84),
        ("louis", "Louis", 81, 2, 2, 79),
        ("loretta", "Loretta", 74, 3, 4, 51),
        ("zelma", "Zelma", 70, 4, 3, 76),
    ]
    analyses = []
    candidates = []
    for candidate_id, name, mission, mission_rank, decision_rank, career in rows:
        analyses.append(
            CandidateAnalysisState(
                candidate_name=name,
                candidate_id=candidate_id,
                status=CandidateAnalysisStatus.ANALYZED,
                match_score=mission,
                decision_score=mission - 2,
                rank=mission_rank,
                score_breakdown={
                    "mission_fit_rank": mission_rank,
                    "decision_rank": decision_rank,
                    "interview_priority": decision_rank,
                    "career_fit": career,
                    "confidence": 82,
                },
                notes=["Recommendation: Interview"],
            )
        )
        candidates.append({"candidate_id": candidate_id, "name": name})
    return RecruitmentSession(
        session_id="release-6-2b",
        job={"title": "HRIS Manager"},
        candidates=candidates,
        status=SessionStatus.COMPLETED,
        analyses=analyses,
    )


def test_source_of_truth_preserves_separate_mission_and_decision_ranks():
    session = _session()
    snapshot = RecruitmentSourceOfTruthService().freeze(session)
    by_name = {item.candidate_name: item for item in snapshot.candidates}

    assert by_name["Loretta"].mission_rank == 3
    assert by_name["Loretta"].decision_rank == 4
    assert by_name["Loretta"].interview_priority == 4
    assert by_name["Loretta"].career_fit_score == 51
    assert by_name["Zelma"].mission_rank == 4
    assert by_name["Zelma"].interview_priority == 3


def test_workspace_uses_interview_priority_without_changing_mission_fit():
    report = RecruitmentWorkspaceService().build(_session())
    assert [item.name for item in report.candidates] == ["Vincent", "Louis", "Zelma", "Loretta"]
    loretta = next(item for item in report.candidates if item.name == "Loretta")
    assert loretta.match_score == 74
    assert loretta.mission_rank == 3
    assert loretta.interview_priority == 4
    assert loretta.career_fit_score == 51


def test_comparison_uses_same_official_order_and_scores():
    report = ComparisonWorkspaceService(signal_service=_SignalService()).build(_session())
    assert [item.candidate_name for item in report.candidates] == ["Vincent", "Louis", "Zelma", "Loretta"]
    loretta = next(item for item in report.candidates if item.candidate_name == "Loretta")
    assert loretta.match_score == 74
    assert loretta.mission_rank == 3
    assert loretta.interview_priority == 4


def test_candidate_names_do_not_drive_decision_order():
    session = _session()
    session.analyses[2].candidate_name = "AAA"
    session.analyses[3].candidate_name = "ZZZ"
    snapshot = RecruitmentSourceOfTruthService().freeze(session)
    assert [item.candidate_id for item in sorted(snapshot.candidates, key=lambda x: x.interview_priority)] == [
        "vincent", "louis", "zelma", "loretta"
    ]


def test_source_of_truth_validation_accepts_dual_rank_contract():
    session = _session()
    service = RecruitmentSourceOfTruthService()
    service.freeze(session)
    assert service.get(session).version == "recruitment-sot-v1.0"
