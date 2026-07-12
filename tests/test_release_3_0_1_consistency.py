from talentcopilot.services.candidate_intelligence import CandidateIntelligenceService
from talentcopilot.services.candidate_workspace_service import CandidateWorkspaceService
from talentcopilot.services.demo_session_factory import create_demo_recruitment_session


def test_demo_candidates_have_unique_stable_ids():
    session = create_demo_recruitment_session()
    candidate_ids = [candidate["candidate_id"] for candidate in session.candidates]
    analysis_ids = [analysis.candidate_id for analysis in session.analyses]

    assert len(candidate_ids) == len(set(candidate_ids))
    assert set(candidate_ids) == set(analysis_ids)


def test_david_smith_has_one_official_score_and_rank_across_services():
    session = create_demo_recruitment_session()
    analysis = session.get_analysis("demo-david-smith-reporting")
    reports = CandidateWorkspaceService().build_all(session)
    report = next(item for item in reports if item.candidate_id == analysis.candidate_id)
    intelligence = CandidateIntelligenceService().build(report)

    assert analysis.official_match_score == report.official_match_score
    assert analysis.official_rank == report.official_rank
    assert intelligence.mission_fit == analysis.official_match_score


def test_david_smith_receives_explainable_partial_fit_not_zero():
    session = create_demo_recruitment_session()
    analysis = session.get_analysis("demo-david-smith-reporting")

    assert analysis.match_score > 0
    assert analysis.match_score < 50
    assert analysis.score_breakdown["required_skills"] == 0
    assert analysis.score_breakdown["transferable_skills"] > 0
    assert round(sum(analysis.score_breakdown.values()), 2) == analysis.match_score


def test_official_ranking_is_deterministic_and_score_descending():
    session = create_demo_recruitment_session()
    ranked = session.ranked_analyses

    assert [item.rank for item in ranked] == list(range(1, len(ranked) + 1))
    assert [item.match_score for item in ranked] == sorted(
        [item.match_score for item in ranked], reverse=True
    )
