from dataclasses import dataclass, field
from types import SimpleNamespace

from talentcopilot.services.recruitment_upload_session_service import RecruitmentUploadSessionService
from talentcopilot.services.upload_text_reader_service import UploadedTextDocument


@dataclass
class FakeRankedCandidate:
    candidate_name: str
    rank: int
    fit_score: float
    ranking_score: float
    recommendation: str = "Interview"
    rationale: str = "Evidence-based fit."
    confidence_score: float = 75
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


def _report():
    job = UploadedTextDocument(
        filename="job.txt",
        file_type="txt",
        text="HRIS Lead\nRequirements\nHRIS; Project Management; Stakeholder Management",
    )
    alice = UploadedTextDocument(
        filename="alice.txt",
        file_type="txt",
        text="Alice Martin\n8 years experience\nSkills\nHRIS; Project Management",
    )
    david = UploadedTextDocument(
        filename="david.txt",
        file_type="txt",
        text="David Smith\n4 years experience\nSkills\nReporting; Excel",
    )
    output = FakeRankingOutput(
        role_title="HRIS Lead",
        ranked_candidates=[
            FakeRankedCandidate("Alice Martin", 1, 82.5, 84.0),
            FakeRankedCandidate("David Smith", 2, 21.0, 24.0, recommendation="Review"),
        ],
    )
    return FakeReport("Ready", job, [alice, david], output)


def test_upload_result_becomes_official_recruitment_session():
    session = RecruitmentUploadSessionService().from_report(_report())

    assert session.role_title == "HRIS Lead"
    assert session.metadata["source"] == "real_upload"
    assert session.candidate_count == 2
    assert session.analyzed_count == 2
    assert [item.candidate_name for item in session.ranked_analyses] == ["Alice Martin", "David Smith"]
    assert [item.match_score for item in session.ranked_analyses] == [82.5, 21.0]
    assert [item.ranking_score for item in session.ranked_analyses] == [84.0, 24.0]
    assert [item.official_match_score for item in session.ranked_analyses] == [84.0, 24.0]
    assert [item.rank for item in session.ranked_analyses] == [1, 2]


def test_uploaded_candidates_receive_unique_stable_ids():
    session = RecruitmentUploadSessionService().from_report(_report())
    candidate_ids = [candidate["candidate_id"] for candidate in session.candidates]
    analysis_ids = [analysis.candidate_id for analysis in session.ranked_analyses]

    assert len(candidate_ids) == len(set(candidate_ids))
    assert candidate_ids == analysis_ids


def test_zero_official_fit_is_preserved():
    report = _report()
    report.ranking_output.ranked_candidates[1].fit_score = 0
    report.ranking_output.ranked_candidates[1].ranking_score = 41

    session = RecruitmentUploadSessionService().from_report(report)
    david = session.get_analysis("David Smith")

    assert david.match_score == 0
    assert david.ranking_score == 41
    assert david.official_match_score == 41
    assert david.rank == 2
