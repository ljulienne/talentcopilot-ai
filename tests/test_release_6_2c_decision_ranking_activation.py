from dataclasses import dataclass

from talentcopilot.decision_ranking import DecisionRankingPolicy
from talentcopilot.models.recruitment_session import (
    CandidateAnalysisState,
    CandidateAnalysisStatus,
    RecruitmentSession,
    SessionStatus,
)
from talentcopilot.recruitment_source_of_truth import RecruitmentSourceOfTruthService


@dataclass
class _Career:
    score: float
    recent_role_alignment: float
    domain_persistence: float
    career_drift: float
    seniority_alignment: float
    functional_alignment: float
    transferability: float


def _career_specialist():
    return _Career(76, 84, 82, 18, 86, 88, 84)


def _career_generalist():
    return _Career(52, 39, 44, 72, 42, 58, 55)


def test_material_career_alignment_can_reverse_a_small_mission_fit_gap():
    policy = DecisionRankingPolicy()
    generalist = policy.evaluate(
        mission_fit=74,
        career=_career_generalist(),
        recruiter_fit=72,
        confidence=82,
    )
    specialist = policy.evaluate(
        mission_fit=70,
        career=_career_specialist(),
        recruiter_fit=72,
        confidence=82,
    )
    assert specialist.score > generalist.score
    assert generalist.alignment_adjustment < 0
    assert generalist.blockers


def test_candidate_name_never_enters_decision_policy():
    policy = DecisionRankingPolicy()
    first = policy.evaluate(mission_fit=74, career=_career_generalist(), recruiter_fit=72, confidence=82)
    second = policy.evaluate(mission_fit=74, career=_career_generalist(), recruiter_fit=72, confidence=82)
    assert first == second


def test_mission_fit_remains_separate_and_unmodified():
    policy = DecisionRankingPolicy()
    mission_fit = 74
    assessment = policy.evaluate(
        mission_fit=mission_fit,
        career=_career_generalist(),
        recruiter_fit=72,
        confidence=82,
    )
    assert mission_fit == 74
    assert assessment.components["mission_fit"] == 74
    assert assessment.score != mission_fit


def test_source_of_truth_orders_by_interview_priority():
    analyses = [
        CandidateAnalysisState(
            candidate_name="Candidate Generalist",
            candidate_id="generalist",
            status=CandidateAnalysisStatus.ANALYZED,
            match_score=74,
            decision_score=58,
            rank=3,
            score_breakdown={
                "mission_fit_rank": 3,
                "decision_rank": 4,
                "interview_priority": 4,
                "career_fit": 52,
            },
        ),
        CandidateAnalysisState(
            candidate_name="Candidate Specialist",
            candidate_id="specialist",
            status=CandidateAnalysisStatus.ANALYZED,
            match_score=70,
            decision_score=72,
            rank=4,
            score_breakdown={
                "mission_fit_rank": 4,
                "decision_rank": 3,
                "interview_priority": 3,
                "career_fit": 76,
            },
        ),
    ]
    session = RecruitmentSession(
        session_id="release-62c",
        job={"title": "HRIS Manager"},
        candidates=[
            {"candidate_id": "generalist", "name": "Candidate Generalist"},
            {"candidate_id": "specialist", "name": "Candidate Specialist"},
        ],
        status=SessionStatus.COMPLETED,
        analyses=analyses,
    )
    service = RecruitmentSourceOfTruthService()
    snapshot = service.freeze(session)
    assert snapshot.version == "recruitment-sot-v1.0"
    ordered = service.ordered_analyses(session)
    assert [item.candidate_id for item in ordered] == ["specialist", "generalist"]
    by_id = {item.candidate_id: item for item in snapshot.candidates}
    assert by_id["generalist"].mission_rank == 3
    assert by_id["generalist"].interview_priority == 4
