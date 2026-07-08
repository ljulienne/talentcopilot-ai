from talentcopilot.decision_core.evidence_graph_builder import EvidenceGraphBuilder


def test_evidence_graph_builder_creates_nodes_edges():
    candidate = {
        "name": "Alice Martin",
        "skills": ["Project Management", "Stakeholder Management"],
        "years_experience": 8,
        "achievements": ["Improved adoption by 35%"],
    }

    graph = EvidenceGraphBuilder().build_from_candidate_dict(candidate, "Transformation Lead")

    assert graph.candidate_name == "Alice Martin"
    assert graph.nodes
    assert graph.edges
    assert graph.sources
    assert graph.evidence_coverage() == 100


def test_evidence_graph_find_nodes_by_type():
    graph = EvidenceGraphBuilder().build_from_candidate_dict(
        {"name": "Alice Martin", "skills": ["HRIS"]},
        "HRIS Lead",
    )

    skills = graph.find_nodes_by_type("skill")

    assert len(skills) == 1
    assert skills[0].label == "HRIS"
