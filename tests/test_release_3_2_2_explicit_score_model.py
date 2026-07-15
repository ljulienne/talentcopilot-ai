"""Tests for the explicit TalentCopilot candidate score model."""

from dataclasses import dataclass, field

from talentcopilot.models.recruitment_session import (
    CandidateAnalysisState,
    CandidateAnalysisStatus,
)
from talentcopilot.services.recruitment_upload_session_service import (
    RecruitmentUploadSessionService,
)
from talentcopilot.services.upload_text_reader_service import (
    UploadedTextDocument,
)


@dataclass
class FakeRankedCandidate:
    candidate_name: str
    rank: int
    fit_score: float | None
    ranking_score: float | None
    recommendation: str = "Review"
    rationale: str = "Evidence-based assessment."
    confidence_score: float = 70
    matching_output: object = None


@dataclass
class FakeRankingOutput:
    role_title: str
    ranked_candidates: list = field(default_factory=list)


@dataclass
class FakeReport:
    status: str
    job_document: object
    candidate_documents: list
    ranking_output: object


def _report(fit_score, ranking_score):
    job = UploadedTextDocument(
        filename="job.txt",
        file_type="txt",
        text="HRIS Lead\nRequirements\nHRIS",
    )

    candidate = UploadedTextDocument(
        filename="candidate.txt",
        file_type="txt",
        text="Candidate Example\n5 years experience\nSkills\nHRIS",
    )

    output = FakeRankingOutput(
        role_title="HRIS Lead",
        ranked_candidates=[
            FakeRankedCandidate(
                candidate_name="Candidate Example",
                rank=1,
                fit_score=fit_score,
                ranking_score=ranking_score,
            )
        ],
    )

    return FakeReport(
        status="Ready",
        job_document=job,
        candidate_documents=[candidate],
        ranking_output=output,
    )


def test_model_keeps_role_fit_and_decision_score_distinct():
    analysis = CandidateAnalysisState(
        candidate_name="Candidate",
        candidate_id="candidate-1",
        status=CandidateAnalysisStatus.ANALYZED,
        match_score=50,
        decision_score=86,
    )

    assert analysis.match_score == 50
    assert analysis.official_match_score == 50
    assert analysis.decision_score == 86
    assert analysis.official_decision_score == 86


def test_upload_session_preserves_both_pipeline_scores():
    session = RecruitmentUploadSessionService().from_report(
        _report(50, 86)
    )

    analysis = session.ranked_analyses[0]

    assert analysis.match_score == 50
    assert analysis.official_match_score == 50
    assert analysis.decision_score == 86
    assert analysis.official_decision_score == 86
    assert analysis.score_breakdown["role_fit"] == 50
    assert analysis.score_breakdown["decision_score"] == 86


def test_zero_decision_score_is_a_valid_value():
    session = RecruitmentUploadSessionService().from_report(
        _report(41, 0)
    )

    analysis = session.ranked_analyses[0]

    assert analysis.match_score == 41
    assert analysis.decision_score == 0
    assert analysis.official_decision_score == 0
    assert analysis.score_breakdown["decision_score"] == 0


def test_missing_decision_score_remains_missing():
    session = RecruitmentUploadSessionService().from_report(
        _report(35, None)
    )

    analysis = session.ranked_analyses[0]

    assert analysis.match_score == 35
    assert analysis.decision_score is None
    assert analysis.official_decision_score is None
    assert "decision_score" not in analysis.score_breakdown


def test_fit_score_falls_back_only_when_it_is_missing():
    session = RecruitmentUploadSessionService().from_report(
        _report(None, 66)
    )

    analysis = session.ranked_analyses[0]

    # Compatibility fallback for pipelines that do not expose fit_score.
    assert analysis.match_score == 66
    assert analysis.decision_score == 66


def test_optional_number_preserves_none_and_zero():
    service = RecruitmentUploadSessionService()

    assert service._optional_number(None) is None
    assert service._optional_number(0) == 0.0
    assert service._optional_number("86") == 86.0
    assert service._optional_number("invalid") is None
