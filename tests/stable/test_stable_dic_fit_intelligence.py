from talentcopilot.decision_core.evidence_graph_builder import EvidenceGraphBuilder
from talentcopilot.decision_core.evidence_intelligence_engine import EvidenceIntelligenceEngine
from talentcopilot.decision_core.fit_intelligence_engine import FitIntelligenceEngine
from talentcopilot.decision_core.fit_intelligence_models import RoleRequirements


def test_fit_intelligence_strong_fit():
    candidate = {
        "name": "Alice Martin",
        "skills": ["Project Management", "Stakeholder Management", "HRIS"],
        "years_experience": 8,
        "achievements": ["Improved adoption by 35%"],
    }
    role = RoleRequirements(
        role_title="Transformation Lead",
        required_skills=["Project Management", "Stakeholder Management"],
        preferred_skills=["HRIS"],
        minimum_years_experience=6,
    )

    graph = EvidenceGraphBuilder().build_from_candidate_dict(candidate, role.role_title)
    evidence = EvidenceIntelligenceEngine().evaluate(graph)
    report = FitIntelligenceEngine().evaluate(graph, role, evidence)

    assert report.fit_score >= 75
    assert report.drivers
    assert report.status in {"Strong fit", "Good fit"}


def test_fit_intelligence_detects_required_skill_gaps():
    candidate = {
        "name": "David Smith",
        "skills": ["Graphic Design"],
        "years_experience": 1,
    }
    role = RoleRequirements(
        role_title="Transformation Lead",
        required_skills=["Project Management", "Stakeholder Management"],
        minimum_years_experience=6,
    )

    graph = EvidenceGraphBuilder().build_from_candidate_dict(candidate, role.role_title)
    evidence = EvidenceIntelligenceEngine().evaluate(graph)
    report = FitIntelligenceEngine().evaluate(graph, role, evidence)

    assert report.fit_score < 50
    assert report.gaps
    assert any(gap.severity == "High" for gap in report.gaps)


def test_fit_intelligence_adds_trace_step():
    from talentcopilot.decision_core.decision_trace_service import DecisionTraceService

    candidate = {"name": "Alice Martin", "skills": ["Leadership"], "years_experience": 5}
    role = RoleRequirements("Leadership Role", required_skills=["Leadership"], minimum_years_experience=3)
    graph = EvidenceGraphBuilder().build_from_candidate_dict(candidate, role.role_title)
    trace = DecisionTraceService().initialize_trace("Alice Martin", graph)
    evidence = EvidenceIntelligenceEngine().evaluate(graph)
    report = FitIntelligenceEngine().evaluate(graph, role, evidence)
    FitIntelligenceEngine().add_trace_step(trace, graph, report)

    assert "EVALUATE_CANDIDATE_FIT" in [step.action for step in trace.steps]
