from dataclasses import replace
from pathlib import Path

from talentcopilot.services.candidate_intelligence_view_service import CandidateDecisionBrief
from talentcopilot.services.executive_decision_intelligence_service import (
    ExecutiveDecisionIntelligenceService,
)
from talentcopilot.services.executive_decision_pdf_service import (
    ExecutiveDecisionPdfService,
)


def _brief(score=86, rank=1, confidence=84, evidence_coverage=80):
    return CandidateDecisionBrief(
        candidate_id="louis",
        candidate_name="Louis",
        official_match_score=score,
        official_rank=rank,
        recommendation="Strong shortlist",
        recommendation_label="Proceed with human validation",
        confidence_score=confidence,
        confidence_label="High",
        evidence_coverage=evidence_coverage,
        potential_signal=82,
        executive_summary="Strong HRIS delivery profile.",
        recommendation_explanation="Evidence supports progression.",
        strengths=("HRIS programme leadership", "API integration"),
        transferable_evidence=("Change management",),
        missing_evidence=("Confirm global rollout ownership",),
        hiring_risks=("Delivery scope: validate personal ownership",),
        interview_priorities=("Validate API architecture ownership",),
        evidence_summary="Evidence is available.",
    )


def test_release_4_5a_preserves_canonical_results():
    source = _brief()
    result = ExecutiveDecisionIntelligenceService().build(source)
    assert result.official_match_score == 86
    assert result.official_rank == 1
    assert result.ai_confidence == 84


def test_release_4_5a_generates_decision_ready_outputs():
    result = ExecutiveDecisionIntelligenceService().build(_brief())
    assert result.recommendation == "Strong Hire"
    assert result.business_impact == "High"
    assert result.next_action.startswith("Invite to a structured final interview")
    assert result.ramp_up == "1–2 months"
    assert len(result.risks) >= 4
    assert result.interview_priorities


def test_release_4_5a_low_confidence_forces_manual_review():
    result = ExecutiveDecisionIntelligenceService().build(
        replace(_brief(), confidence_score=40)
    )
    assert result.recommendation == "Manual review required"
    assert result.decision_status == "LOW CONFIDENCE"
    assert result.business_impact == "Limited"


def test_release_4_5a_lower_scores_do_not_receive_shortlist_recommendation():
    result = ExecutiveDecisionIntelligenceService().build(
        replace(_brief(), official_match_score=30, official_rank=3)
    )
    assert result.recommendation == "Do not prioritize"
    assert result.ramp_up == "Long ramp-up"
    assert result.official_rank == 3


def test_release_4_5a_pdf_is_valid():
    result = ExecutiveDecisionIntelligenceService().build(_brief())
    content = ExecutiveDecisionPdfService().generate(result)
    assert content.startswith(b"%PDF")
    assert len(content) > 1500


def test_release_4_5a_candidate_ui_integrates_advisor_without_matching():
    source = Path("talentcopilot/ui/candidate_workspace.py").read_text()
    assert "AI Executive Advisor" in source
    assert "ExecutiveDecisionIntelligenceService" in source
    assert "ExecutiveDecisionPdfService" in source
    assert "Download Executive Decision Brief (PDF)" in source
    assert "MatchingEngine(" not in source
    assert "FitIntelligenceEngine(" not in source
