"""
Regression tests for the official candidate display score.

CandidateAnalysisState.match_score remains the historical raw fit score.
Recruiter-facing services display the consolidated ranking score.
"""

from types import SimpleNamespace

from talentcopilot.services.official_score_service import (
    get_official_candidate_score,
)
from talentcopilot.services.recruitment_upload_session_service import (
    RecruitmentUploadSessionService,
)


def _analysis(
    *,
    match_score=50,
    ranking_score=None,
    metadata=None,
):
    score_breakdown = {}

    if ranking_score is not None:
        score_breakdown["official_ranking_score"] = ranking_score

    return SimpleNamespace(
        match_score=match_score,
        score_breakdown=score_breakdown,
        metadata=metadata or {},
    )


def test_official_score_prefers_consolidated_ranking_score():
    analysis = _analysis(
        match_score=50,
        ranking_score=86,
    )

    assert analysis.match_score == 50
    assert get_official_candidate_score(analysis) == 86


def test_official_score_preserves_zero_ranking_score():
    analysis = _analysis(
        match_score=41,
        ranking_score=0,
    )

    assert get_official_candidate_score(analysis) == 0


def test_official_score_falls_back_to_match_score():
    analysis = _analysis(match_score=35)

    assert get_official_candidate_score(analysis) == 35


def test_metadata_ranking_score_is_supported():
    analysis = _analysis(
        match_score=10,
        metadata={"ranking_score": 30},
    )

    assert get_official_candidate_score(analysis) == 30


def test_colab_scores_are_resolved_for_streamlit_views():
    raw_fit_scores = [50, 35, 10, 10]
    consolidated_scores = [86, 66, 30, 25]

    analyses = [
        _analysis(
            match_score=fit,
            ranking_score=ranking,
        )
        for fit, ranking in zip(
            raw_fit_scores,
            consolidated_scores,
        )
    ]

    assert [
        get_official_candidate_score(analysis)
        for analysis in analyses
    ] == [86, 66, 30, 25]


def test_legacy_upload_fit_selection_remains_unchanged():
    service = RecruitmentUploadSessionService()

    assert service._first_number(50, 86, 0.0) == 50
    assert service._first_number(0, 41, 0.0) == 0
