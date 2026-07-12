from talentcopilot.models.candidate_intelligence import CandidateRiskType
from talentcopilot.models.candidate_workspace import (
    CandidateEvidence,
    CandidateRisk,
    CandidateSkill,
    CandidateWorkspaceReport,
)
from talentcopilot.services.candidate_intelligence import CandidateIntelligenceService
from talentcopilot.ui.candidate_workspace import render_candidate_workspace


def _report(**overrides):
    values = {
        "candidate_name": "Alice Martin",
        "rank": 1,
        "match_score": 86.0,
        "recommendation": "Proceed",
        "executive_summary": "Strong transformation and stakeholder profile.",
        "skills": [
            CandidateSkill("Transformation Leadership", 90, "Led a global ERP programme."),
            CandidateSkill("Stakeholder Management", 82, "Coordinated executive stakeholders."),
            CandidateSkill("Budget Ownership", 68, ""),
        ],
        "evidence": [
            CandidateEvidence("ERP transformation", "Delivered a multi-country rollout.", "High"),
            CandidateEvidence("Executive influence", "Presented to the steering committee.", "High"),
        ],
        "risks": [
            CandidateRisk("Budget ownership", "Annual budget amount is not documented.", "Medium"),
        ],
        "interview_focus": ["Validate budget ownership with a quantified example."],
    }
    values.update(overrides)
    return CandidateWorkspaceReport(**values)


def test_candidate_intelligence_is_importable():
    assert callable(render_candidate_workspace)
    assert CandidateIntelligenceService


def test_existing_match_score_is_preserved():
    snapshot = CandidateIntelligenceService().build(_report(match_score=87.5))
    assert snapshot.mission_fit == 87.5


def test_intelligence_exposes_distinct_decision_signals():
    snapshot = CandidateIntelligenceService().build(_report())
    assert 0 <= snapshot.evidence_coverage <= 100
    assert 0 <= snapshot.decision_confidence <= 100
    assert 0 <= snapshot.potential_signal <= 100
    assert snapshot.strengths
    assert snapshot.interview_strategy


def test_missing_information_is_not_presented_as_candidate_failure():
    snapshot = CandidateIntelligenceService().build(_report())
    unknowns = [risk for risk in snapshot.risks if risk.risk_type is CandidateRiskType.UNKNOWN]
    assert unknowns
    assert all(risk.severity == "Unknown" for risk in unknowns)


def test_low_evidence_reduces_decision_confidence():
    rich = CandidateIntelligenceService().build(_report())
    limited = CandidateIntelligenceService().build(
        _report(evidence=[], skills=[], risks=[])
    )
    assert limited.evidence_coverage < rich.evidence_coverage
    assert limited.decision_confidence < rich.decision_confidence
    assert "human validation" in limited.recommendation_explanation.lower() or "structured interview" in limited.recommendation_explanation.lower()


def test_potential_signal_is_explicitly_non_decisional():
    snapshot = CandidateIntelligenceService().build(_report())
    assert snapshot.potential_signal >= 0
    # Product guardrail: the UI wording is asserted in source through the public label.
    source = open("talentcopilot/ui/candidate_workspace.py", encoding="utf-8").read()
    assert "Development signal — not a hiring decision" in source
    assert "do not evaluate a person's worth" in source
