"""Release 3.3 regression shield for one public candidate score."""
from pathlib import Path
from types import SimpleNamespace

from talentcopilot.models.recruitment_session import (
    CandidateAnalysisState,
    CandidateAnalysisStatus,
    RecruitmentSession,
    SessionStatus,
)
from talentcopilot.services.candidate_intelligence_view_service import CandidateIntelligenceViewService
from talentcopilot.services.comparison_workspace_service import ComparisonWorkspaceService


def _analysis(match=86, confidence=84, decision=77, rank=1):
    return CandidateAnalysisState(
        candidate_name="Louis Julienne",
        candidate_id="candidate-louis",
        status=CandidateAnalysisStatus.ANALYZED,
        match_score=match,
        decision_score=decision,
        rank=rank,
        score_breakdown={"confidence": confidence},
    )


def _session():
    return RecruitmentSession(
        session_id="release-3-3",
        job={"title": "HRIS Project Manager"},
        candidates=[{"candidate_id": "candidate-louis", "name": "Louis Julienne"}],
        status=SessionStatus.COMPLETED,
        analyses=[_analysis()],
    )


def test_candidate_state_has_one_official_score_and_ai_confidence():
    analysis = _analysis()
    assert analysis.official_match_score == 86
    assert analysis.official_confidence_score == 84
    assert analysis.official_rank == 1
    assert analysis.decision_score == 77


def test_comparison_uses_official_match_and_ai_confidence():
    report = ComparisonWorkspaceService().build(_session())
    candidate = report.candidates[0]
    assert candidate.match_score == 86
    assert candidate.ai_confidence == 84
    assert candidate.decision_score == 77


def test_candidate_intelligence_uses_canonical_upload_confidence():
    report = SimpleNamespace(
        candidate_id="candidate-louis",
        candidate_name="Louis Julienne",
        official_match_score=86,
        official_rank=1,
        recommendation="Review",
        executive_summary="Summary",
        score_breakdown={"confidence": 84},
        skills=[],
        interview_focus=[],
    )
    intelligence = SimpleNamespace(
        decision_confidence=49,
        recommendation="Review",
        strengths=(),
        missing_evidence=(),
        risks=(),
        interview_strategy=(),
        evidence_coverage=47,
        potential_signal=60,
        recommendation_explanation="Validate evidence.",
        evidence_summary="Evidence available.",
    )
    brief = CandidateIntelligenceViewService().build(report, intelligence)
    assert brief.official_match_score == 86
    assert brief.confidence_score == 84
    assert brief.official_rank == 1


def test_user_facing_ui_has_no_competing_score_labels():
    repo = Path(__file__).resolve().parents[1]
    comparison = (repo / "talentcopilot/ui/comparison_workspace.py").read_text(encoding="utf-8")
    assert '"Official Match"' in comparison
    assert '"AI Confidence"' in comparison
    assert '"Role Fit"' not in comparison
    assert '"Decision Score"' not in comparison

    ui_sources = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in (repo / "talentcopilot/ui").rglob("*.py")
    )
    assert "Decision Confidence" not in ui_sources
