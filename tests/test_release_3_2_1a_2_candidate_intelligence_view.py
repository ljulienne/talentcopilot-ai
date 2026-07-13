from talentcopilot.models.candidate_intelligence import (
    CandidateIntelligenceRisk,
    CandidateIntelligenceSnapshot,
    CandidateRiskType,
)
from talentcopilot.models.candidate_workspace import (
    CandidateRisk,
    CandidateSkill,
    CandidateWorkspaceReport,
)
from talentcopilot.services.candidate_intelligence_view_service import (
    CandidateIntelligenceViewService,
)


def _report():
    return CandidateWorkspaceReport(
        candidate_name="Louis Julienne",
        candidate_id="candidate-louis",
        rank=2,
        match_score=50.0,
        recommendation="Proceed",
        executive_summary="Strong transferable HRIS background with focused validation required.",
        skills=[
            CandidateSkill(
                "International HRIS",
                88,
                "Led multi-country HRIS deployments.",
            ),
            CandidateSkill(
                "Power BI",
                72,
                "Delivered HR analytics dashboards.",
            ),
            CandidateSkill(
                "SuccessFactors",
                35,
                "",
            ),
        ],
        risks=[
            CandidateRisk(
                "SuccessFactors depth",
                "Direct implementation depth is not explicit.",
                "Medium",
            ),
        ],
        interview_focus=[
            "Validate SuccessFactors functional depth.",
            "Clarify ownership of Core HR decisions.",
        ],
    )


def _intelligence():
    return CandidateIntelligenceSnapshot(
        candidate_name="Louis Julienne",
        mission_fit=50.0,
        evidence_coverage=68,
        decision_confidence=61,
        potential_signal=77,
        recommendation="Proceed",
        recommendation_explanation=(
            "The official mission fit is supported by international HRIS "
            "experience, while platform-specific depth requires validation."
        ),
        strengths=("International HRIS",),
        risks=(
            CandidateIntelligenceRisk(
                title="SuccessFactors depth",
                detail="Evidence remains limited.",
                severity="Unknown",
                risk_type=CandidateRiskType.UNKNOWN,
            ),
        ),
        missing_evidence=(
            "SAP SuccessFactors depth",
            "ICR campaign ownership",
        ),
        interview_strategy=(
            "Validate SuccessFactors functional depth.",
            "Clarify ownership of Core HR decisions.",
        ),
        evidence_summary="4 usable evidence items.",
    )


def test_premium_view_preserves_official_score_and_rank():
    view = CandidateIntelligenceViewService().build(
        _report(),
        _intelligence(),
    )

    assert view.official_match_score == 50.0
    assert view.official_rank == 2
    assert view.candidate_id == "candidate-louis"


def test_premium_view_organises_existing_decision_signals():
    view = CandidateIntelligenceViewService().build(
        _report(),
        _intelligence(),
    )

    assert view.confidence_score == 61
    assert view.confidence_label == "Moderate"
    assert view.strengths == ("International HRIS",)
    assert any(
        item.startswith("Power BI")
        for item in view.transferable_evidence
    )
    assert "SAP SuccessFactors depth" in view.missing_evidence
    assert view.interview_priorities


def test_premium_view_uses_prudent_risk_language_from_existing_output():
    view = CandidateIntelligenceViewService().build(
        _report(),
        _intelligence(),
    )

    assert view.hiring_risks
    assert "Evidence remains limited" in view.hiring_risks[0]
