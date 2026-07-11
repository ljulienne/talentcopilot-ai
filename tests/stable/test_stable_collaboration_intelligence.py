from talentcopilot.organization_intelligence.collaboration_engine import CollaborationIntelligenceEngine
from talentcopilot.organization_intelligence.demo_data import demo_dataframe
from talentcopilot.organization_intelligence.graph import OrganizationGraphBuilder
from talentcopilot.organization_intelligence.ingestion import dataframe_to_employees


def _diagnostic():
    employees = dataframe_to_employees(demo_dataframe())
    graph = OrganizationGraphBuilder().build(employees)
    return CollaborationIntelligenceEngine().analyze(graph)


def test_collaboration_diagnostic_has_executive_metrics():
    diagnostic = _diagnostic()
    assert diagnostic.employee_count == 6
    assert diagnostic.department_count == 4
    assert 0 <= diagnostic.overall_collaboration_score <= 100
    assert diagnostic.overall_health in {"Healthy", "Watch", "At risk"}


def test_collaboration_detects_department_pairs_and_silo_signals():
    diagnostic = _diagnostic()
    assert len(diagnostic.department_pairs) == 6
    assert diagnostic.departments
    assert all(0 <= item.collaboration_score <= 100 for item in diagnostic.departments)
    assert any(item.inferred_links == 0 for item in diagnostic.department_pairs)


def test_collaboration_detects_brokers_and_generates_insights():
    diagnostic = _diagnostic()
    assert diagnostic.brokers
    assert diagnostic.insights
    first = diagnostic.insights[0]
    assert first.evidence
    assert first.recommendations
    assert first.category in {"Collaboration", "Network dependency"}


def test_collaboration_recommendations_are_deduplicated():
    diagnostic = _diagnostic()
    assert len(diagnostic.recommendations) == len(set(diagnostic.recommendations))
