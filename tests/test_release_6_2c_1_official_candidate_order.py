from types import SimpleNamespace

from talentcopilot.decision_ranking import DecisionRankingPolicy
from talentcopilot.recruitment_source_of_truth import RecruitmentSourceOfTruthService
from talentcopilot.services.candidate_workspace_service import CandidateWorkspaceService


def analysis(name, cid, mission_rank, decision_rank, score, decision_score):
    return SimpleNamespace(
        candidate_name=name,
        candidate_id=cid,
        rank=mission_rank,
        official_rank=mission_rank,
        match_score=score,
        official_match_score=score,
        decision_score=decision_score,
        official_confidence_score=90,
        score_breakdown={
            "mission_fit_rank": mission_rank,
            "decision_rank": decision_rank,
            "interview_priority": decision_rank,
            "career_fit": 70,
        },
        decision_report=None,
    )


def session():
    analyses = [
        analysis("Vincent", "v", 1, 1, 90, 88),
        analysis("Louis", "l", 2, 2, 82, 80),
        analysis("Loretta", "o", 3, 4, 76, 64),
        analysis("Zelma", "z", 4, 3, 72, 69),
    ]
    candidates = [
        {"candidate_id": item.candidate_id, "name": item.candidate_name, "skills": [], "achievements": []}
        for item in analyses
    ]
    return SimpleNamespace(
        session_id="release-6-2c-1",
        role_title="HRIS Manager",
        analyses=analyses,
        ranked_analyses=analyses,
        candidates=candidates,
        metadata={},
    )


def test_single_official_candidate_order_is_decision_order():
    current = session()
    service = RecruitmentSourceOfTruthService()
    service.freeze(current, replace=True)
    assert service.ordered_candidate_ids(current) == ["v", "l", "z", "o"]
    assert [x.candidate_name for x in service.ordered_analyses(current)] == ["Vincent", "Louis", "Zelma", "Loretta"]


def test_candidate_workspace_uses_same_order_and_decision_rank():
    current = session()
    RecruitmentSourceOfTruthService().freeze(current, replace=True)
    reports = CandidateWorkspaceService().build_all(current)
    assert [x.candidate_name for x in reports] == ["Vincent", "Louis", "Zelma", "Loretta"]
    assert [x.rank for x in reports] == [1, 2, 3, 4]


def test_compound_career_mismatch_can_reverse_small_mission_advantage():
    policy = DecisionRankingPolicy()
    aligned = SimpleNamespace(
        score=72, recent_role_alignment=78, domain_persistence=75,
        career_drift=24, seniority_alignment=76, functional_alignment=74,
        transferability=78,
    )
    drifted = SimpleNamespace(
        score=58, recent_role_alignment=36, domain_persistence=48,
        career_drift=72, seniority_alignment=38, functional_alignment=62,
        transferability=67,
    )
    aligned_result = policy.evaluate(mission_fit=72, career=aligned, recruiter_fit=70, confidence=88)
    drifted_result = policy.evaluate(mission_fit=76, career=drifted, recruiter_fit=72, confidence=88)
    assert aligned_result.score > drifted_result.score
    assert "combined recent-role mismatch and domain drift" in drifted_result.blockers
