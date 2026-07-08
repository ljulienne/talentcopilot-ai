from talentcopilot.decision_core.evidence_graph_builder import EvidenceGraphBuilder
from talentcopilot.decision_core.evidence_intelligence_engine import EvidenceIntelligenceEngine


def test_evidence_intelligence_strong_evidence():
    graph = EvidenceGraphBuilder().build_from_candidate_dict(
        {
            "name": "Alice Martin",
            "skills": ["Project Management", "Stakeholder Management"],
            "years_experience": 8,
            "achievements": ["Improved adoption by 35%"],
        },
        "Transformation Lead",
    )

    report = EvidenceIntelligenceEngine().evaluate(graph)

    assert report.evidence_quality_score > 0
    assert report.evidence_coverage_score == 100
    assert report.evidence_readiness_score >= 60
    assert report.strengths
    assert report.status in {"Strong evidence", "Usable evidence", "Limited evidence"}


def test_evidence_intelligence_detects_gaps():
    graph = EvidenceGraphBuilder().build_from_candidate_dict(
        {"name": "David Smith", "skills": []},
        "Transformation Lead",
    )

    report = EvidenceIntelligenceEngine().evaluate(graph)

    assert report.gaps
    assert report.evidence_readiness_score < 85


def test_evidence_intelligence_adds_trace_step():
    from talentcopilot.decision_core.decision_trace_service import DecisionTraceService

    graph = EvidenceGraphBuilder().build_from_candidate_dict(
        {"name": "Alice Martin", "skills": ["Leadership"]},
        "Transformation Lead",
    )
    trace = DecisionTraceService().initialize_trace("Alice Martin", graph)
    report = EvidenceIntelligenceEngine().evaluate(graph)
    EvidenceIntelligenceEngine().add_trace_step(trace, graph, report)

    actions = [step.action for step in trace.steps]
    assert "EVALUATE_EVIDENCE_QUALITY" in actions
