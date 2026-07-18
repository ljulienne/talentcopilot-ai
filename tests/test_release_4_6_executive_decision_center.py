from types import SimpleNamespace

from talentcopilot.services.executive_decision_center_service import (
    ExecutiveDecisionCenterService,
)
from talentcopilot.services.executive_decision_intelligence_service import (
    ExecutiveDecisionIntelligenceService,
)
from talentcopilot.services.executive_decision_pdf_service import (
    ExecutiveDecisionPdfService,
)


def _skill(name, level, evidence=""):
    return SimpleNamespace(name=name, level=level, evidence=evidence)


def _evidence(title, detail, strength="Strong"):
    return SimpleNamespace(title=title, detail=detail, strength=strength)


def _report(name="Alice", score=78, rank=1):
    return SimpleNamespace(
        candidate_id=name.lower(),
        candidate_name=name,
        official_match_score=score,
        match_score=score,
        official_rank=rank,
        rank=rank,
        recommendation="Proceed",
        score_breakdown={"confidence": 82},
        skills=[
            _skill("HRIS", 90, "Implemented Workday globally"),
            _skill("Transformation", 76, "Led adoption programme"),
        ],
        evidence=[
            _evidence("HRIS delivery", "Implemented Workday for 12 countries"),
            _evidence("Adoption", "Increased adoption by 35%"),
            _evidence("Leadership", "Led a team of 10 consultants"),
            _evidence("Governance", "Managed steering committee decisions"),
        ],
        interview_focus=("Validate international leadership scope.",),
    )


def _intelligence(missing=()):
    return SimpleNamespace(
        decision_confidence=82,
        evidence_coverage=84,
        strengths=("HRIS delivery", "Transformation leadership"),
        missing_evidence=missing,
        interview_strategy=("Validate international leadership scope.",),
        evidence_summary="Evidence is specific and role-relevant.",
        risks=(),
    )


def _executive(report, intelligence):
    return ExecutiveDecisionIntelligenceService().build(report, intelligence)


def test_preserves_canonical_score_rank_and_confidence():
    report = _report(score=78, rank=2)
    intelligence = _intelligence()
    center = ExecutiveDecisionCenterService().build(
        report, intelligence, _executive(report, intelligence)
    )
    assert center.official_match_score == 78
    assert center.official_rank == 2
    assert center.ai_confidence == 82


def test_decision_readiness_is_evidence_completeness_not_match_score():
    report = _report(score=78)
    complete = ExecutiveDecisionCenterService().build(
        report, _intelligence(), _executive(report, _intelligence())
    )
    incomplete_intelligence = _intelligence(("English level", "Salary expectations"))
    incomplete = ExecutiveDecisionCenterService().build(
        report, incomplete_intelligence, _executive(report, incomplete_intelligence)
    )
    assert complete.decision_readiness > incomplete.decision_readiness
    assert complete.official_match_score == incomplete.official_match_score


def test_evidence_quality_detects_direct_outcomes():
    report = _report()
    intelligence = _intelligence()
    center = ExecutiveDecisionCenterService().build(
        report, intelligence, _executive(report, intelligence)
    )
    assert any(item.quality == "Direct" for item in center.evidence_quality)


def test_confidence_explanation_and_timeline_are_present():
    report = _report()
    intelligence = _intelligence()
    center = ExecutiveDecisionCenterService().build(
        report, intelligence, _executive(report, intelligence)
    )
    assert len(center.confidence_reasons) >= 3
    assert [item.period for item in center.timeline] == [
        "Week 1", "Week 2", "Month 1", "Month 3", "Month 6"
    ]


def test_peer_comparison_does_not_recalculate_scores():
    selected = _report("Alice", 78, 1)
    peer = _report("Bob", 70, 2)
    intelligence = _intelligence()
    center = ExecutiveDecisionCenterService().build(
        selected,
        intelligence,
        _executive(selected, intelligence),
        peer_reports=[selected, peer],
    )
    assert len(center.comparison) == 1
    assert "8 point(s) ahead" in center.comparison[0].headline
    assert center.official_match_score == 78


def test_pdf_v2_contains_valid_pdf_bytes():
    report = _report()
    intelligence = _intelligence()
    executive = _executive(report, intelligence)
    center = ExecutiveDecisionCenterService().build(report, intelligence, executive)
    pdf = ExecutiveDecisionPdfService().generate(executive, center=center)
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 1000


def test_candidate_workspace_integrates_decision_center():
    from pathlib import Path
    source = Path("talentcopilot/ui/candidate_workspace.py").read_text()
    assert "ExecutiveDecisionCenterService" in source
    assert "Executive Decision Center" in source
    assert "Decision Readiness" in source
    assert "Evidence Quality" in source
