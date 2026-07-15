"""Comparison Workspace dual-score regression tests."""

from pathlib import Path

from talentcopilot.models.recruitment_session import (
    CandidateAnalysisState,
    CandidateAnalysisStatus,
    RecruitmentSession,
    SessionStatus,
)
from talentcopilot.services.comparison_workspace_service import (
    ComparisonWorkspaceService,
)


def _session(decision_score=86):
    analysis = CandidateAnalysisState(
        candidate_name="Louis Julienne",
        candidate_id="candidate-louis",
        status=CandidateAnalysisStatus.ANALYZED,
        match_score=50,
        decision_score=decision_score,
        rank=1,
    )

    return RecruitmentSession(
        session_id="comparison-test",
        job={
            "title": "HRIS Project Manager",
            "required_skills": ["HRIS"],
        },
        candidates=[
            {
                "candidate_id": "candidate-louis",
                "name": "Louis Julienne",
            }
        ],
        status=SessionStatus.COMPLETED,
        analyses=[analysis],
    )


def test_comparison_keeps_role_fit_and_decision_score_distinct():
    report = ComparisonWorkspaceService().build(
        _session(decision_score=86)
    )

    candidate = report.candidates[0]

    assert candidate.match_score == 50
    assert candidate.decision_score == 86
    assert candidate.rank == 1


def test_missing_decision_score_remains_missing():
    report = ComparisonWorkspaceService().build(
        _session(decision_score=None)
    )

    candidate = report.candidates[0]

    assert candidate.match_score == 50
    assert candidate.decision_score is None


def test_zero_decision_score_is_preserved():
    report = ComparisonWorkspaceService().build(
        _session(decision_score=0)
    )

    candidate = report.candidates[0]

    assert candidate.match_score == 50
    assert candidate.decision_score == 0


def test_comparison_ui_uses_canonical_score_labels():
    """Release 3.3 exposes one match score and one AI confidence."""

    ui_file = (
        Path(__file__).resolve().parents[1]
        / "talentcopilot"
        / "ui"
        / "comparison_workspace.py"
    )

    source = ui_file.read_text(encoding="utf-8")

    assert '"Official Match"' in source
    assert '"AI Confidence"' in source
    assert "c.match_score" in source
    assert "c.ai_confidence" in source

    # Former competing score labels must not return to recruiter UX.
    assert '"Role Fit"' not in source
    assert '"Decision Score"' not in source
