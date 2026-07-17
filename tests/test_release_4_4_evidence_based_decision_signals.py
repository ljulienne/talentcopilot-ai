from pathlib import Path

from talentcopilot.models.recruitment_session import (
    CandidateAnalysisState,
    CandidateAnalysisStatus,
    RecruitmentSession,
    SessionStatus,
)
from talentcopilot.services.candidate_decision_signal_service import (
    CandidateDecisionSignalService,
)
from talentcopilot.services.comparison_workspace_service import (
    ComparisonWorkspaceService,
)


def _analysis(name, candidate_id, score, confidence, rank):
    return CandidateAnalysisState(
        candidate_name=name,
        candidate_id=candidate_id,
        status=CandidateAnalysisStatus.ANALYZED,
        match_score=score,
        decision_score=score - 5,
        rank=rank,
        score_breakdown={"confidence": confidence},
    )


def _session():
    analyses = [
        _analysis("Louis", "louis", 86, 84, 1),
        _analysis("Vincent", "vincent", 66, 76, 2),
        _analysis("Loretta", "loretta", 30, 71, 3),
        _analysis("Zelma", "zelma", 25, 71, 4),
    ]
    return RecruitmentSession(
        session_id="release-4-4",
        job={
            "title": "HRIS Project Manager",
            "required_skills": [
                "HRIS",
                "Project Management",
                "API Integration",
                "Change Management",
            ],
        },
        candidates=[
            {
                "candidate_id": "louis",
                "name": "Louis",
                "skills": ["HRIS", "Project Management", "API Integration"],
                "achievements": ["Led an HRIS rollout for 4,000 employees."],
            },
            {
                "candidate_id": "vincent",
                "name": "Vincent",
                "skills": ["HRIS", "Project Management"],
                "achievements": ["Supported a multi-country implementation."],
            },
            {
                "candidate_id": "loretta",
                "name": "Loretta",
                "skills": ["Recruitment"],
                "achievements": [],
            },
            {
                "candidate_id": "zelma",
                "name": "Zelma",
                "skills": ["Reporting"],
                "achievements": [],
            },
        ],
        status=SessionStatus.COMPLETED,
        analyses=analyses,
    )


def test_release_4_4_preserves_canonical_scores_and_ranks():
    report = ComparisonWorkspaceService().build(_session())
    assert [item.match_score for item in report.candidates] == [86, 66, 30, 25]
    assert [item.rank for item in report.candidates] == [1, 2, 3, 4]
    assert [item.ai_confidence for item in report.candidates] == [84, 76, 71, 71]


def test_release_4_4_recommendations_vary_with_official_match():
    report = ComparisonWorkspaceService().build(_session())
    assert [item.recommendation for item in report.candidates] == [
        "Strong shortlist",
        "Shortlist with targeted validation",
        "Low fit — significant gaps",
        "Low fit — significant gaps",
    ]


def test_release_4_4_strengths_and_risks_are_evidence_based():
    report = ComparisonWorkspaceService().build(_session())
    assert "HRIS" in report.candidates[0].key_strength
    assert "API Integration" in report.candidates[0].key_strength
    assert "HRIS" in report.candidates[2].key_risk
    assert "Project Management" in report.candidates[2].key_risk
    assert report.candidates[0].key_strength != report.candidates[2].key_strength


def test_release_4_4_generic_placeholders_are_absent():
    report = ComparisonWorkspaceService().build(_session())
    forbidden = {"Review", "Relevant experience", "Requires validation"}
    for candidate in report.candidates:
        assert candidate.recommendation not in forbidden
        assert candidate.key_strength not in forbidden
        assert candidate.key_risk not in forbidden


def test_release_4_4_low_confidence_requires_manual_review():
    session = _session()
    session.analyses[0].score_breakdown["confidence"] = 40
    signals = CandidateDecisionSignalService().build(session.analyses[0], session)
    assert signals.recommendation == "Manual review required"


def test_release_4_4_production_trace_is_removed():
    source = Path("talentcopilot/ui/recruitment_decision_workspace.py").read_text()
    assert "Official score propagation trace" not in source
    assert "Temporary Release 4.2.3 diagnostic" not in source
    assert "Production input contract" not in source
