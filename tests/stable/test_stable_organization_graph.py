from talentcopilot.organization_intelligence.demo_data import demo_dataframe
from talentcopilot.organization_intelligence.graph import OrganizationGraphBuilder
from talentcopilot.organization_intelligence.graph_engine import OrganizationGraphEngine
from talentcopilot.organization_intelligence.ingestion import dataframe_to_employees


def _diagnostic():
    employees = dataframe_to_employees(demo_dataframe())
    graph = OrganizationGraphBuilder().build(employees)
    return graph, OrganizationGraphEngine().analyze(graph)


def test_graph_contains_employees_and_edges():
    graph, diagnostic = _diagnostic()
    assert len(graph.employees) == 6
    assert len(graph.edges) > 0
    assert diagnostic.edge_count == len(graph.edges)


def test_graph_exposes_people_and_department_metrics():
    _, diagnostic = _diagnostic()
    assert diagnostic.people
    assert diagnostic.departments
    assert diagnostic.department_count == 4
    assert all(0 <= item.connectivity_score <= 100 for item in diagnostic.departments)


def test_graph_generates_explainable_insights():
    _, diagnostic = _diagnostic()
    assert diagnostic.insights
    first = diagnostic.insights[0]
    assert first.evidence
    assert first.recommendations
    assert first.category in {"Collaboration", "Network dependency"}
