"""Regression tests for TalentCopilot's dual score model."""

from types import SimpleNamespace

from talentcopilot.models.recruitment_session import (
    CandidateAnalysisState,
    CandidateAnalysisStatus,
)
from talentcopilot.services.official_score_service import (
    get_official_candidate_score,
)
from talentcopilot.services.recruitment_upload_session_service import (
    RecruitmentUploadSessionService,
)


def _analysis(match_score, ranking_score=None):
    return CandidateAnalysisState(
        candidate_name="Candidate",
        candidate_id="candidate-1",
        status=CandidateAnalysisStatus.ANALYZED,
        match_score=match_score,
        ranking_score=ranking_score,
    )


def test_raw_fit_and_consolidated_ranking_are_preserved():
    analysis = _analysis(50, 86)

    assert analysis.match_score == 50
    assert analysis.ranking_score == 86
    assert analysis.official_match_score == 86


def test_official_score_falls_back_to_raw_fit():
    analysis = _analysis(35)

    assert analysis.match_score == 35
    assert analysis.ranking_score is None
    assert analysis.official_match_score == 35


def test_zero_ranking_score_is_preserved():
    analysis = _analysis(41, 0)

    assert analysis.match_score == 41
    assert analysis.ranking_score == 0
    assert analysis.official_match_score == 0


def test_recruiter_score_resolver_uses_consolidated_score():
    assert get_official_candidate_score(_analysis(50, 86)) == 86
    assert get_official_candidate_score(_analysis(35, 66)) == 66
    assert get_official_candidate_score(_analysis(10, 30)) == 30
    assert get_official_candidate_score(_analysis(10, 25)) == 25


def test_legacy_raw_fit_selection_remains_unchanged():
    service = RecruitmentUploadSessionService()

    assert service._first_number(50, 86, 0.0) == 50
    assert service._first_number(0, 41, 0.0) == 0


def test_optional_number_preserves_missing_value():
    service = RecruitmentUploadSessionService()

    assert service._optional_number(None) is None
    assert service._optional_number(86) == 86.0
    assert service._optional_number("66") == 66.0
    assert service._optional_number("invalid") is None
