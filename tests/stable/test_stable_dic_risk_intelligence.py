from talentcopilot.decision_core.evidence_graph_builder import EvidenceGraphBuilder
from talentcopilot.decision_core.evidence_intelligence_engine import EvidenceIntelligenceEngine
from talentcopilot.decision_core.fit_intelligence_engine import FitIntelligenceEngine
from talentcopilot.decision_core.fit_intelligence_models import RoleRequirements
from talentcopilot.decision_core.risk_intelligence_engine import RiskIntelligenceEngine


def _reports(candidate, role):
    graph = EvidenceGraphBuilder().build_from_candidate_dict(candidate, role.role_title)
    evidence = EvidenceIntelligenceEngine().evaluate(graph)
    fit = FitIntelligenceEngine().evaluate(graph, role, evidence)
    risk = RiskIntelligenceEngine().evaluate(graph, role, evidence, fit)
    return graph, evidence, fit, risk


def test_risk_intelligence_low_risk_for_strong_candidate():
    candidate = {
        "name": "Alice Martin",
        "skills": ["Project Management", "Stakeholder Management"],
        "years_experience": 8,
        "achievements": ["Improved adoption by 35%"],
    }
    role = RoleRequirements(
        "Transformation Lead",
        required_skills=["Project Management", "Stakeholder Management"],
        minimum_years_experience=6,
    )

    _, _, _, risk = _reports(candidate, role)

    assert risk.risk_level in {"Low", "Medium"}
    assert risk.risk_score < 50


def test_risk_intelligence_high_risk_for_missing_critical_skills():
    candidate = {"name": "David Smith", "skills": ["Graphic Design"], "years_experience": 1}
    role = RoleRequirements(
        "Transformation Lead",
        required_skills=["Project Management", "Stakeholder Management"],
        minimum_years_experience=6,
    )

    _, _, _, risk = _reports(candidate, role)

    assert risk.risk_level in {"High", "Critical"}
    assert risk.risk_factors
    assert risk.mitigation_actions


def test_risk_intelligence_adds_trace_step():
    from talentcopilot.decision_core.decision_trace_service import DecisionTraceService

    candidate = {"name": "Alice Martin", "skills": ["Leadership"], "years_experience": 5}
    role = RoleRequirements("Leadership Role", required_skills=["Leadership"], minimum_years_experience=3)
    graph, evidence, fit, risk = _reports(candidate, role)
    trace = DecisionTraceService().initialize_trace("Alice Martin", graph)
    RiskIntelligenceEngine().add_trace_step(trace, graph, risk)

    assert "EVALUATE_HIRING_RISK" in [step.action for step in trace.steps]
